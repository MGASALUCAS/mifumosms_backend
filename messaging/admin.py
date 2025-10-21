"""
Clean admin configuration for messaging models - organized and streamlined.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from .models import (
    Contact, Segment, Template, Conversation, Message, Attachment,
    Campaign, Flow
)
from .models_sms import (
    SMSProvider, SMSSenderID, SMSMessage,
    SMSTemplate, SMSDeliveryReport, SMSBulkUpload, SMSSchedule
)
from .models_sender_requests import SenderIDRequest
from . import admin_sender_requests

# =============================================================================
# CORE MESSAGING MODELS
# =============================================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Manage contacts and customer information."""
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
        if not change:
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
    """Manage contact segments for targeted messaging."""
    list_display = ['name', 'created_by', 'contact_count', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['contact_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Manage message templates."""
    list_display = ['name', 'created_by', 'category', 'language', 'approved', 'usage_count', 'created_at']
    list_filter = ['category', 'language', 'approved', 'created_at', 'created_by']
    search_fields = ['name', 'body_text', 'created_by__email']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Manage customer conversations and chat history."""
    list_display = ['contact', 'status', 'message_count', 'unread_count', 'last_message_at']
    list_filter = ['status', 'created_at', 'last_message_at']
    search_fields = ['contact__name', 'contact__phone_e164', 'subject']
    readonly_fields = ['message_count', 'unread_count', 'created_at', 'updated_at', 'last_message_at', 'closed_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Manage individual messages in conversations."""
    list_display = ['conversation', 'recipient_display', 'direction_badge', 'provider', 'status_badge', 'preview_text', 'created_at']
    list_filter = ['direction', 'provider', 'status', 'created_at']
    search_fields = ['text', 'conversation__contact__name', 'recipient_number']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at']
    list_per_page = 25

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

    def recipient_display(self, obj):
        if obj.conversation and obj.conversation.contact:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.conversation.contact.name,
                obj.conversation.contact.phone_e164 or obj.conversation.contact.phone_number
            )
        elif obj.recipient_number:
            return format_html('<strong>{}</strong>', obj.recipient_number)
        else:
            return format_html('<span class="text-muted">-</span>')
    recipient_display.short_description = 'Recipient'


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """Manage file attachments in messages."""
    list_display = ['message', 'file_name', 'file_type', 'file_size', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['file_name']
    readonly_fields = ['created_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Manage SMS and messaging campaigns."""
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
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    """Manage automated messaging flows and workflows."""
    list_display = ['name', 'created_by', 'active', 'trigger_count', 'created_at']
    list_filter = ['active', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['trigger_count', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# =============================================================================
# SMS MANAGEMENT MODELS
# =============================================================================

@admin.register(SMSProvider)
class SMSProviderAdmin(admin.ModelAdmin):
    """Configure SMS service providers and API settings."""
    list_display = [
        'name', 'provider_type', 'tenant', 'is_active', 'is_default',
        'cost_per_sms', 'currency', 'created_at'
    ]
    list_filter = [
        'provider_type', 'is_active', 'is_default', 'currency', 'created_at', 'tenant'
    ]
    search_fields = [
        'name', 'provider_type', 'tenant__name', 'api_key'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    list_per_page = 25

    fieldsets = (
        ('Provider Information', {
            'fields': ('name', 'provider_type', 'tenant', 'is_active', 'is_default'),
            'classes': ('wide',)
        }),
        ('API Configuration', {
            'fields': ('api_key', 'secret_key', 'api_url', 'webhook_url'),
            'classes': ('wide',)
        }),
        ('Cost Configuration', {
            'fields': ('cost_per_sms', 'currency'),
            'classes': ('wide',)
        }),
        ('Settings', {
            'fields': ('settings',),
            'classes': ('wide', 'collapse')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('wide', 'collapse')
        }),
    )


@admin.register(SMSSenderID)
class SMSSenderIDAdmin(admin.ModelAdmin):
    """Manage approved SMS sender IDs."""
    list_display = [
        'sender_id', 'tenant', 'provider', 'status_badge', 'created_at'
    ]
    list_filter = [
        'status', 'provider__provider_type', 'created_at', 'tenant'
    ]
    search_fields = [
        'sender_id', 'tenant__name', 'provider__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'provider_sender_id'
    ]
    list_per_page = 25

    def status_badge(self, obj):
        status_colors = {
            'pending': 'badge-warning',
            'active': 'badge-success',
            'inactive': 'badge-secondary',
            'rejected': 'badge-danger'
        }
        color = status_colors.get(obj.status, 'badge-secondary')
        return format_html(f'<span class="badge {color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    """Monitor SMS message delivery and status."""
    list_display = [
        'base_message', 'provider', 'sender_id', 'status_badge', 'cost_amount', 'sent_at'
    ]
    list_filter = [
        'status', 'provider__provider_type', 'sent_at', 'created_at'
    ]
    search_fields = [
        'base_message__text', 'sender_id__sender_id', 'provider__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'sent_at', 'delivered_at'
    ]
    list_per_page = 25

    def status_badge(self, obj):
        status_colors = {
            'queued': 'badge-warning',
            'sent': 'badge-info',
            'delivered': 'badge-success',
            'failed': 'badge-danger',
            'read': 'badge-success'
        }
        color = status_colors.get(obj.status, 'badge-secondary')
        return format_html(f'<span class="badge {color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    """Create and manage SMS message templates."""
    list_display = [
        'name', 'category', 'tenant', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'is_active', 'created_at', 'tenant'
    ]
    search_fields = [
        'name', 'message', 'category', 'tenant__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    list_per_page = 25


@admin.register(SMSDeliveryReport)
class SMSDeliveryReportAdmin(admin.ModelAdmin):
    """View SMS delivery reports and analytics."""
    list_display = [
        'sms_message', 'status', 'dest_addr', 'delivered_at', 'received_at'
    ]
    list_filter = [
        'status', 'delivered_at', 'received_at'
    ]
    search_fields = [
        'sms_message__base_message__text', 'provider_message_id', 'dest_addr'
    ]
    readonly_fields = [
        'id', 'received_at', 'delivered_at'
    ]
    list_per_page = 25


@admin.register(SMSBulkUpload)
class SMSBulkUploadAdmin(admin.ModelAdmin):
    """Manage bulk SMS uploads and batch processing."""
    list_display = [
        'file_name', 'tenant', 'status_badge', 'total_rows', 'processed_rows', 'created_at'
    ]
    list_filter = [
        'status', 'created_at', 'tenant'
    ]
    search_fields = [
        'file_name', 'tenant__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'completed_at', 'total_rows', 'processed_rows', 'successful_rows', 'failed_rows'
    ]
    list_per_page = 25

    def status_badge(self, obj):
        status_colors = {
            'pending': 'badge-warning',
            'processing': 'badge-info',
            'completed': 'badge-success',
            'failed': 'badge-danger'
        }
        color = status_colors.get(obj.status, 'badge-secondary')
        return format_html(f'<span class="badge {color}">{obj.status.title()}</span>')
    status_badge.short_description = 'Status'


@admin.register(SMSSchedule)
class SMSScheduleAdmin(admin.ModelAdmin):
    """Schedule automated SMS messages and campaigns."""
    list_display = [
        'name', 'tenant', 'frequency', 'is_active', 'next_run', 'created_at'
    ]
    list_filter = [
        'frequency', 'is_active', 'created_at', 'tenant'
    ]
    search_fields = [
        'name', 'tenant__name'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'next_run', 'last_run'
    ]
    list_per_page = 25

    fieldsets = (
        ('Schedule Information', {
            'fields': ('name', 'tenant', 'frequency', 'is_active'),
            'classes': ('wide',)
        }),
        ('Timing', {
            'fields': ('next_run', 'last_run'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('wide', 'collapse')
        }),
    )


# =============================================================================
# ADMIN CUSTOMIZATION
# =============================================================================

# Customize admin site headers
admin.site.site_header = "Mifumo SMS Management"
admin.site.site_title = "Mifumo Admin"
admin.site.index_title = "SMS & Messaging Administration"

# Use default Django admin index template (no custom override)
