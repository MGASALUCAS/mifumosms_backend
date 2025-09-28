"""
Serializers for tenant-related models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tenant, Domain, Membership

User = get_user_model()


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'subdomain', 'timezone', 'created_at', 'updated_at',
            'business_name', 'business_type', 'phone_number', 'email', 'address',
            'wa_phone_number_id', 'wa_phone_number', 'wa_verified',
            'is_active', 'trial_ends_at', 'is_trial_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_trial_active']


class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new tenants."""
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'subdomain', 'timezone', 'business_name', 'business_type',
            'phone_number', 'email', 'address'
        ]
    
    def validate_subdomain(self, value):
        """Validate subdomain is unique and follows naming conventions."""
        if Tenant.objects.filter(subdomain=value).exists():
            raise serializers.ValidationError("This subdomain is already taken.")
        
        # Basic validation
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError("Subdomain can only contain letters, numbers, hyphens, and underscores.")
        
        if value.startswith('-') or value.endswith('-'):
            raise serializers.ValidationError("Subdomain cannot start or end with a hyphen.")
        
        return value


class DomainSerializer(serializers.ModelSerializer):
    """Serializer for Domain model."""
    
    class Meta:
        model = Domain
        fields = ['id', 'domain', 'is_primary', 'verified', 'created_at']
        read_only_fields = ['id', 'created_at']


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for Membership model."""
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_email', 'user_name', 'role', 'status',
            'invited_by', 'invited_by_email', 'invited_at', 'joined_at'
        ]
        read_only_fields = ['id', 'invited_at', 'joined_at']


class MembershipCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new memberships."""
    
    email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Membership
        fields = ['email', 'role']
    
    def create(self, validated_data):
        """Create membership by email."""
        email = validated_data.pop('email')
        tenant = self.context['tenant']
        invited_by = self.context['request'].user
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create user if doesn't exist
            user = User.objects.create_user(
                email=email,
                username=email,
                first_name='',
                last_name=''
            )
        
        membership, created = Membership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={
                'role': validated_data['role'],
                'invited_by': invited_by,
                'status': 'pending'
            }
        )
        
        if not created:
            raise serializers.ValidationError("User is already a member of this tenant.")
        
        return membership


class TenantSwitchSerializer(serializers.Serializer):
    """Serializer for switching between tenants."""
    
    tenant_id = serializers.UUIDField()
    
    def validate_tenant_id(self, value):
        """Validate user has access to the tenant."""
        request = self.context['request']
        try:
            membership = Membership.objects.get(
                tenant_id=value,
                user=request.user,
                status='active'
            )
            return value
        except Membership.DoesNotExist:
            raise serializers.ValidationError("You don't have access to this tenant.")
