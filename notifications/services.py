"""
Notification service for managing notifications.
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from typing import List, Dict, Optional, Any
from .models import (
    Notification, NotificationTemplate, NotificationSettings,
    NotificationType, NotificationPriority, NotificationStatus
)
from messaging.services.sms_service import SMSService

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for managing notifications.
    """
    
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
    
    def create_notification(
        self,
        user: User,
        title: str,
        message: str,
        notification_type: str = NotificationType.SYSTEM,
        priority: str = NotificationPriority.MEDIUM,
        data: Dict = None,
        action_url: str = None,
        action_text: str = None,
        expires_at: datetime = None,
        is_system: bool = False,
        is_auto_generated: bool = False
    ) -> Notification:
        """
        Create a new notification for a user.
        
        Args:
            user: User to send notification to
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            data: Additional data
            action_url: URL to navigate when clicked
            action_text: Text for action button
            expires_at: When notification expires
            is_system: Whether it's a system notification
            is_auto_generated: Whether it's auto-generated
        
        Returns:
            Created notification instance
        """
        try:
            with transaction.atomic():
                # Get user's tenant, create a default one if none exists
                try:
                    tenant = user.get_tenant()
                except:
                    # If user has no tenant, get the first available tenant or create a default one
                    from tenants.models import Tenant
                    tenant = Tenant.objects.first()
                    if not tenant:
                        tenant = Tenant.objects.create(
                            name="Default System Tenant",
                            domain="system.local"
                        )
                
                notification = Notification.objects.create(
                    user=user,
                    tenant=tenant,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    data=data or {},
                    action_url=action_url,
                    action_text=action_text,
                    expires_at=expires_at,
                    is_system=is_system,
                    is_auto_generated=is_auto_generated
                )
                
                # Send additional notifications if enabled
                self._send_additional_notifications(notification)
                
                logger.info(f"Created notification for user {user.email}: {title}")
                return notification
                
        except Exception as e:
            logger.error(f"Failed to create notification for user {user.email}: {str(e)}")
            raise
    
    def create_notification_from_template(
        self,
        user: User,
        template_name: str,
        context: Dict = None,
        **kwargs
    ) -> Notification:
        """
        Create notification from template.
        
        Args:
            user: User to send notification to
            template_name: Name of the template
            context: Variables for template rendering
            **kwargs: Additional notification parameters
        
        Returns:
            Created notification instance
        """
        try:
            template = NotificationTemplate.objects.get(
                name=template_name,
                is_active=True
            )
            
            rendered = template.render(context or {})
            
            return self.create_notification(
                user=user,
                title=rendered['title'],
                message=rendered['message'],
                notification_type=rendered['notification_type'],
                priority=rendered['priority'],
                **kwargs
            )
            
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Notification template '{template_name}' not found")
            raise
        except Exception as e:
            logger.error(f"Failed to create notification from template: {str(e)}")
            raise
    
    def create_bulk_notifications(
        self,
        users: List[User],
        title: str,
        message: str,
        notification_type: str = NotificationType.SYSTEM,
        priority: str = NotificationPriority.MEDIUM,
        **kwargs
    ) -> List[Notification]:
        """
        Create notifications for multiple users.
        
        Args:
            users: List of users to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            **kwargs: Additional notification parameters
        
        Returns:
            List of created notifications
        """
        notifications = []
        
        try:
            with transaction.atomic():
                for user in users:
                    notification = self.create_notification(
                        user=user,
                        title=title,
                        message=message,
                        notification_type=notification_type,
                        priority=priority,
                        **kwargs
                    )
                    notifications.append(notification)
                
                logger.info(f"Created {len(notifications)} bulk notifications")
                return notifications
                
        except Exception as e:
            logger.error(f"Failed to create bulk notifications: {str(e)}")
            raise
    
    def get_user_notifications(
        self,
        user: User,
        status: str = None,
        notification_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user: User to get notifications for
            status: Filter by status
            notification_type: Filter by type
            limit: Number of notifications to return
            offset: Number of notifications to skip
        
        Returns:
            List of notifications
        """
        queryset = Notification.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter out expired notifications
        queryset = queryset.filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        )
        
        return queryset[offset:offset + limit]
    
    def get_unread_count(self, user: User) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user: User to get count for
        
        Returns:
            Number of unread notifications
        """
        return Notification.objects.filter(
            user=user,
            status=NotificationStatus.UNREAD
        ).count()
    
    def mark_as_read(self, notification_id: str, user: User) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of notification to mark as read
            user: User who owns the notification
        
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {user.email}")
            return False
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return False
    
    def mark_all_as_read(self, user: User) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user: User to mark notifications as read for
        
        Returns:
            Number of notifications marked as read
        """
        try:
            count = Notification.objects.filter(
                user=user,
                status=NotificationStatus.UNREAD
            ).update(
                status=NotificationStatus.READ,
                read_at=timezone.now()
            )
            
            logger.info(f"Marked {count} notifications as read for user {user.email}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to mark all notifications as read: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: str, user: User) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: ID of notification to delete
            user: User who owns the notification
        
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user
            )
            notification.delete()
            return True
        except Notification.DoesNotExist:
            logger.warning(f"Notification {notification_id} not found for user {user.email}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete notification: {str(e)}")
            return False
    
    def cleanup_expired_notifications(self) -> int:
        """
        Clean up expired notifications.
        
        Returns:
            Number of notifications deleted
        """
        try:
            count = Notification.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()[0]
            
            logger.info(f"Cleaned up {count} expired notifications")
            return count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired notifications: {str(e)}")
            return 0
    
    def _send_additional_notifications(self, notification: Notification):
        """
        Send additional notifications (email, SMS) based on user settings.
        
        Args:
            notification: Notification instance
        """
        try:
            settings_obj, created = NotificationSettings.objects.get_or_create(
                user=notification.user
            )
            
            # Send email notification if enabled
            if settings_obj.should_notify_email(notification.notification_type):
                self._send_email_notification(notification)
            
            # Send SMS notification if enabled
            if settings_obj.should_notify_sms(notification.notification_type, notification.priority):
                self._send_sms_notification(notification)
                
        except Exception as e:
            logger.error(f"Failed to send additional notifications: {str(e)}")
    
    def _send_email_notification(self, notification: Notification):
        """
        Send email notification.
        
        Args:
            notification: Notification instance
        """
        try:
            subject = f"[Mifumo WMS] {notification.title}"
            message = f"""
            {notification.message}
            
            Priority: {notification.get_priority_display()}
            Type: {notification.get_notification_type_display()}
            
            {f"Action: {notification.action_text}" if notification.action_text else ""}
            {f"URL: {notification.action_url}" if notification.action_url else ""}
            
            ---
            This is an automated notification from Mifumo WMS.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [notification.user.email],
                fail_silently=False,
            )
            
            logger.info(f"Sent email notification to {notification.user.email}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
    
    def _send_sms_notification(self, notification: Notification):
        """
        Send SMS notification.
        
        Args:
            notification: Notification instance
        """
        try:
            if not notification.user.phone_number:
                logger.warning(f"No phone number for user {notification.user.email}")
                return
            
            # Create SMS message
            message = f"Mifumo WMS: {notification.title}\n{notification.message}"
            
            if notification.action_url:
                message += f"\n\nView: {notification.action_url}"
            
            # Send SMS
            sms_service = SMSService(self.tenant_id)
            result = sms_service.send_sms(
                to=notification.user.phone_number,
                message=message,
                sender_id="Mifumo-WMS"
            )
            
            if result.get('success'):
                logger.info(f"Sent SMS notification to {notification.user.phone_number}")
            else:
                logger.error(f"Failed to send SMS notification: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")


class SMSCreditNotificationService:
    """
    Service for SMS credit-related notifications.
    """
    
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
        self.notification_service = NotificationService(tenant_id)
    
    def check_and_notify_low_credit(self, user: User, current_credits: int, total_credits: int = None):
        """
        Check SMS credit level and send notification if low.
        
        Args:
            user: User to check credits for
            current_credits: Current SMS credits
            total_credits: Total credits purchased (optional)
        """
        try:
            settings_obj, created = NotificationSettings.objects.get_or_create(
                user=user
            )
            
            if not total_credits:
                total_credits = current_credits * 4  # Assume 25% remaining means 75% used
            
            percentage = (current_credits / total_credits) * 100 if total_credits > 0 else 0
            
            # Check if notification should be sent
            if percentage <= settings_obj.credit_critical_threshold:
                self._send_critical_credit_notification(user, current_credits, percentage)
            elif percentage <= settings_obj.credit_warning_threshold:
                self._send_low_credit_notification(user, current_credits, percentage)
                
        except Exception as e:
            logger.error(f"Failed to check SMS credit for user {user.email}: {str(e)}")
    
    def _send_low_credit_notification(self, user: User, current_credits: int, percentage: float):
        """
        Send low credit notification.
        
        Args:
            user: User to notify
            current_credits: Current SMS credits
            percentage: Credit percentage remaining
        """
        title = "Low SMS Credit Warning"
        message = f"Your SMS credit is running low. You have {current_credits} credits remaining ({percentage:.1f}% of your total). Consider purchasing more credits to avoid service interruption."
        
        self.notification_service.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.SMS_CREDIT,
            priority=NotificationPriority.MEDIUM,
            data={
                'current_credits': current_credits,
                'percentage': percentage,
                'type': 'low_credit'
            },
            action_url='/billing/sms/purchase/',
            action_text='Buy Credits',
            is_auto_generated=True
        )
    
    def _send_critical_credit_notification(self, user: User, current_credits: int, percentage: float):
        """
        Send critical credit notification.
        
        Args:
            user: User to notify
            current_credits: Current SMS credits
            percentage: Credit percentage remaining
        """
        title = "Critical: SMS Credit Very Low"
        message = f"URGENT: Your SMS credit is critically low! You have only {current_credits} credits remaining ({percentage:.1f}% of your total). Purchase credits immediately to avoid service interruption."
        
        self.notification_service.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.SMS_CREDIT,
            priority=NotificationPriority.URGENT,
            data={
                'current_credits': current_credits,
                'percentage': percentage,
                'type': 'critical_credit'
            },
            action_url='/billing/sms/purchase/',
            action_text='Buy Credits Now',
            is_auto_generated=True
        )
