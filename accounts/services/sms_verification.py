"""
SMS Verification Service for user authentication and account verification.
"""
import random
import string
import base64
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from messaging.services.sms_service import SMSService
from messaging.services.beem_sms import BeemSMSService
from messaging.models import SMSProvider, SMSSenderID
from tenants.models import Tenant


class SMSVerificationService:
    """
    Service for handling SMS verification codes for user authentication.
    """
    
    def __init__(self, tenant_id=None):
        self.tenant_id = tenant_id
        self.sms_service = None
        self.sender_id = "Taarifa-SMS"  # Use approved sender ID
        
    def _get_sms_service(self):
        """Get SMS service instance."""
        if not self.sms_service:
            if self.tenant_id:
                self.sms_service = SMSService(str(self.tenant_id))
            else:
                # Use default tenant for system-wide operations
                default_tenant = Tenant.objects.first()
                if default_tenant:
                    self.sms_service = SMSService(str(default_tenant.id))
        return self.sms_service
    
    def _get_sender_id(self):
        """Get or create Taarifa-SMS sender ID."""
        if not self.tenant_id:
            return None
            
        tenant = Tenant.objects.get(id=self.tenant_id)
        
        # Try to get existing Taarifa-SMS sender ID
        sender_id = SMSSenderID.objects.filter(
            tenant=tenant,
            sender_id=self.sender_id,
            status='active'
        ).first()
        
        if not sender_id:
            # Create default sender ID if it doesn't exist
            from messaging.services.sms_validation import get_or_create_default_sender
            provider = SMSProvider.objects.filter(
                tenant=tenant,
                is_active=True
            ).first()
            
            if provider:
                sender_id = get_or_create_default_sender(tenant, provider)
        
        return sender_id
    
    def generate_verification_code(self, length=6):
        """Generate a random verification code."""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_verification_sms(self, phone_number, code, message_type="verification"):
        """
        Send verification SMS to phone number using the working messaging system approach.
        
        Args:
            phone_number (str): Phone number in E.164 format
            code (str): Verification code to send
            message_type (str): Type of verification (verification, password_reset, etc.)
        
        Returns:
            dict: Result with success status and message
        """
        try:
            # Format phone number for Beem API (international format without +)
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            elif phone_number.startswith('0') and len(phone_number) == 10:
                # Convert local format (0689726060) to international format (255689726060)
                phone_number = '255' + phone_number[1:]
            elif len(phone_number) == 9 and phone_number.startswith('6'):
                # Convert local format without leading 0 (689726060) to international format (255689726060)
                phone_number = '255' + phone_number
            
            # Create appropriate message based on type
            if message_type == "verification":
                message = f"Your Mifumo WMS verification code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."
            elif message_type == "password_reset":
                message = f"Your Mifumo WMS password reset code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."
            elif message_type == "account_confirmation":
                message = f"Your Mifumo WMS account confirmation code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."
            else:
                message = f"Your Mifumo WMS verification code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."
            
            # Use the working messaging system approach (SMSService)
            from messaging.services.sms_service import SMSService
            
            sms_service = SMSService(self.tenant_id)
            
            result = sms_service.send_sms(
                to=phone_number,
                message=message,
                sender_id=self.sender_id,
                recipient_id=str(int(timezone.now().timestamp()))
            )
            
            if result.get('success'):
                return {
                    'success': True,
                    'message': 'Verification code sent successfully',
                    'phone_number': f"+{phone_number}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to send SMS'),
                    'details': result
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send verification SMS: {str(e)}'
            }
    
    def _send_sms_direct(self, phone_number, message, sender_id):
        """
        Send SMS directly using Beem API with the same authentication as messaging system.
        
        Args:
            phone_number (str): Phone number without + prefix
            message (str): SMS message content
            sender_id (str): Sender ID to use
        
        Returns:
            dict: Result with success status and response
        """
        try:
            # Get API credentials
            api_key = getattr(settings, 'BEEM_API_KEY', None)
            secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
            
            if not api_key or not secret_key:
                return {
                    'success': False,
                    'error': 'Beem API credentials not configured'
                }
            
            # Create Basic Auth header (same as working messaging system)
            credentials = f"{api_key}:{secret_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            auth_header = f"Basic {encoded_credentials}"
            
            # Prepare request data (same format as working messaging system)
            data = {
                "source_addr": sender_id,
                "message": message,
                "encoding": 0,  # GSM7 encoding
                "recipients": [{
                    "recipient_id": f"verification_{int(timezone.now().timestamp())}",
                    "dest_addr": phone_number
                }]
            }
            
            # Make API request (same as working messaging system)
            response = requests.post(
                getattr(settings, 'BEEM_SEND_URL', 'https://apisms.beem.africa/v1/send'),
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('successful'):
                return {
                    'success': True,
                    'request_id': response_data.get('request_id'),
                    'message_id': response_data.get('request_id'),
                    'valid_count': response_data.get('valid', 0),
                    'invalid_count': response_data.get('invalid', 0),
                    'duplicates_count': response_data.get('duplicates', 0),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Unknown error'),
                    'error_code': response_data.get('code'),
                    'response': response_data
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"API request failed: {str(e)}",
                'error_code': 'NETWORK_ERROR'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Service error: {str(e)}",
                'error_code': 'SERVICE_ERROR'
            }
    
    def is_phone_locked(self, user):
        """Check if phone verification is locked for user."""
        if user.phone_verification_locked_until:
            if timezone.now() < user.phone_verification_locked_until:
                return True
            else:
                # Unlock if time has passed
                user.phone_verification_locked_until = None
                user.phone_verification_attempts = 0
                user.save(update_fields=['phone_verification_locked_until', 'phone_verification_attempts'])
        return False
    
    def lock_phone_verification(self, user, minutes=30):
        """Lock phone verification for user."""
        user.phone_verification_locked_until = timezone.now() + timedelta(minutes=minutes)
        user.save(update_fields=['phone_verification_locked_until'])
    
    def increment_verification_attempts(self, user):
        """Increment verification attempts and lock if necessary."""
        user.phone_verification_attempts += 1
        
        # Lock after 5 attempts
        if user.phone_verification_attempts >= 5:
            self.lock_phone_verification(user, minutes=30)
        
        user.save(update_fields=['phone_verification_attempts'])
    
    def reset_verification_attempts(self, user):
        """Reset verification attempts."""
        user.phone_verification_attempts = 0
        user.phone_verification_locked_until = None
        user.save(update_fields=['phone_verification_attempts', 'phone_verification_locked_until'])
    
    def verify_code(self, user, code, clear_code=True):
        """
        Verify the provided code for user.
        
        Args:
            user: User instance
            code (str): Verification code to check
            clear_code (bool): Whether to clear the code after verification (default: True)
        
        Returns:
            dict: Result with success status and message
        """
        try:
            # Bypass SMS verification for superadmin users
            if user.is_superuser:
                # Mark phone as verified automatically for superadmin users
                user.phone_verified = True
                user.save(update_fields=['phone_verified'])
                return {
                    'success': True,
                    'message': 'Phone number automatically verified for superadmin user',
                    'bypassed': True
                }
            
            # Check if phone is locked
            if self.is_phone_locked(user):
                return {
                    'success': False,
                    'error': 'Phone verification is temporarily locked. Please try again later.',
                    'locked_until': user.phone_verification_locked_until
                }
            
            # Check if code exists
            if not user.phone_verification_code:
                return {
                    'success': False,
                    'error': 'No verification code found. Please request a new code.'
                }
            
            # Check if code has expired (10 minutes)
            if user.phone_verification_sent_at:
                if timezone.now() > user.phone_verification_sent_at + timedelta(minutes=10):
                    return {
                        'success': False,
                        'error': 'Verification code has expired. Please request a new code.'
                    }
            
            # Check if code matches
            if user.phone_verification_code == code:
                # Success - mark phone as verified and reset attempts
                user.phone_verified = True
                
                # Only clear code if requested (for password reset, keep code until password is reset)
                if clear_code:
                    user.phone_verification_code = ''
                    user.phone_verification_sent_at = None
                
                self.reset_verification_attempts(user)
                user.save()
                
                return {
                    'success': True,
                    'message': 'Phone number verified successfully'
                }
            else:
                # Wrong code - increment attempts
                self.increment_verification_attempts(user)
                return {
                    'success': False,
                    'error': 'Invalid verification code. Please try again.',
                    'attempts_remaining': max(0, 5 - user.phone_verification_attempts)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def send_verification_code(self, user, message_type="verification"):
        """
        Send verification code to user's phone.
        
        Args:
            user: User instance
            message_type (str): Type of verification message
        
        Returns:
            dict: Result with success status and message
        """
        try:
            # Check if phone number exists
            if not user.phone_number:
                return {
                    'success': False,
                    'error': 'Phone number not found. Please add a phone number to your account.'
                }
            
            # Bypass SMS verification for superadmin users
            if user.is_superuser:
                # Mark phone as verified automatically for superadmin users
                user.phone_verified = True
                user.save(update_fields=['phone_verified'])
                return {
                    'success': True,
                    'message': 'Phone number automatically verified for superadmin user',
                    'bypassed': True,
                    'phone_number': user.phone_number
                }
            
            # Check if phone is locked
            if self.is_phone_locked(user):
                return {
                    'success': False,
                    'error': 'Phone verification is temporarily locked. Please try again later.',
                    'locked_until': user.phone_verification_locked_until
                }
            
            # Generate new code
            code = self.generate_verification_code()
            
            # Update user with new code
            user.phone_verification_code = code
            user.phone_verification_sent_at = timezone.now()
            user.save(update_fields=['phone_verification_code', 'phone_verification_sent_at'])
            
            # Send SMS
            result = self.send_verification_sms(
                user.phone_number, 
                code, 
                message_type
            )
            
            if result['success']:
                return {
                    'success': True,
                    'message': 'Verification code sent successfully',
                    'phone_number': user.phone_number
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to send verification code: {str(e)}'
            }
