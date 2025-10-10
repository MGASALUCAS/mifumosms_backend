"""
Admin configuration for user models with Jazzmin enhancements.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'get_full_name', 'is_verified', 'is_active', 'get_tenant_name', 'created_at']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'created_at', 'email_notifications', 'sms_notifications']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    list_per_page = 25

    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password'),
            'classes': ('wide',)
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'timezone', 'avatar', 'bio'),
            'classes': ('wide',)
        }),
        ('Permissions & Access', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('wide',)
        }),
        ('Account Status', {
            'fields': ('is_verified', 'verification_token', 'verification_sent_at'),
            'classes': ('wide',)
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'sms_notifications'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'last_login_at'),
            'classes': ('wide', 'collapse')
        }),
    )

    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login_at', 'date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'

    def get_tenant_name(self, obj):
        tenant = obj.tenant
        if tenant:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:tenants_tenant_change', args=[tenant.pk]),
                tenant.name
            )
        return '-'
    get_tenant_name.short_description = 'Tenant'
    get_tenant_name.admin_order_field = 'memberships__tenant__name'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'job_title', 'company', 'industry', 'api_key_status', 'created_at']
    list_filter = ['preferred_language', 'date_format', 'time_format', 'industry', 'api_key_created_at']
    search_fields = ['user__email', 'job_title', 'company', 'industry']
    readonly_fields = ['api_key_created_at', 'created_at', 'updated_at']
    list_per_page = 25

    fieldsets = (
        ('User Information', {
            'fields': ('user',),
            'classes': ('wide',)
        }),
        ('Professional Details', {
            'fields': ('job_title', 'company', 'industry'),
            'classes': ('wide',)
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'date_format', 'time_format'),
            'classes': ('wide',)
        }),
        ('API Access', {
            'fields': ('api_key', 'api_key_created_at'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('wide', 'collapse')
        }),
    )

    def api_key_status(self, obj):
        if obj.api_key:
            return format_html(
                '<span class="badge badge-success">Active</span>'
            )
        return format_html(
            '<span class="badge badge-secondary">Not Generated</span>'
        )
    api_key_status.short_description = 'API Key Status'
