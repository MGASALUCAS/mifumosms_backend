"""
Admin configuration for Sender ID Requests.
"""
from django.contrib import admin
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from .models_sender_requests import SenderIDRequest
from .models_sms import SenderNameRequest
from django.contrib.admin.sites import NotRegistered


@admin.register(SenderIDRequest)
class SenderIDRequestAdmin(admin.ModelAdmin):
    """Admin configuration for Sender ID Requests."""
    list_display = [
        'requested_sender_id', 'tenant', 'user', 'request_type',
        'status_badge', 'created_at', 'reviewed_at', 'admin_actions'
    ]
    list_filter = [
        'status', 'request_type', 'created_at', 'reviewed_at', 'tenant'
    ]
    search_fields = [
        'requested_sender_id', 'tenant__name', 'user__email', 
        'user__first_name', 'user__last_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'reviewed_at', 'id'
    ]
    list_per_page = 25
    actions = ['approve_selected', 'reject_selected', 'require_changes_selected']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('requested_sender_id', 'sample_content', 'request_type'),
            'classes': ('wide',)
        }),
        ('Status & Review', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'rejection_reason'),
            'classes': ('wide',)
        }),
        ('Ownership', {
            'fields': ('tenant', 'user'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'id'),
            'classes': ('wide', 'collapse')
        }),
    )
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def _status_select_html(self):
        """Build a reusable status <select> based on model choices."""
        choices = dict(SenderIDRequest.STATUS_CHOICES)
        # maintain order as defined
        options = ''.join([f"<option value='{key}'>{label}</option>" for key, label in SenderIDRequest.STATUS_CHOICES])
        return options

    def admin_actions(self, obj):
        """Inline action buttons for each row."""
        approve_url = f"{obj.pk}/approve/"
        reject_url = f"{obj.pk}/reject/"
        require_changes_form = (
            f"<form action='{obj.pk}/require-changes/' method='post' style='display:inline;'>"
            f"<input type='text' name='reason' placeholder='Required changes' style='width:180px;margin-right:6px;'>"
            f"<button type='submit' class='button' style='background:#ffc107; color:black; padding:4px 8px; border-radius:4px;'>Require Changes</button>"
            f"</form>"
        )
        # Generic set-status form (works for any current status)
        set_status_form = (
            f"<form action='{obj.pk}/set-status/' method='post' style='display:inline;margin-left:6px;'>"
            f"<select name='status' style='height:28px;'>{self._status_select_html()}</select>"
            f"<input type='text' name='reason' placeholder='Optional reason' style='width:160px;margin:0 6px;'>"
            f"<button type='submit' class='button' style='background:#17a2b8; color:white; padding:4px 8px; border-radius:4px;'>Update</button>"
            f"</form>"
        )
        return format_html(
            '<a class="button" href="{}" style="margin-right:6px; background:#28a745; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;">Approve</a>'
            '<a class="button" href="{}" style="margin-right:6px; background:#dc3545; color:white; padding:4px 8px; border-radius:4px; text-decoration:none;">Reject</a>'
            '{}' '{}',
            approve_url, reject_url, mark_safe(require_changes_form), mark_safe(set_status_form)
        )
    admin_actions.short_description = 'Actions'
    
    def save_model(self, request, obj, form, change):
        """Handle saving the model."""
        if not change and not obj.user:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    # Bulk actions
    def approve_selected(self, request, queryset):
        updated = 0
        for req in queryset.filter(status='pending'):
            req.approve(request.user)
            updated += 1
        self.message_user(request, f"Approved {updated} request(s)")
    approve_selected.short_description = 'Approve selected pending requests'

    def reject_selected(self, request, queryset):
        updated = 0
        for req in queryset.filter(status='pending'):
            req.reject(request.user, reason='Rejected by admin action')
            updated += 1
        self.message_user(request, f"Rejected {updated} request(s)")
    reject_selected.short_description = 'Reject selected pending requests'

    def require_changes_selected(self, request, queryset):
        updated = 0
        for req in queryset.filter(status='pending'):
            req.status = 'requires_changes'
            req.rejection_reason = req.rejection_reason or 'Changes required by admin'
            req.reviewed_by = request.user
            req.reviewed_at = timezone.now()
            req.save(update_fields=['status', 'rejection_reason', 'reviewed_by', 'reviewed_at'])
            updated += 1
        self.message_user(request, f"Marked {updated} request(s) as Requires Changes")
    require_changes_selected.short_description = 'Mark selected as Requires Changes'

    # Row action URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:object_id>/approve/', self.admin_site.admin_view(self.approve_view), name='senderidrequest_approve'),
            path('<uuid:object_id>/reject/', self.admin_site.admin_view(self.reject_view), name='senderidrequest_reject'),
            path('<uuid:object_id>/require-changes/', self.admin_site.admin_view(csrf_exempt(self.require_changes_view)), name='senderidrequest_require_changes'),
            path('<uuid:object_id>/set-status/', self.admin_site.admin_view(csrf_exempt(self.set_status_view)), name='senderidrequest_set_status'),
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id):
        try:
            obj = SenderIDRequest.objects.get(pk=object_id)
            if obj.status == 'pending':
                obj.approve(request.user)
                self.message_user(request, 'Request approved')
        except SenderIDRequest.DoesNotExist:
            self.message_user(request, 'Request not found')
        from django.shortcuts import redirect
        return redirect('admin:messaging_senderidrequest_changelist')

    def reject_view(self, request, object_id):
        try:
            obj = SenderIDRequest.objects.get(pk=object_id)
            if obj.status == 'pending':
                obj.reject(request.user, reason='Rejected by admin')
                self.message_user(request, 'Request rejected')
        except SenderIDRequest.DoesNotExist:
            self.message_user(request, 'Request not found')
        from django.shortcuts import redirect
        return redirect('admin:messaging_senderidrequest_changelist')

    def require_changes_view(self, request, object_id):
        from django.shortcuts import redirect
        try:
            obj = SenderIDRequest.objects.get(pk=object_id)
            if obj.status == 'pending':
                reason = request.POST.get('reason') or 'Changes required by admin'
                obj.status = 'requires_changes'
                obj.rejection_reason = reason
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
                obj.save(update_fields=['status', 'rejection_reason', 'reviewed_by', 'reviewed_at'])
                self.message_user(request, 'Marked as Requires Changes')
        except SenderIDRequest.DoesNotExist:
            self.message_user(request, 'Request not found')
        return redirect('admin:messaging_senderidrequest_changelist')

    def set_status_view(self, request, object_id):
        from django.shortcuts import redirect
        try:
            obj = SenderIDRequest.objects.get(pk=object_id)
            new_status = (request.POST.get('status') or '').strip()
            reason = (request.POST.get('reason') or '').strip()
            valid_statuses = {k for k, _ in SenderIDRequest.STATUS_CHOICES}
            if new_status in valid_statuses:
                obj.status = new_status
                if new_status in ['rejected', 'requires_changes']:
                    obj.rejection_reason = reason or obj.rejection_reason or 'Updated by admin'
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
                obj.save(update_fields=['status', 'rejection_reason', 'reviewed_by', 'reviewed_at'])
                self.message_user(request, f'Status updated to {new_status}')
            else:
                self.message_user(request, f'Invalid status: {new_status}')
        except SenderIDRequest.DoesNotExist:
            self.message_user(request, 'Request not found')
        return redirect('admin:messaging_senderidrequest_changelist')

