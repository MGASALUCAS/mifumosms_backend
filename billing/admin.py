"""
Admin configuration for billing models.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    SMSPackage, SMSBalance, Purchase, UsageRecord, 
    BillingPlan, Subscription, PaymentTransaction, CustomSMSPurchase
)


@admin.register(SMSPackage)
class SMSPackageAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'package_type', 'credits', 'price_formatted', 'unit_price_formatted', 
        'savings_display', 'status_badges', 'created_at'
    ]
    list_filter = ['package_type', 'sender_id_restriction', 'is_popular', 'is_active', 'created_at']
    search_fields = ['name', 'package_type', 'default_sender_id']
    readonly_fields = ['created_at', 'updated_at', 'savings_percentage']
    list_per_page = 25
    ordering = ['price']
    
    fieldsets = (
        ('Package Information', {
            'fields': ('name', 'package_type', 'credits', 'price', 'unit_price'),
            'classes': ('wide',)
        }),
        ('Pricing Details', {
            'fields': ('savings_percentage',),
            'classes': ('wide', 'collapse'),
            'description': 'Savings compared to standard rate (30 TZS per SMS)'
        }),
        ('Status & Features', {
            'fields': ('is_popular', 'is_active', 'features'),
            'classes': ('wide',)
        }),
        ('Sender ID Configuration', {
            'fields': (
                'default_sender_id', 
                'sender_id_restriction', 
                'allowed_sender_ids'
            ),
            'classes': ('wide',),
            'description': 'Configure which sender IDs are allowed for this package'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_formatted(self, obj):
        """Format price with currency."""
        return f"{obj.price:,.2f} TZS"
    price_formatted.short_description = 'Price'
    price_formatted.admin_order_field = 'price'
    
    def unit_price_formatted(self, obj):
        """Format unit price with currency."""
        return f"{obj.unit_price:,.2f} TZS"
    unit_price_formatted.short_description = 'Unit Price'
    unit_price_formatted.admin_order_field = 'unit_price'
    
    def savings_display(self, obj):
        """Display savings percentage with color coding."""
        try:
            # Ensure we have a valid object with unit_price
            if not hasattr(obj, 'unit_price') or obj.unit_price is None:
                return format_html('<span style="color: gray;">No data</span>')
            
            # Calculate savings manually to avoid property issues
            standard_rate = 30  # TZS per SMS
            unit_price = float(obj.unit_price)  # Ensure it's a float
            
            if unit_price < standard_rate:
                savings = round(((standard_rate - unit_price) / standard_rate) * 100, 1)
            else:
                savings = 0
            
            if savings > 0:
                color = 'green' if savings >= 20 else 'orange' if savings >= 10 else 'blue'
                # Use string formatting instead of format_html for the percentage
                savings_text = '{:.1f}% OFF'.format(savings)
                return format_html(
                    '<span style="color: {}; font-weight: bold;">{}</span>',
                    color, savings_text
                )
            return format_html('<span style="color: gray;">No savings</span>')
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            obj_name = obj.name if hasattr(obj, 'name') else 'unknown'
            logger.error("Savings display error for {}: {}".format(obj_name, str(e)))
            return format_html('<span style="color: red;">Error</span>')
    savings_display.short_description = 'Savings'
    
    def status_badges(self, obj):
        """Display status badges."""
        try:
            badges = []
            
            if obj.is_popular:
                badges.append('<span class="badge badge-success">Popular</span>')
            else:
                badges.append('<span class="badge badge-secondary">Regular</span>')
                
            if obj.is_active:
                badges.append('<span class="badge badge-success">Active</span>')
            else:
                badges.append('<span class="badge badge-danger">Inactive</span>')
                
            return mark_safe(' '.join(badges))
        except Exception as e:
            return mark_safe('<span class="badge badge-danger">Error</span>')
    status_badges.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related()
    
    def get_actions(self, request):
        """Add custom actions."""
        actions = super().get_actions(request)
        if request.user.has_perm('billing.change_smspackage'):
            actions['mark_as_popular'] = self.get_action('mark_as_popular')
            actions['mark_as_regular'] = self.get_action('mark_as_regular')
            actions['activate_packages'] = self.get_action('activate_packages')
            actions['deactivate_packages'] = self.get_action('deactivate_packages')
        return actions
    
    def mark_as_popular(self, request, queryset):
        """Mark selected packages as popular."""
        updated = queryset.update(is_popular=True)
        self.message_user(request, f'{updated} packages marked as popular.')
    mark_as_popular.short_description = "Mark selected packages as popular"
    
    def mark_as_regular(self, request, queryset):
        """Mark selected packages as regular (not popular)."""
        updated = queryset.update(is_popular=False)
        self.message_user(request, f'{updated} packages marked as regular.')
    mark_as_regular.short_description = "Mark selected packages as regular"
    
    def activate_packages(self, request, queryset):
        """Activate selected packages."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} packages activated.')
    activate_packages.short_description = "Activate selected packages"
    
    def deactivate_packages(self, request, queryset):
        """Deactivate selected packages."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} packages deactivated.')
    deactivate_packages.short_description = "Deactivate selected packages"


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
    raw_id_fields = ['package', 'tenant', 'user', 'payment_transaction']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'credits_used', 'cost', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tenant__name']
    readonly_fields = ['created_at']
    raw_id_fields = ['tenant', 'message']


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
    list_display = ['order_id', 'tenant', 'amount', 'currency', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'completed_at']
    search_fields = ['order_id', 'zenopay_order_id', 'invoice_number', 'tenant__name', 'buyer_email', 'buyer_name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'failed_at', 'zenopay_order_id', 'order_id', 'invoice_number']
    raw_id_fields = ['tenant']
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


@admin.register(CustomSMSPurchase)
class CustomSMSPurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tenant', 'credits', 'unit_price', 'total_price', 
        'active_tier', 'status', 'created_at'
    ]
    list_filter = ['status', 'active_tier', 'created_at', 'completed_at']
    search_fields = ['tenant__name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['tenant', 'payment_transaction']
    
    fieldsets = (
        ('Purchase Details', {
            'fields': ('tenant', 'credits', 'unit_price', 'total_price'),
            'classes': ('wide',)
        }),
        ('Pricing Tier', {
            'fields': ('active_tier', 'tier_min_credits', 'tier_max_credits'),
            'classes': ('wide',)
        }),
        ('Payment', {
            'fields': ('payment_transaction', 'status'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'payment_transaction')
