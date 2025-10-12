"""
Admin configuration for messaging models with Jazzmin enhancements.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Contact, Segment, Template, Conversation, Message, Attachment,
    Campaign, Flow
)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_e164', 'email', 'created_by', 'status_badge', 'opt_in_status', 'created_at']
    list_filter = ['is_active', 'opt_in_at', 'opt_out_at', 'created_at', 'created_by']
    search_fields = ['name', 'phone_e164', 'email', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at', 'last_contacted_at', 'is_opted_in']
    list_per_page = 25

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'phone_e164', 'email'),
            'classes': ('wide',)
        }),
        ('Status & Preferences', {
            'fields': ('is_active', 'is_opted_in', 'opt_in_at', 'opt_out_at', 'last_contacted_at'),
            'classes': ('wide',)
        }),
        ('Ownership', {
            'fields': ('created_by',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide', 'collapse')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current user when creating a new contact."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge badge-success">Active</span>')
        return format_html('<span class="badge badge-secondary">Inactive</span>')
    status_badge.short_description = 'Status'

    def opt_in_status(self, obj):
        if obj.is_opted_in:
            return format_html('<span class="badge badge-info">Opted In</span>')
        return format_html('<span class="badge badge-warning">Not Opted In</span>')
    opt_in_status.short_description = 'Opt-in Status'

@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'contact_count', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['contact_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current user when creating a new segment."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'category', 'language', 'approved', 'usage_count', 'created_at']
    list_filter = ['category', 'language', 'approved', 'created_at', 'created_by']
    search_fields = ['name', 'body_text', 'created_by__email']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current user when creating a new template."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['contact', 'status', 'message_count', 'unread_count', 'last_message_at']
    list_filter = ['status', 'created_at', 'last_message_at']
    search_fields = ['contact__name', 'contact__phone_e164', 'subject']
    readonly_fields = ['message_count', 'unread_count', 'created_at', 'updated_at', 'last_message_at', 'closed_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'direction_badge', 'provider', 'status_badge', 'preview_text', 'created_at']
    list_filter = ['direction', 'provider', 'status', 'created_at']
    search_fields = ['text', 'conversation__contact__name']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at']
    list_per_page = 25

    fieldsets = (
        ('Message Content', {
            'fields': ('conversation', 'text', 'template'),
            'classes': ('wide',)
        }),
        ('Delivery Information', {
            'fields': ('direction', 'provider', 'status', 'created_by'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at', 'read_at', 'created_at', 'updated_at'),
            'classes': ('wide', 'collapse')
        }),
    )

    def direction_badge(self, obj):
        if obj.direction == 'inbound':
            return format_html('<span class="badge badge-info">Inbound</span>')
        return format_html('<span class="badge badge-primary">Outbound</span>')
    direction_badge.short_description = 'Direction'

    def status_badge(self, obj):
        status_colors = {
            'pending': 'badge-warning',
            'sent': 'badge-info',
            'delivered': 'badge-success',
            'failed': 'badge-danger',
            'read': 'badge-success'
        }
        color = status_colors.get(obj.status, 'badge-secondary')
        return format_html(f'<span class="badge {color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'

    def preview_text(self, obj):
        if obj.text:
            return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
        return '-'
    preview_text.short_description = 'Preview'

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['message', 'file_name', 'file_type', 'file_size', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['created_at']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'status', 'campaign_type', 'total_recipients', 'sent_count', 'created_at']
    list_filter = ['status', 'campaign_type', 'created_at', 'scheduled_at', 'created_by']
    search_fields = ['name', 'description', 'message_text', 'created_by__email']
    readonly_fields = [
        'total_recipients', 'sent_count', 'delivered_count', 'read_count', 'failed_count',
        'started_at', 'completed_at', 'created_at', 'updated_at', 'progress_percentage',
        'delivery_rate', 'read_rate', 'is_active', 'can_edit', 'can_start', 'can_pause', 'can_cancel'
    ]
    filter_horizontal = ['target_segments', 'target_contacts']

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current user when creating a new campaign."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'campaign_type', 'created_by'),
            'classes': ('wide',)
        }),
        ('Content', {
            'fields': ('message_text', 'template'),
            'classes': ('wide',)
        }),
        ('Targeting', {
            'fields': ('target_segments', 'target_contacts', 'target_criteria'),
            'classes': ('wide',)
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_at', 'is_recurring', 'recurring_schedule'),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('total_recipients', 'sent_count', 'delivered_count', 'read_count', 'failed_count'),
            'classes': ('wide', 'collapse')
        }),
        ('Cost Tracking', {
            'fields': ('estimated_cost', 'actual_cost'),
            'classes': ('wide', 'collapse')
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('wide', 'collapse')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('wide', 'collapse')
        }),
    )

@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'active', 'trigger_count', 'created_at']
    list_filter = ['active', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['trigger_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Automatically set created_by to the current user when creating a new flow."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
