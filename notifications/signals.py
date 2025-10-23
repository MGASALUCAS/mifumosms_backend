"""
Signal handlers for automatic notification creation.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from accounts.models import User
from billing.models import SMSBalance
from .services import SMSCreditNotificationService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SMSBalance)
def monitor_sms_credit_changes(sender, instance, created, **kwargs):
    """
    Monitor SMS credit changes and send notifications when credits are low.
    
    This signal is triggered whenever SMSBalance is saved (created or updated).
    """
    try:
        # Get the user associated with this balance
        user = instance.tenant.users.first()  # Assuming tenant has users
        if not user:
            logger.warning(f"No user found for tenant {instance.tenant.id}")
            return
        
        # Only check if credits have actually changed
        if not created and hasattr(instance, '_previous_credits'):
            previous_credits = instance._previous_credits
            current_credits = instance.credits
            
            # Only send notification if credits decreased
            if current_credits < previous_credits:
                sms_credit_service = SMSCreditNotificationService()
                sms_credit_service.check_and_notify_low_credit(
                    user=user,
                    current_credits=current_credits,
                    total_credits=instance.total_credits or current_credits * 4
                )
        
        # Store current credits for next comparison
        instance._previous_credits = instance.credits
        
    except Exception as e:
        logger.error(f"Failed to monitor SMS credit changes: {str(e)}")


@receiver(pre_save, sender=SMSBalance)
def store_previous_credits(sender, instance, **kwargs):
    """
    Store previous credits before saving to detect changes.
    """
    try:
        if instance.pk:
            # Get the previous instance from database
            previous_instance = SMSBalance.objects.get(pk=instance.pk)
            instance._previous_credits = previous_instance.credits
        else:
            # New instance, no previous credits
            instance._previous_credits = instance.credits
    except SMSBalance.DoesNotExist:
        # Instance doesn't exist yet, treat as new
        instance._previous_credits = instance.credits
    except Exception as e:
        logger.error(f"Failed to store previous credits: {str(e)}")
        instance._previous_credits = instance.credits


@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    """
    Create notification settings for new users.
    """
    try:
        if created:
            from .models import NotificationSettings
            NotificationSettings.objects.get_or_create(user=instance)
            logger.info(f"Created notification settings for user {instance.email}")
    except Exception as e:
        logger.error(f"Failed to create notification settings for user {instance.email}: {str(e)}")
