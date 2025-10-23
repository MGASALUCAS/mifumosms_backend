"""
Admin configuration for notification models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Notification, NotificationSettings, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = [
        'title', 'user', 'notification_type', 'priority', 'status',
        'is_system', 'is_auto_generated', 'created_at', 'time_ago_display'
    ]
    list_filter = [
        'notification_type', 'priority', 'status', 'is_system',
        'is_auto_generated', 'created_at'
    ]
    search_fields = ['title', 'message', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'tenant', 'title', 'message')
        }),
        ('Notification Details', {
            'fields': ('notification_type', 'priority', 'status', 'data')
        }),
        ('Actions', {
            'fields': ('action_url', 'action_text')
        }),
        ('System Information', {
            'fields': ('is_system', 'is_auto_generated', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'read_at'),
            'classes': ('collapse',)
        })
    )
    
    def time_ago_display(self, obj):
        """Display time ago in admin."""
        return obj.time_ago
    time_ago_display.short_description = 'Time Ago'
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('user', 'tenant')
    
    def has_add_permission(self, request):
        """Allow adding notifications in admin."""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow changing notifications in admin."""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting notifications in admin."""
        return True


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationSettings model."""
    
    list_display = [
        'user', 'email_notifications', 'sms_notifications',
        'credit_warning_threshold', 'credit_critical_threshold'
    ]
    list_filter = [
        'email_notifications', 'sms_notifications', 'in_app_notifications',
        'email_sms_credit', 'email_campaigns', 'email_contacts',
        'email_billing', 'email_security'
    ]
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_notifications', 'email_sms_credit', 'email_campaigns',
                'email_contacts', 'email_billing', 'email_security'
            )
        }),
        ('SMS Notifications', {
            'fields': ('sms_notifications', 'sms_credit_warning', 'sms_critical')
        }),
        ('In-App Notifications', {
            'fields': ('in_app_notifications',)
        }),
        ('Credit Warning Thresholds', {
            'fields': ('credit_warning_threshold', 'credit_critical_threshold')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related('user')


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationTemplate model."""
    
    list_display = [
        'name', 'notification_type', 'priority', 'is_active',
        'created_at', 'updated_at'
    ]
    list_filter = ['notification_type', 'priority', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'is_active')
        }),
        ('Template Content', {
            'fields': ('title_template', 'message_template', 'variables')
        }),
        ('Notification Settings', {
            'fields': ('notification_type', 'priority')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request)
    
    def has_add_permission(self, request):
        """Allow adding templates in admin."""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow changing templates in admin."""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting templates in admin."""
        return True
