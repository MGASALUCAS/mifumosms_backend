"""
Admin configuration for billing models.
"""
from django.contrib import admin
from .models import (
    SMSPackage, SMSBalance, Purchase, UsageRecord, 
    BillingPlan, Subscription, PaymentTransaction
)


@admin.register(SMSPackage)
class SMSPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'package_type', 'credits', 'price', 'unit_price', 'is_popular', 'is_active']
    list_filter = ['package_type', 'is_popular', 'is_active', 'created_at']
    search_fields = ['name', 'package_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SMSBalance)
class SMSBalanceAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'credits', 'total_purchased', 'total_used', 'last_updated']
    list_filter = ['created_at', 'last_updated']
    search_fields = ['tenant__name', 'tenant__domain']
    readonly_fields = ['created_at', 'last_updated']
    raw_id_fields = ['tenant']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'tenant', 'user', 'package', 'credits', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['invoice_number', 'tenant__name', 'user__email', 'package__name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['package', 'user', 'tenant', 'payment_transaction']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'user', 'credits_used', 'cost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tenant__name', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['tenant', 'user', 'message']


@admin.register(BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'currency', 'billing_cycle', 'is_active']
    list_filter = ['plan_type', 'billing_cycle', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'plan', 'status', 'current_period_end', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['tenant__name', 'plan__name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['tenant', 'plan']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'tenant', 'user', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'completed_at']
    search_fields = ['order_id', 'zenopay_order_id', 'invoice_number', 'tenant__name', 'user__email', 'buyer_email', 'buyer_name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'failed_at', 'zenopay_order_id', 'order_id', 'invoice_number']
    raw_id_fields = ['tenant', 'user']
    fieldsets = (
        ('Transaction Details', {
            'fields': ('order_id', 'zenopay_order_id', 'invoice_number', 'amount', 'currency', 'status')
        }),
        ('Customer Information', {
            'fields': ('buyer_email', 'buyer_name', 'buyer_phone')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_reference', 'webhook_url', 'webhook_received')
        }),
        ('ZenoPay Data', {
            'fields': ('zenopay_reference', 'zenopay_transid', 'zenopay_channel', 'zenopay_msisdn'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at', 'failed_at'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('webhook_data', 'metadata', 'error_message'),
            'classes': ('collapse',)
        })
    )
