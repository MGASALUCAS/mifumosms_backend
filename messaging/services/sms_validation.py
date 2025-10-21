"""
SMS validation service for credit and sender ID checks.
"""
import logging
from django.db import transaction
from django.utils import timezone
from billing.models import SMSBalance, UsageRecord

logger = logging.getLogger(__name__)


class SMSValidationError(Exception):
    """Exception raised when SMS validation fails."""
    pass


class SMSValidationService:
    """
    Service for validating SMS sending permissions and managing credits.
    """
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.sms_balance = None
        self._load_balance()
    
    def _load_balance(self):
        """Load or create SMS balance for tenant."""
        try:
            self.sms_balance, created = SMSBalance.objects.get_or_create(
                tenant=self.tenant,
                defaults={'credits': 0}
            )
        except Exception as e:
            logger.error(f"Failed to load SMS balance for tenant {self.tenant.id}: {e}")
            raise SMSValidationError("Failed to load SMS balance")
    
    def calculate_sms_segments(self, message):
        """
        Calculate the number of SMS segments required for a message.
        Since we only allow plain text (ASCII), all messages use 160 characters per segment.
        
        Args:
            message: The SMS message content
            
        Returns:
            int: Number of SMS segments required
        """
        if not message:
            return 0
        
        # Plain text only: 160 characters per segment
        return (len(message) + 159) // 160
    
    def validate_message_length(self, message):
        """
        Validate that the message doesn't exceed 200 SMS segments.
        
        Args:
            message: The SMS message content
            
        Returns:
            dict: Validation result with status and details
            
        Raises:
            SMSValidationError: If message exceeds segment limit
        """
        try:
            segments = self.calculate_sms_segments(message)
            
            if segments > 200:
                raise SMSValidationError(
                    f"Message too long. Your message requires {segments} SMS segments, "
                    f"but the maximum allowed is 200 segments. Please reduce your message length."
                )
            
            return {
                'valid': True,
                'segments': segments,
                'message_length': len(message),
                'max_segments': 200
            }
            
        except SMSValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating message length: {e}")
            raise SMSValidationError("Failed to validate message length")
    
    def validate_sender_id(self, sender_id):
        """
        Validate that the sender ID is active and registered.
        
        Args:
            sender_id: The sender ID to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            SMSValidationError: If validation fails
        """
        from messaging.models_sms import SMSSenderID
        
        try:
            sms_sender = SMSSenderID.objects.filter(
                tenant=self.tenant,
                sender_id=sender_id,
                status='active'
            ).first()
            
            if not sms_sender:
                raise SMSValidationError(
                    f"Sender ID '{sender_id}' is not registered or not active. "
                    "Please register and activate your sender ID before sending SMS."
                )
            
            return True
            
        except SMSValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating sender ID {sender_id}: {e}")
            raise SMSValidationError("Failed to validate sender ID")
    
    def validate_credits(self, required_credits=1):
        """
        Validate that the tenant has sufficient SMS credits.
        
        Args:
            required_credits: Number of credits required (default: 1)
            
        Returns:
            bool: True if sufficient credits available
            
        Raises:
            SMSValidationError: If insufficient credits
        """
        try:
            if not self.sms_balance:
                raise SMSValidationError("SMS balance not available")
            
            if self.sms_balance.credits < required_credits:
                raise SMSValidationError(
                    f"Insufficient SMS credits. Required: {required_credits}, "
                    f"Available: {self.sms_balance.credits}. Please purchase more credits to send SMS."
                )
            
            return True
            
        except SMSValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating credits: {e}")
            raise SMSValidationError("Failed to validate SMS credits")
    
    def validate_sms_sending(self, sender_id, required_credits=1, message=None):
        """
        Complete validation for SMS sending.
        
        Args:
            sender_id: The sender ID to validate
            required_credits: Number of credits required
            message: Optional message content to validate length
            
        Returns:
            dict: Validation result with status and details
            
        Raises:
            SMSValidationError: If validation fails
        """
        try:
            # Validate message length first (if provided)
            if message:
                length_result = self.validate_message_length(message)
                if not length_result['valid']:
                    return {
                        'valid': False,
                        'error': f"Message too long. Your message requires {length_result.get('segments', 0)} SMS segments, but the maximum allowed is 200 segments. Please reduce your message length.",
                        'error_type': 'message_too_long',
                        'reason': 'message_too_long'
                    }
            
            # Validate sender ID
            self.validate_sender_id(sender_id)
            
            # Validate credits
            self.validate_credits(required_credits)
            
            return {
                'valid': True,
                'sender_id': sender_id,
                'available_credits': self.sms_balance.credits,
                'required_credits': required_credits,
                'remaining_credits': self.sms_balance.credits - required_credits,
                'message_segments': length_result.get('segments', 1) if message else 1
            }
            
        except SMSValidationError as e:
            return {
                'valid': False,
                'error': str(e),
                'error_type': 'validation_error'
            }
        except Exception as e:
            logger.error(f"Unexpected error in SMS validation: {e}")
            return {
                'valid': False,
                'error': 'An unexpected error occurred during validation',
                'error_type': 'system_error'
            }
    
    @transaction.atomic
    def deduct_credits(self, amount, sender_id, message_id=None, description=None):
        """
        Deduct SMS credits from tenant balance.
        
        Args:
            amount: Number of credits to deduct
            sender_id: Sender ID used for the SMS
            message_id: Optional message ID for tracking
            description: Optional description for usage record
            
        Returns:
            bool: True if deduction successful
            
        Raises:
            SMSValidationError: If deduction fails
        """
        try:
            if not self.sms_balance:
                raise SMSValidationError("SMS balance not available")
            
            if self.sms_balance.credits < amount:
                raise SMSValidationError(
                    f"Insufficient credits for deduction. Required: {amount}, "
                    f"Available: {self.sms_balance.credits}"
                )
            
            # Deduct credits
            success = self.sms_balance.use_credits(amount)
            
            if not success:
                raise SMSValidationError("Failed to deduct credits")
            
            # Create usage record
            # Get the first active user from the tenant
            active_membership = self.tenant.memberships.filter(status='active').first()
            if active_membership:
                user = active_membership.user
            else:
                # Fallback: get any user from the tenant
                user = self.tenant.memberships.first().user if self.tenant.memberships.exists() else None
            
            if user:
                UsageRecord.objects.create(
                    tenant=self.tenant,
                    user=user,
                    credits_used=amount,
                    cost=0.0  # Cost is handled in purchase
                )
            
            logger.info(
                f"Deducted {amount} SMS credits for tenant {self.tenant.id}, "
                f"sender {sender_id}. Remaining: {self.sms_balance.credits}"
            )
            
            return True
            
        except SMSValidationError:
            raise
        except Exception as e:
            logger.error(f"Error deducting credits: {e}")
            raise SMSValidationError("Failed to deduct SMS credits")
    
    def get_balance_info(self):
        """
        Get current SMS balance information.
        
        Returns:
            dict: Balance information
        """
        try:
            if not self.sms_balance:
                return {
                    'credits': 0,
                    'total_purchased': 0,
                    'total_used': 0,
                    'can_send_sms': False
                }
            
            return {
                'credits': self.sms_balance.credits,
                'total_purchased': self.sms_balance.total_purchased,
                'total_used': self.sms_balance.total_used,
                'can_send_sms': self.sms_balance.credits > 0,
                'last_updated': self.sms_balance.last_updated
            }
            
        except Exception as e:
            logger.error(f"Error getting balance info: {e}")
            return {
                'credits': 0,
                'total_purchased': 0,
                'total_used': 0,
                'can_send_sms': False,
                'error': str(e)
            }
    
    def get_active_sender_ids(self):
        """
        Get list of active sender IDs for the tenant.
        
        Returns:
            list: List of active sender IDs
        """
        try:
            from messaging.models_sms import SMSSenderID
            
            sender_ids = SMSSenderID.objects.filter(
                tenant=self.tenant,
                status='active'
            ).values_list('sender_id', flat=True)
            
            return list(sender_ids)
            
        except Exception as e:
            logger.error(f"Error getting active sender IDs: {e}")
            return []
    
    def can_send_sms(self, sender_id=None):
        """
        Check if tenant can send SMS.
        
        Args:
            sender_id: Optional specific sender ID to check
            
        Returns:
            dict: Can send status and details
        """
        try:
            # Check if has credits
            if not self.sms_balance or self.sms_balance.credits <= 0:
                return {
                    'can_send': False,
                    'reason': 'no_credits',
                    'message': 'No SMS credits available. Please purchase credits to send SMS.',
                    'available_credits': 0
                }
            
            # Check sender ID if provided
            if sender_id:
                try:
                    self.validate_sender_id(sender_id)
                except SMSValidationError as e:
                    return {
                        'can_send': False,
                        'reason': 'invalid_sender_id',
                        'message': str(e),
                        'available_credits': self.sms_balance.credits
                    }
            
            return {
                'can_send': True,
                'reason': 'valid',
                'message': 'SMS sending is allowed',
                'available_credits': self.sms_balance.credits
            }
            
        except Exception as e:
            logger.error(f"Error checking SMS sending capability: {e}")
            return {
                'can_send': False,
                'reason': 'system_error',
                'message': 'System error occurred while checking SMS capability',
                'available_credits': 0
            }
