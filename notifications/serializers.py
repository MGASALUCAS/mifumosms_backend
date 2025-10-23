"""
Serializers for notification models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Notification, NotificationSettings, NotificationTemplate,
    NotificationType, NotificationPriority, NotificationStatus
)

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    
    time_ago = serializers.ReadOnlyField()
    is_unread = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority', 'status',
            'data', 'action_url', 'action_text', 'created_at', 'updated_at',
            'read_at', 'expires_at', 'is_system', 'is_auto_generated',
            'time_ago', 'is_unread'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'read_at', 'is_system',
            'is_auto_generated', 'time_ago', 'is_unread'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'priority',
            'data', 'action_url', 'action_text', 'expires_at'
        ]
    
    def validate_notification_type(self, value):
        """Validate notification type."""
        if value not in [choice[0] for choice in NotificationType.choices]:
            raise serializers.ValidationError("Invalid notification type")
        return value
    
    def validate_priority(self, value):
        """Validate priority."""
        if value not in [choice[0] for choice in NotificationPriority.choices]:
            raise serializers.ValidationError("Invalid priority")
        return value


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for NotificationSettings model."""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'email_notifications', 'email_sms_credit', 'email_campaigns',
            'email_contacts', 'email_billing', 'email_security',
            'sms_notifications', 'sms_credit_warning', 'sms_critical',
            'in_app_notifications', 'credit_warning_threshold',
            'credit_critical_threshold'
        ]
    
    def validate_credit_warning_threshold(self, value):
        """Validate credit warning threshold."""
        if not (1 <= value <= 100):
            raise serializers.ValidationError("Credit warning threshold must be between 1 and 100")
        return value
    
    def validate_credit_critical_threshold(self, value):
        """Validate credit critical threshold."""
        if not (1 <= value <= 100):
            raise serializers.ValidationError("Credit critical threshold must be between 1 and 100")
        return value
    
    def validate(self, attrs):
        """Validate that critical threshold is less than warning threshold."""
        warning_threshold = attrs.get('credit_warning_threshold')
        critical_threshold = attrs.get('credit_critical_threshold')
        
        if warning_threshold and critical_threshold:
            if critical_threshold >= warning_threshold:
                raise serializers.ValidationError(
                    "Critical threshold must be less than warning threshold"
                )
        
        return attrs


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'title_template', 'message_template',
            'notification_type', 'priority', 'is_active', 'variables',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    by_type = serializers.DictField()
    by_priority = serializers.DictField()
    recent_count = serializers.IntegerField()


class RecentNotificationSerializer(serializers.ModelSerializer):
    """Simplified serializer for recent notifications in header."""
    
    time_ago = serializers.ReadOnlyField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'action_url', 'action_text', 'created_at', 'time_ago'
        ]


class SystemNotificationCreateSerializer(serializers.Serializer):
    """Serializer for creating system notifications."""
    
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    priority = serializers.ChoiceField(
        choices=NotificationPriority.choices,
        default=NotificationPriority.MEDIUM
    )
    user_emails = serializers.ListField(
        child=serializers.EmailField(),
        required=False,
        help_text="List of user emails to notify. If empty, notifies all users in tenant."
    )
    action_url = serializers.URLField(required=False)
    action_text = serializers.CharField(max_length=100, required=False)
    
    def validate_user_emails(self, value):
        """Validate that all emails exist."""
        if value:
            existing_emails = set(User.objects.filter(
                email__in=value
            ).values_list('email', flat=True))
            
            missing_emails = set(value) - existing_emails
            if missing_emails:
                raise serializers.ValidationError(
                    f"Users with these emails do not exist: {', '.join(missing_emails)}"
                )
        
        return value


class SMSCreditTestSerializer(serializers.Serializer):
    """Serializer for testing SMS credit notifications."""
    
    current_credits = serializers.IntegerField(
        min_value=0,
        default=10,
        help_text="Current SMS credits"
    )
    total_credits = serializers.IntegerField(
        min_value=1,
        default=100,
        help_text="Total SMS credits purchased"
    )
    
    def validate(self, attrs):
        """Validate that current credits don't exceed total credits."""
        current = attrs.get('current_credits', 0)
        total = attrs.get('total_credits', 1)
        
        if current > total:
            raise serializers.ValidationError(
                "Current credits cannot exceed total credits"
            )
        
        return attrs
