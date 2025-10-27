"""
Serializers for API integration system.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import APIAccount, APIKey, APIIntegration, APIUsageLog
from tenants.models import Tenant

User = get_user_model()


class APIAccountSerializer(serializers.ModelSerializer):
    """Serializer for API Account."""
    
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    api_keys_count = serializers.SerializerMethodField()
    integrations_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APIAccount
        fields = [
            'id', 'account_id', 'name', 'description', 'owner', 'tenant',
            'status', 'is_active', 'rate_limit_per_minute', 'rate_limit_per_hour',
            'rate_limit_per_day', 'total_api_calls', 'last_api_call',
            'created_at', 'updated_at', 'expires_at',
            # Read-only fields
            'owner_email', 'owner_name', 'tenant_name', 'api_keys_count', 'integrations_count'
        ]
        read_only_fields = [
            'id', 'account_id', 'owner', 'tenant', 'total_api_calls', 'last_api_call',
            'created_at', 'updated_at', 'api_keys_count', 'integrations_count'
        ]
    
    def get_api_keys_count(self, obj):
        """Get count of active API keys."""
        return obj.api_keys.filter(is_active=True).count()
    
    def get_integrations_count(self, obj):
        """Get count of active integrations."""
        return obj.integrations.filter(is_active=True).count()


class APIAccountCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API Account."""
    
    class Meta:
        model = APIAccount
        fields = [
            'name', 'description', 'rate_limit_per_minute', 'rate_limit_per_hour',
            'rate_limit_per_day', 'expires_at'
        ]
    
    def create(self, validated_data):
        """Create API account with generated account_id."""
        # Get user and tenant from context
        user = self.context['request'].user
        tenant = getattr(user, 'tenant', None)
        
        if not tenant:
            raise serializers.ValidationError("User must be associated with a tenant")
        
        # Generate account_id
        validated_data['account_id'] = self.generate_account_id()
        validated_data['owner'] = user
        validated_data['tenant'] = tenant
        
        return super().create(validated_data)
    
    def generate_account_id(self):
        """Generate unique account ID."""
        import secrets
        return secrets.token_urlsafe(16).upper()


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API Key."""
    
    api_account_name = serializers.CharField(source='api_account.name', read_only=True)
    account_id = serializers.CharField(source='api_account.account_id', read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'api_account', 'key_name', 'api_key', 'secret_key',
            'status', 'is_active', 'permissions', 'total_uses', 'last_used',
            'last_used_ip', 'created_at', 'updated_at', 'expires_at', 'revoked_at',
            # Read-only fields
            'api_account_name', 'account_id'
        ]
        read_only_fields = [
            'id', 'api_account', 'api_key', 'secret_key', 'total_uses', 'last_used',
            'last_used_ip', 'created_at', 'updated_at', 'revoked_at'
        ]
    
    def to_representation(self, instance):
        """Customize representation to hide sensitive data."""
        data = super().to_representation(instance)
        
        # Only show full API key to the owner
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if not (hasattr(instance, 'api_account') and 
                   instance.api_account.owner == user):
                # Hide sensitive data for non-owners
                data['api_key'] = f"{instance.api_key[:8]}..." if instance.api_key else None
                data['secret_key'] = "***" if instance.secret_key else None
        
        return data


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API Key."""
    
    class Meta:
        model = APIKey
        fields = [
            'key_name', 'permissions', 'expires_at'
        ]
    
    def create(self, validated_data):
        """Create API key with generated credentials."""
        # Get API account from context
        api_account = self.context['api_account']
        
        # Generate API key and secret
        api_key, secret_key = self.generate_credentials()
        
        validated_data['api_account'] = api_account
        validated_data['api_key'] = api_key
        validated_data['secret_key'] = secret_key
        
        return super().create(validated_data)
    
    def generate_credentials(self):
        """Generate API key and secret key."""
        import secrets
        api_key = f"mif_{secrets.token_urlsafe(32)}"
        secret_key = secrets.token_urlsafe(32)
        return api_key, secret_key


class APIIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for API Integration."""
    
    api_account_name = serializers.CharField(source='api_account.name', read_only=True)
    account_id = serializers.CharField(source='api_account.account_id', read_only=True)
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = APIIntegration
        fields = [
            'id', 'api_account', 'name', 'description', 'platform', 'webhook_url',
            'status', 'is_active', 'config', 'total_requests', 'successful_requests',
            'failed_requests', 'last_request', 'created_at', 'updated_at',
            # Read-only fields
            'api_account_name', 'account_id', 'success_rate'
        ]
        read_only_fields = [
            'id', 'api_account', 'total_requests', 'successful_requests',
            'failed_requests', 'last_request', 'created_at', 'updated_at'
        ]
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage."""
        if obj.total_requests == 0:
            return 0.0
        return round((obj.successful_requests / obj.total_requests) * 100, 2)
    
    def validate_webhook_url(self, value):
        """Validate webhook URL."""
        if value:
            from .utils import validate_webhook_url
            is_valid, error_message = validate_webhook_url(value)
            if not is_valid:
                raise serializers.ValidationError(error_message)
        return value


class APIIntegrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API Integration."""
    
    class Meta:
        model = APIIntegration
        fields = [
            'name', 'description', 'platform', 'webhook_url', 'config'
        ]
    
    def create(self, validated_data):
        """Create API integration."""
        # Get API account from context
        api_account = self.context['api_account']
        validated_data['api_account'] = api_account
        
        return super().create(validated_data)
    
    def validate_webhook_url(self, value):
        """Validate webhook URL."""
        if value:
            from .utils import validate_webhook_url
            is_valid, error_message = validate_webhook_url(value)
            if not is_valid:
                raise serializers.ValidationError(error_message)
        return value


class APIUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for API Usage Log."""
    
    api_account_name = serializers.CharField(source='api_account.name', read_only=True)
    account_id = serializers.CharField(source='api_account.account_id', read_only=True)
    api_key_name = serializers.CharField(source='api_key.key_name', read_only=True)
    integration_name = serializers.CharField(source='integration.name', read_only=True)
    
    class Meta:
        model = APIUsageLog
        fields = [
            'id', 'api_account', 'api_key', 'integration', 'endpoint', 'method',
            'status_code', 'ip_address', 'user_agent', 'request_size', 'response_size',
            'response_time_ms', 'error_message', 'timestamp',
            # Read-only fields
            'api_account_name', 'account_id', 'api_key_name', 'integration_name'
        ]
        read_only_fields = [
            'id', 'api_account', 'api_key', 'integration', 'timestamp'
        ]


class APIAccountStatsSerializer(serializers.Serializer):
    """Serializer for API Account statistics."""
    
    account_id = serializers.CharField()
    name = serializers.CharField()
    total_api_calls = serializers.IntegerField()
    active_api_keys = serializers.IntegerField()
    active_integrations = serializers.IntegerField()
    success_rate = serializers.FloatField()
    rate_limit_info = serializers.DictField()
    last_activity = serializers.DateTimeField()


class APIKeyStatsSerializer(serializers.Serializer):
    """Serializer for API Key statistics."""
    
    key_name = serializers.CharField()
    api_key = serializers.CharField()
    total_uses = serializers.IntegerField()
    last_used = serializers.DateTimeField()
    last_used_ip = serializers.IPAddressField()
    is_active = serializers.BooleanField()


class IntegrationStatsSerializer(serializers.Serializer):
    """Serializer for Integration statistics."""
    
    name = serializers.CharField()
    platform = serializers.CharField()
    total_requests = serializers.IntegerField()
    success_rate = serializers.FloatField()
    last_request = serializers.DateTimeField()
    is_active = serializers.BooleanField()






