"""
Admin configuration for billing models.
"""
from django.contrib import admin
from .models import (
    SMSPackage, SMSBalance, Purchase, UsageRecord, 
    BillingPlan, Subscription
)


@admin.register(SMSPackage)
class SMSPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'credits', 'price', 'unit_price', 'is_popular', 'is_active']
    list_filter = ['package_type', 'is_popular', 'is_active', 'created_at']
    search_fields = ['name', 'package_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SMSBalance)
class SMSBalanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'credits', 'total_purchased', 'total_used', 'last_updated']
    list_filter = ['created_at', 'last_updated']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'last_updated']
    raw_id_fields = ['user']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'package', 'credits', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['invoice_number', 'user__email', 'package__name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['package', 'user']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'credits_used', 'cost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'message']


@admin.register(BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'currency', 'billing_cycle', 'is_active']
    list_filter = ['plan_type', 'billing_cycle', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'current_period_end', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'plan__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'plan']
