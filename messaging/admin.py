"""
Admin configuration for messaging models with Jazzmin enhancements.
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
from .models_sms import SenderNameRequest

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


@admin.register(SenderNameRequest)
class SenderNameRequestAdmin(admin.ModelAdmin):
    """Admin interface for managing sender name requests with approval/rejection actions."""

    list_display = [
        'sender_name', 'tenant', 'created_by', 'status_badge', 'supporting_docs_count',
        'created_at', 'reviewed_by', 'reviewed_at', 'admin_actions'
    ]
    list_filter = [
        'status', 'tenant', 'created_at', 'reviewed_at', 'created_by', 'reviewed_by'
    ]
    search_fields = [
        'sender_name', 'use_case', 'created_by__email', 'created_by__first_name',
        'created_by__last_name', 'tenant__name', 'admin_notes'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'supporting_documents_count',
        'provider_request_id', 'provider_response'
    ]
    list_per_page = 25
    list_select_related = ['tenant', 'created_by', 'reviewed_by']

    fieldsets = (
        ('Request Information', {
            'fields': ('sender_name', 'use_case', 'tenant', 'created_by'),
            'classes': ('wide',)
        }),
        ('Supporting Documents', {
            'fields': ('supporting_documents', 'supporting_documents_count'),
            'classes': ('wide',)
        }),
        ('Review & Status', {
            'fields': ('status', 'admin_notes', 'reviewed_by', 'reviewed_at'),
            'classes': ('wide',)
        }),
        ('Provider Integration', {
            'fields': ('provider_request_id', 'provider_response'),
            'classes': ('wide', 'collapse')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide', 'collapse')
        }),
    )

    actions = ['approve_requests', 'reject_requests', 'mark_requires_changes']

    def status_badge(self, obj):
        """Display status with color-coded badge and emoji."""
        status_config = {
            'pending': {
                'emoji': '🟡',
                'color': 'badge-warning',
                'text': 'Pending Review'
            },
            'approved': {
                'emoji': '🟢',
                'color': 'badge-success',
                'text': 'Approved'
            },
            'rejected': {
                'emoji': '🔴',
                'color': 'badge-danger',
                'text': 'Rejected'
            },
            'requires_changes': {
                'emoji': '🔵',
                'color': 'badge-info',
                'text': 'Requires Changes'
            }
        }

        config = status_config.get(obj.status, {
            'emoji': '⚪',
            'color': 'badge-secondary',
            'text': obj.get_status_display()
        })

        return format_html(
            '<span class="badge {}" style="font-size: 0.9rem; padding: 6px 12px; border-radius: 15px; font-weight: 600;">{} {}</span>',
            config['color'],
            config['emoji'],
            config['text']
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def supporting_docs_count(self, obj):
        """Display count of supporting documents with emoji."""
        count = obj.supporting_documents_count
        if count > 0:
            return format_html(
                '<span class="badge badge-info" style="font-size: 0.8rem; padding: 4px 10px; border-radius: 12px;">📎 {}</span>',
                count
            )
        return format_html(
            '<span class="badge badge-secondary" style="font-size: 0.8rem; padding: 4px 10px; border-radius: 12px;">📎 0</span>'
        )
    supporting_docs_count.short_description = 'Documents'
    supporting_docs_count.admin_order_field = 'supporting_documents_count'

    def admin_actions(self, obj):
        """Display action buttons for admin operations with emojis."""
        if obj.status == 'pending':
            approve_url = reverse('admin:messaging_sendernamerequest_approve', args=[obj.pk])
            reject_url = reverse('admin:messaging_sendernamerequest_reject', args=[obj.pk])
            return format_html(
                '<div style="display: flex; gap: 5px; flex-wrap: wrap;">'
                '<a class="button" href="{}" style="background: #28a745; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: none; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;" onclick="return confirm(\'Are you sure you want to approve this request?\')">✅ Approve</a>'
                '<a class="button" href="{}" style="background: #dc3545; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: none; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;" onclick="return confirm(\'Are you sure you want to reject this request?\')">❌ Reject</a>'
                '<button type="button" onclick="markAsRequiresChanges(\'{}\')" style="background: #17a2b8; color: white; padding: 6px 12px; border: none; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;">🔄 Requires Changes</button>'
                '</div>',
                approve_url, reject_url, obj.pk
            )
        elif obj.status == 'requires_changes':
            approve_url = reverse('admin:messaging_sendernamerequest_approve', args=[obj.pk])
            return format_html(
                '<div style="display: flex; gap: 5px; flex-wrap: wrap;">'
                '<a class="button" href="{}" style="background: #28a745; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 0.8rem; font-weight: 600; border: none; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;" onclick="return confirm(\'Are you sure you want to approve this request?\')">✅ Approve</a>'
                '<span style="color: #17a2b8; font-weight: 600; font-size: 0.9rem; padding: 6px 12px; background: #e0f7fa; border-radius: 6px;">🔄 Requires Changes</span>'
                '</div>',
                approve_url
            )
        elif obj.status == 'approved':
            return format_html(
                '<span style="color: #28a745; font-weight: 600; font-size: 0.9rem; padding: 6px 12px; background: #d4edda; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;">✅ Approved</span>'
            )
        elif obj.status == 'rejected':
            return format_html(
                '<span style="color: #dc3545; font-weight: 600; font-size: 0.9rem; padding: 6px 12px; background: #f8d7da; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;">❌ Rejected</span>'
            )
        return '-'
    admin_actions.short_description = 'Actions'

    def save_model(self, request, obj, form, change):
        """Automatically set reviewed_by when status changes."""
        if change and 'status' in form.changed_data:
            obj.reviewed_by = request.user
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

    def approve_requests(self, request, queryset):
        """Bulk approve selected requests."""
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'✅ {updated} requests approved successfully.')
    approve_requests.short_description = '✅ Approve selected requests'

    def reject_requests(self, request, queryset):
        """Bulk reject selected requests."""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'❌ {updated} requests rejected successfully.')
    reject_requests.short_description = '❌ Reject selected requests'

    def mark_requires_changes(self, request, queryset):
        """Mark selected requests as requiring changes."""
        updated = queryset.filter(status='pending').update(
            status='requires_changes',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f'🔄 {updated} requests marked as requiring changes.')
    mark_requires_changes.short_description = '🔄 Mark as requiring changes'

    def get_queryset(self, request):
        """Filter requests based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # For non-superusers, only show requests from their tenant
        if hasattr(request.user, 'tenant'):
            return qs.filter(tenant=request.user.tenant)
        return qs.none()

    def has_add_permission(self, request):
        """Allow admins to add new requests."""
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        """Allow admins to change requests."""
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        """Allow superusers to delete requests."""
        return request.user.is_superuser

    def get_urls(self):
        """Add custom URLs for approve/reject actions."""
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:request_id>/approve/',
                self.admin_site.admin_view(self.approve_request),
                name='messaging_sendernamerequest_approve',
            ),
            path(
                '<uuid:request_id>/reject/',
                self.admin_site.admin_view(self.reject_request),
                name='messaging_sendernamerequest_reject',
            ),
        ]
        return custom_urls + urls

    def approve_request(self, request, request_id):
        """Approve a single sender name request."""
        try:
            sender_request = SenderNameRequest.objects.get(id=request_id)
            sender_request.status = 'approved'
            sender_request.reviewed_by = request.user
            sender_request.reviewed_at = timezone.now()
            sender_request.save()

            messages.success(request, f'Sender name request "{sender_request.sender_name}" has been approved.')
        except SenderNameRequest.DoesNotExist:
            messages.error(request, 'Sender name request not found.')

        return redirect('admin:messaging_sendernamerequest_changelist')

    def reject_request(self, request, request_id):
        """Reject a single sender name request."""
        try:
            sender_request = SenderNameRequest.objects.get(id=request_id)
            sender_request.status = 'rejected'
            sender_request.reviewed_by = request.user
            sender_request.reviewed_at = timezone.now()
            sender_request.save()

            messages.success(request, f'Sender name request "{sender_request.sender_name}" has been rejected.')
        except SenderNameRequest.DoesNotExist:
            messages.error(request, 'Sender name request not found.')

        return redirect('admin:messaging_sendernamerequest_changelist')
