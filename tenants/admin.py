"""
Admin configuration for tenant models.
"""
from django.contrib import admin
from .models import Tenant, Domain, Membership


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'business_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'wa_verified', 'created_at']
    search_fields = ['name', 'subdomain', 'business_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary', 'verified', 'created_at']
    list_filter = ['is_primary', 'verified', 'created_at']
    search_fields = ['domain', 'tenant__name']
    readonly_fields = ['id', 'created_at']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'status', 'joined_at']
    list_filter = ['role', 'status', 'invited_at']
    search_fields = ['user__email', 'tenant__name']
    readonly_fields = ['id', 'invited_at', 'joined_at']
