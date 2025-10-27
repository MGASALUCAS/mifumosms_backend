"""
Notification service for sending push messages and SMS notifications.
"""
import logging
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending various types of notifications to users.
    """
    
    def __init__(self, tenant=None):
        self.tenant = tenant
    
    def send_payment_success_notification(self, user, purchase, payment_transaction):
        """
        Send notification when payment is completed successfully.
        
        Args:
            user: User who made the payment
            purchase: Purchase object
            payment_transaction: PaymentTransaction object
        """
        try:
            # Send SMS notification if enabled and user has phone
            if self._should_send_sms_notification(user):
                self._send_sms_payment_notification(user, purchase, payment_transaction)
            
            # Send email notification if enabled
            if self._should_send_email_notification(user):
                self._send_email_payment_notification(user, purchase, payment_transaction)
            
            # Send push notification if FCM is configured
            if self._should_send_push_notification(user):
                self._send_push_payment_notification(user, purchase, payment_transaction)
            
            logger.info(f"Payment success notifications sent for user {user.email}, purchase {purchase.id}")
            
        except Exception as e:
            logger.error(f"Failed to send payment success notification: {str(e)}")
    
    def send_payment_failed_notification(self, user, purchase, payment_transaction, error_message=None):
        """
        Send notification when payment fails.
        
        Args:
            user: User who made the payment
            purchase: Purchase object
            payment_transaction: PaymentTransaction object
            error_message: Error message to include
        """
        try:
            # Send SMS notification if enabled and user has phone
            if self._should_send_sms_notification(user):
                self._send_sms_payment_failed_notification(user, purchase, payment_transaction, error_message)
            
            # Send email notification if enabled
            if self._should_send_email_notification(user):
                self._send_email_payment_failed_notification(user, purchase, payment_transaction, error_message)
            
            logger.info(f"Payment failed notifications sent for user {user.email}, purchase {purchase.id}")
            
        except Exception as e:
            logger.error(f"Failed to send payment failed notification: {str(e)}")
    
    def _should_send_sms_notification(self, user) -> bool:
        """Check if SMS notification should be sent."""
        return (
            getattr(settings, 'SMS_NOTIFICATION_ENABLED', False) and
            hasattr(user, 'profile') and
            getattr(user.profile, 'sms_notifications', False) and
            hasattr(user, 'phone') and user.phone
        )
    
    def _should_send_email_notification(self, user) -> bool:
        """Check if email notification should be sent."""
        return (
            getattr(settings, 'EMAIL_NOTIFICATION_ENABLED', False) and
            hasattr(user, 'profile') and
            getattr(user.profile, 'email_notifications', False)
        )
    
    def _should_send_push_notification(self, user) -> bool:
        """Check if push notification should be sent."""
        return (
            getattr(settings, 'FCM_SERVER_KEY', '') and
            getattr(settings, 'FCM_SENDER_ID', '')
        )
    
    def _send_sms_payment_notification(self, user, purchase, payment_transaction):
        """Send SMS notification for successful payment."""
        try:
            from messaging.services.sms_service import SMSService
            
            # Get notification sender ID
            sender_id = getattr(settings, 'SMS_NOTIFICATION_SENDER_ID', 'NOTIFY')
            
            # Create message
            message = (
                f"Payment Successful! {purchase.credits} SMS credits added to your account. "
                f"Order: {payment_transaction.order_id}. "
                f"New balance: {self.tenant.sms_balance.credits if self.tenant else 'N/A'} credits. "
                f"Thank you for using Mifumo WMS!"
            )
            
            # Send SMS
            sms_service = SMSService(str(self.tenant.id) if self.tenant else None)
            result = sms_service.send_sms(
                to=user.phone,
                message=message,
                sender_id=sender_id
            )
            
            if result.get('success'):
                logger.info(f"SMS payment notification sent to {user.phone}")
            else:
                logger.error(f"Failed to send SMS payment notification: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending SMS payment notification: {str(e)}")
    
    def _send_sms_payment_failed_notification(self, user, purchase, payment_transaction, error_message):
        """Send SMS notification for failed payment."""
        try:
            from messaging.services.sms_service import SMSService
            
            # Get notification sender ID
            sender_id = getattr(settings, 'SMS_NOTIFICATION_SENDER_ID', 'NOTIFY')
            
            # Create message
            message = (
                f"Payment Failed! Your payment for {purchase.credits} SMS credits could not be processed. "
                f"Order: {payment_transaction.order_id}. "
                f"Please try again or contact support. Thank you for using Mifumo WMS!"
            )
            
            # Send SMS
            sms_service = SMSService(str(self.tenant.id) if self.tenant else None)
            result = sms_service.send_sms(
                to=user.phone,
                message=message,
                sender_id=sender_id
            )
            
            if result.get('success'):
                logger.info(f"SMS payment failed notification sent to {user.phone}")
            else:
                logger.error(f"Failed to send SMS payment failed notification: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending SMS payment failed notification: {str(e)}")
    
    def _send_email_payment_notification(self, user, purchase, payment_transaction):
        """Send email notification for successful payment."""
        try:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            
            subject = f"Payment Successful - {purchase.credits} SMS Credits Added"
            
            # Create email content
            context = {
                'user': user,
                'purchase': purchase,
                'payment_transaction': payment_transaction,
                'tenant': self.tenant,
                'new_balance': self.tenant.sms_balance.credits if self.tenant else 0
            }
            
            # Simple text message for now
            message = (
                f"Dear {user.get_full_name() or user.email},\n\n"
                f"Your payment has been processed successfully!\n\n"
                f"Order Details:\n"
                f"- Order ID: {payment_transaction.order_id}\n"
                f"- Credits Added: {purchase.credits}\n"
                f"- Amount Paid: {payment_transaction.amount} {payment_transaction.currency}\n"
                f"- New Balance: {context['new_balance']} credits\n\n"
                f"Thank you for using Mifumo WMS!\n\n"
                f"Best regards,\n"
                f"Mifumo WMS Team"
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'EMAIL_NOTIFICATION_FROM', 'noreply@mifumo.com'),
                recipient_list=[user.email],
                fail_silently=False
            )
            
            logger.info(f"Email payment notification sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Error sending email payment notification: {str(e)}")
    
    def _send_email_payment_failed_notification(self, user, purchase, payment_transaction, error_message):
        """Send email notification for failed payment."""
        try:
            from django.core.mail import send_mail
            
            subject = f"Payment Failed - {purchase.credits} SMS Credits"
            
            message = (
                f"Dear {user.get_full_name() or user.email},\n\n"
                f"Unfortunately, your payment could not be processed.\n\n"
                f"Order Details:\n"
                f"- Order ID: {payment_transaction.order_id}\n"
                f"- Credits Requested: {purchase.credits}\n"
                f"- Amount: {payment_transaction.amount} {payment_transaction.currency}\n"
                f"- Error: {error_message or 'Unknown error'}\n\n"
                f"Please try again or contact our support team for assistance.\n\n"
                f"Best regards,\n"
                f"Mifumo WMS Team"
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'EMAIL_NOTIFICATION_FROM', 'noreply@mifumo.com'),
                recipient_list=[user.email],
                fail_silently=False
            )
            
            logger.info(f"Email payment failed notification sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Error sending email payment failed notification: {str(e)}")
    
    def _send_push_payment_notification(self, user, purchase, payment_transaction):
        """Send push notification for successful payment."""
        try:
            # TODO: Implement FCM push notification
            # This would require FCM setup and user device tokens
            logger.info(f"Push notification for payment success would be sent to user {user.email}")
            
        except Exception as e:
            logger.error(f"Error sending push payment notification: {str(e)}")


# Global instance
notification_service = NotificationService()













