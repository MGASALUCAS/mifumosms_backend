"""
Admin configuration for billing models.
"""
from django.contrib import admin
from .models import Plan, Subscription, Invoice, UsageRecord, PaymentMethod, Coupon


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_monthly', 'price_yearly', 'messages_limit', 'is_active']
    list_filter = ['plan_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'plan', 'status', 'billing_cycle', 'current_period_end', 'created_at']
    list_filter = ['status', 'billing_cycle', 'created_at']
    search_fields = ['tenant__name', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']
    raw_id_fields = ['tenant', 'plan']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'tenant', 'status', 'total_amount', 'invoice_date']
    list_filter = ['status', 'currency', 'invoice_date']
    search_fields = ['invoice_number', 'tenant__name', 'stripe_invoice_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    raw_id_fields = ['tenant', 'subscription']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'metric_name', 'quantity', 'total_cost', 'period_start']
    list_filter = ['metric_name', 'period_start', 'created_at']
    search_fields = ['tenant__name', 'metric_name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['tenant', 'subscription']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'payment_type', 'card_brand', 'card_last4', 'is_default', 'is_active']
    list_filter = ['payment_type', 'is_default', 'is_active', 'created_at']
    search_fields = ['tenant__name', 'stripe_payment_method_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['tenant']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'coupon_type', 'discount_value', 'used_count', 'is_valid', 'is_active']
    list_filter = ['coupon_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code', 'name']
    readonly_fields = ['used_count', 'is_valid', 'created_at', 'updated_at']
