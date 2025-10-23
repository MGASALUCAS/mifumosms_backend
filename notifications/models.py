"""
Notification models for the Mifumo WMS system.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class NotificationType(models.TextChoices):
    """Notification type choices."""
    SYSTEM = 'system', 'System Notification'
    SMS_CREDIT = 'sms_credit', 'SMS Credit Notification'
    CAMPAIGN = 'campaign', 'Campaign Notification'
    CONTACT = 'contact', 'Contact Notification'
    BILLING = 'billing', 'Billing Notification'
    SECURITY = 'security', 'Security Notification'
    MAINTENANCE = 'maintenance', 'Maintenance Notification'
    ERROR = 'error', 'Error Notification'
    SUCCESS = 'success', 'Success Notification'
    WARNING = 'warning', 'Warning Notification'
    INFO = 'info', 'Information Notification'


class NotificationPriority(models.TextChoices):
    """Notification priority levels."""
    LOW = 'low', 'Low Priority'
    MEDIUM = 'medium', 'Medium Priority'
    HIGH = 'high', 'High Priority'
    URGENT = 'urgent', 'Urgent Priority'


class NotificationStatus(models.TextChoices):
    """Notification status choices."""
    UNREAD = 'unread', 'Unread'
    READ = 'read', 'Read'
    ARCHIVED = 'archived', 'Archived'


class Notification(models.Model):
    """
    Notification model for storing user notifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='notifications')
    
    # Notification content
    title = models.CharField(max_length=200, help_text="Notification title")
    message = models.TextField(help_text="Detailed notification message")
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        help_text="Type of notification"
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.MEDIUM,
        help_text="Notification priority level"
    )
    status = models.CharField(
        max_length=10,
        choices=NotificationStatus.choices,
        default=NotificationStatus.UNREAD,
        help_text="Notification read status"
    )
    
    # Additional data
    data = models.JSONField(default=dict, blank=True, help_text="Additional notification data")
    action_url = models.URLField(blank=True, null=True, help_text="URL to navigate when notification is clicked")
    action_text = models.CharField(max_length=100, blank=True, help_text="Text for action button")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True, help_text="When notification expires")
    
    # System fields
    is_system = models.BooleanField(default=False, help_text="System-generated notification")
    is_auto_generated = models.BooleanField(default=False, help_text="Auto-generated notification")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['tenant', 'notification_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if self.status == NotificationStatus.UNREAD:
            self.status = NotificationStatus.READ
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])
    
    def mark_as_archived(self):
        """Mark notification as archived."""
        self.status = NotificationStatus.ARCHIVED
        self.save(update_fields=['status'])
    
    def is_expired(self):
        """Check if notification has expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_unread(self):
        """Check if notification is unread."""
        return self.status == NotificationStatus.UNREAD
    
    @property
    def time_ago(self):
        """Get human-readable time since creation."""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


class NotificationTemplate(models.Model):
    """
    Template for generating notifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Template name")
    title_template = models.CharField(max_length=200, help_text="Title template with variables")
    message_template = models.TextField(help_text="Message template with variables")
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        help_text="Type of notification this template generates"
    )
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.MEDIUM,
        help_text="Default priority for notifications using this template"
    )
    is_active = models.BooleanField(default=True, help_text="Whether template is active")
    variables = models.JSONField(
        default=list,
        help_text="List of variables used in the template",
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def render(self, context=None):
        """Render template with given context."""
        if not context:
            context = {}
        
        try:
            title = self.title_template.format(**context)
            message = self.message_template.format(**context)
            return {
                'title': title,
                'message': message,
                'notification_type': self.notification_type,
                'priority': self.priority
            }
        except KeyError as e:
            raise ValueError(f"Missing variable in template: {e}")


class NotificationSettings(models.Model):
    """
    User notification preferences and settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Email notifications
    email_notifications = models.BooleanField(default=True, help_text="Enable email notifications")
    email_sms_credit = models.BooleanField(default=True, help_text="Email notifications for SMS credit")
    email_campaigns = models.BooleanField(default=True, help_text="Email notifications for campaigns")
    email_contacts = models.BooleanField(default=True, help_text="Email notifications for contacts")
    email_billing = models.BooleanField(default=True, help_text="Email notifications for billing")
    email_security = models.BooleanField(default=True, help_text="Email notifications for security")
    
    # SMS notifications
    sms_notifications = models.BooleanField(default=False, help_text="Enable SMS notifications")
    sms_credit_warning = models.BooleanField(default=True, help_text="SMS notifications for low credit")
    sms_critical = models.BooleanField(default=True, help_text="SMS notifications for critical issues")
    
    # In-app notifications
    in_app_notifications = models.BooleanField(default=True, help_text="Enable in-app notifications")
    
    # Credit warning thresholds
    credit_warning_threshold = models.IntegerField(
        default=25,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentage threshold for credit warning (1-100)"
    )
    credit_critical_threshold = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentage threshold for critical credit warning (1-100)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Settings"
        verbose_name_plural = "Notification Settings"
    
    def __str__(self):
        return f"Notification settings for {self.user.email}"
    
    def should_notify_email(self, notification_type):
        """Check if email notification should be sent for given type."""
        if not self.email_notifications:
            return False
        
        type_mapping = {
            NotificationType.SMS_CREDIT: self.email_sms_credit,
            NotificationType.CAMPAIGN: self.email_campaigns,
            NotificationType.CONTACT: self.email_contacts,
            NotificationType.BILLING: self.email_billing,
            NotificationType.SECURITY: self.email_security,
        }
        
        return type_mapping.get(notification_type, True)
    
    def should_notify_sms(self, notification_type, priority):
        """Check if SMS notification should be sent for given type and priority."""
        if not self.sms_notifications:
            return False
        
        if priority == NotificationPriority.URGENT:
            return True
        
        if notification_type == NotificationType.SMS_CREDIT and self.sms_credit_warning:
            return True
        
        if priority == NotificationPriority.HIGH and self.sms_critical:
            return True
        
        return False
