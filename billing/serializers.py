"""
Serializers for billing models.
"""
from rest_framework import serializers
from .models import Plan, Subscription, Invoice, UsageRecord, PaymentMethod, Coupon


class PlanSerializer(serializers.ModelSerializer):
    """Serializer for Plan model."""
    
    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'plan_type', 'description', 'price_monthly', 'price_yearly',
            'messages_limit', 'cost_limit', 'users_limit', 'features', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_trial = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'tenant', 'plan', 'plan_name', 'status', 'billing_cycle',
            'current_period_start', 'current_period_end', 'trial_end',
            'is_active', 'is_trial', 'created_at', 'updated_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'cancelled_at'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'tenant', 'tenant_name', 'subscription', 'invoice_number',
            'status', 'subtotal', 'tax_amount', 'total_amount', 'amount_paid',
            'amount_due', 'currency', 'invoice_date', 'due_date', 'paid_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'created_at', 'updated_at'
        ]


class UsageRecordSerializer(serializers.ModelSerializer):
    """Serializer for UsageRecord model."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = UsageRecord
        fields = [
            'id', 'tenant', 'tenant_name', 'subscription', 'metric_name',
            'quantity', 'unit_price', 'total_cost', 'period_start', 'period_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'tenant', 'tenant_name', 'payment_type', 'is_default',
            'card_brand', 'card_last4', 'card_exp_month', 'card_exp_year',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for Coupon model."""
    
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'name', 'description', 'coupon_type', 'discount_value',
            'currency', 'max_uses', 'used_count', 'valid_from', 'valid_until',
            'is_valid', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'used_count', 'is_valid', 'created_at', 'updated_at'
        ]


class CreateSubscriptionSerializer(serializers.Serializer):
    """Serializer for creating a subscription."""
    
    plan_id = serializers.UUIDField()
    billing_cycle = serializers.ChoiceField(choices=['monthly', 'yearly'])
    payment_method_id = serializers.UUIDField(required=False)
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate_plan_id(self, value):
        """Validate plan exists and is active."""
        try:
            plan = Plan.objects.get(id=value, is_active=True)
            return value
        except Plan.DoesNotExist:
            raise serializers.ValidationError("Invalid plan ID")
    
    def validate_coupon_code(self, value):
        """Validate coupon code if provided."""
        if value:
            try:
                coupon = Coupon.objects.get(code=value, is_active=True)
                if not coupon.is_valid:
                    raise serializers.ValidationError("Coupon is not valid")
                return value
            except Coupon.DoesNotExist:
                raise serializers.ValidationError("Invalid coupon code")
        return value


class UpdateSubscriptionSerializer(serializers.Serializer):
    """Serializer for updating a subscription."""
    
    plan_id = serializers.UUIDField(required=False)
    billing_cycle = serializers.ChoiceField(choices=['monthly', 'yearly'], required=False)
    payment_method_id = serializers.UUIDField(required=False)


class BillingOverviewSerializer(serializers.Serializer):
    """Serializer for billing overview."""
    
    current_plan = PlanSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    current_usage = serializers.DictField(read_only=True)
    upcoming_invoice = InvoiceSerializer(read_only=True)
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)
    recent_invoices = InvoiceSerializer(many=True, read_only=True)
    usage_history = UsageRecordSerializer(many=True, read_only=True)
