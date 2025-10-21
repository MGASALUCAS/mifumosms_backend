"""
Serializers for billing functionality.
"""
from rest_framework import serializers
from .models import (
    SMSPackage, SMSBalance, Purchase, UsageRecord, 
    BillingPlan, Subscription, PaymentTransaction, CustomSMSPurchase
)


class SMSPackageSerializer(serializers.ModelSerializer):
    """Serializer for SMS packages."""
    savings_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = SMSPackage
        fields = [
            'id', 'name', 'package_type', 'credits', 'price', 'unit_price',
            'is_popular', 'is_active', 'features', 'savings_percentage',
            'default_sender_id', 'allowed_sender_ids', 'sender_id_restriction',
            'created_at', 'updated_at'
        ]


class SMSBalanceSerializer(serializers.ModelSerializer):
    """Serializer for SMS balance."""
    tenant = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = SMSBalance
        fields = [
            'id', 'tenant', 'credits', 'total_purchased', 'total_used', 
            'last_updated', 'created_at'
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializer for purchase records."""
    package_name = serializers.CharField(source='package.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tenant = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'invoice_number', 'package', 'package_name', 'tenant',
            'amount', 'credits', 'unit_price', 'payment_method',
            'payment_method_display', 'payment_reference', 'status',
            'status_display', 'created_at', 'completed_at'
        ]


class PurchaseCreateSerializer(serializers.Serializer):
    """Serializer for creating purchases."""
    package_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(choices=Purchase.PAYMENT_METHODS)
    payment_reference = serializers.CharField(required=False, allow_blank=True)
    
    def validate_package_id(self, value):
        """Validate that package exists and is active."""
        try:
            package = SMSPackage.objects.get(id=value, is_active=True)
            return value
        except SMSPackage.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive package")


class UsageRecordSerializer(serializers.ModelSerializer):
    """Serializer for usage records."""
    
    class Meta:
        model = UsageRecord
        fields = [
            'id', 'credits_used', 'cost', 'created_at'
        ]


class BillingPlanSerializer(serializers.ModelSerializer):
    """Serializer for billing plans."""
    
    class Meta:
        model = BillingPlan
        fields = [
            'id', 'name', 'plan_type', 'description', 'price', 'currency',
            'billing_cycle', 'max_contacts', 'max_campaigns', 'max_sms_per_month',
            'features', 'is_active', 'created_at'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.ReadOnlyField()
    tenant = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_name', 'tenant', 'status', 'status_display',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'is_active', 'created_at'
        ]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    purchase_data = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'order_id', 'zenopay_order_id', 'invoice_number',
            'amount', 'currency', 'buyer_email', 'buyer_name', 'buyer_phone',
            'payment_method', 'payment_method_display', 'status', 'status_display',
            'zenopay_reference', 'zenopay_transid', 'zenopay_channel', 'zenopay_msisdn',
            'webhook_received', 'created_at', 'updated_at', 'completed_at', 'failed_at',
            'error_message', 'purchase_data'
        ]
        read_only_fields = [
            'id', 'order_id', 'zenopay_order_id', 'invoice_number',
            'zenopay_reference', 'zenopay_transid', 'zenopay_channel', 'zenopay_msisdn',
            'webhook_received', 'created_at', 'updated_at', 'completed_at', 'failed_at'
        ]
    
    def get_purchase_data(self, obj):
        """Get related purchase data."""
        if obj.purchase:
            return {
                'id': str(obj.purchase.id),
                'package_name': obj.purchase.package.name,
                'credits': obj.purchase.credits,
                'unit_price': float(obj.purchase.unit_price)
            }
        return None


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating payments."""
    package_id = serializers.UUIDField()
    buyer_email = serializers.EmailField()
    buyer_name = serializers.CharField(max_length=100)
    buyer_phone = serializers.CharField(max_length=20)
    
    def validate_package_id(self, value):
        """Validate that package exists and is active."""
        try:
            package = SMSPackage.objects.get(id=value, is_active=True)
            return value
        except SMSPackage.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive package")
    
    def validate_buyer_phone(self, value):
        """Validate Tanzanian phone number format."""
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Check if it's a valid Tanzanian mobile number
        if phone.startswith('07') and len(phone) == 10:
            return value
        elif phone.startswith('2557') and len(phone) == 13:
            return value
        else:
            raise serializers.ValidationError(
                "Please provide a valid Tanzanian mobile number (e.g., 0744963858)"
            )


class CustomSMSPurchaseSerializer(serializers.ModelSerializer):
    """Serializer for custom SMS purchases."""
    active_tier = serializers.ReadOnlyField()
    tier_min_credits = serializers.ReadOnlyField()
    tier_max_credits = serializers.ReadOnlyField()
    unit_price = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomSMSPurchase
        fields = [
            'id', 'credits', 'unit_price', 'total_price', 'active_tier',
            'tier_min_credits', 'tier_max_credits', 'status', 'created_at',
            'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'completed_at']
    
    def validate_credits(self, value):
        """Validate that credits meet minimum requirement."""
        if value < 100:
            raise serializers.ValidationError(
                "Minimum 100 SMS credits required for custom purchase."
            )
        return value


class CustomSMSPurchaseCreateSerializer(serializers.Serializer):
    """Serializer for creating custom SMS purchases."""
    credits = serializers.IntegerField(min_value=100)
    buyer_email = serializers.EmailField()
    buyer_name = serializers.CharField(max_length=100)
    buyer_phone = serializers.CharField(max_length=20)
    mobile_money_provider = serializers.ChoiceField(
        choices=['vodacom', 'tigo', 'airtel', 'halotel'],
        default='vodacom'
    )
    
    def validate_credits(self, value):
        """Validate credits and calculate pricing."""
        if value < 100:
            raise serializers.ValidationError(
                "Minimum 100 SMS credits required for custom purchase."
            )
        return value
    
    def validate_buyer_phone(self, value):
        """Validate phone number format."""
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Check if it's a valid Tanzanian mobile number
        if phone.startswith(('07', '06')) and len(phone) == 10:
            return phone
        elif phone.startswith('255') and len(phone) == 12:
            # Convert from international format
            if phone[3:5] in ['07', '06']:
                return '0' + phone[3:]
        
        raise serializers.ValidationError(
            "Please provide a valid Tanzanian mobile number (e.g., 0744963858)"
        )