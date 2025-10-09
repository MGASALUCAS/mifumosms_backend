"""
Serializers for billing functionality.
"""
from rest_framework import serializers
from .models import (
    SMSPackage, SMSBalance, Purchase, UsageRecord, 
    BillingPlan, Subscription
)


class SMSPackageSerializer(serializers.ModelSerializer):
    """Serializer for SMS packages."""
    savings_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = SMSPackage
        fields = [
            'id', 'name', 'package_type', 'credits', 'price', 'unit_price',
            'is_popular', 'features', 'savings_percentage'
        ]


class SMSBalanceSerializer(serializers.ModelSerializer):
    """Serializer for SMS balance."""
    
    class Meta:
        model = SMSBalance
        fields = [
            'id', 'credits', 'total_purchased', 'total_used', 
            'last_updated', 'created_at'
        ]


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializer for purchase records."""
    package_name = serializers.CharField(source='package.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'invoice_number', 'package', 'package_name',
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
            'features', 'is_active'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions."""
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_name', 'status', 'status_display',
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'is_active', 'created_at'
        ]