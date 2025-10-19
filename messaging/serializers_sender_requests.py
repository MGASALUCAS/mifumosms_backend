"""
Serializers for sender ID request system.
"""
from rest_framework import serializers
from .models_sender_requests import SenderIDRequest, SenderIDUsage
from billing.models import SMSPackage


class SenderIDRequestSerializer(serializers.ModelSerializer):
    """Serializer for sender ID requests."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    reviewed_by_email = serializers.CharField(source='reviewed_by.email', read_only=True)
    sms_package_name = serializers.CharField(source='sms_package.name', read_only=True)
    
    class Meta:
        model = SenderIDRequest
        fields = [
            'id', 'tenant', 'user', 'request_type', 'requested_sender_id',
            'sample_content', 'business_justification', 'status',
            'reviewed_by', 'reviewed_at', 'rejection_reason', 'sms_package',
            'created_at', 'updated_at',
            # Read-only fields
            'user_email', 'tenant_name', 'reviewed_by_email', 'sms_package_name'
        ]
        read_only_fields = ['id', 'tenant', 'user', 'status', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at']

    def validate_requested_sender_id(self, value):
        """Validate the requested sender ID."""
        if not value:
            raise serializers.ValidationError("Sender ID is required.")
        
        if len(value) > 11:
            raise serializers.ValidationError("Sender ID cannot exceed 11 characters.")
        
        if not value.replace(' ', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Sender ID can only contain letters, numbers, spaces, and hyphens.")
        
        return value.upper()

    def validate_sample_content(self, value):
        """Validate the sample content."""
        if not value:
            raise serializers.ValidationError("Sample content is required.")
        
        if len(value) > 170:
            raise serializers.ValidationError("Sample content cannot exceed 170 characters.")
        
        return value

    def validate(self, data):
        """Validate the entire request."""
        # Note: SMS purchase is now optional for normal users
        # They can request sender ID first, then purchase SMS credits later
        tenant = self.context.get('tenant')
        
        # Check if sender ID already exists for this tenant
        if tenant:
            existing_request = SenderIDRequest.objects.filter(
                tenant=tenant,
                requested_sender_id=data.get('requested_sender_id')
            ).exclude(status='rejected').first()
            
            if existing_request:
                raise serializers.ValidationError("A request for this sender ID already exists.")
        
        return data


class SenderIDRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sender ID requests."""
    
    class Meta:
        model = SenderIDRequest
        fields = [
            'request_type', 'requested_sender_id', 'sample_content',
            'business_justification', 'sms_package'
        ]

    def validate_requested_sender_id(self, value):
        """Validate the requested sender ID."""
        if not value:
            raise serializers.ValidationError("Sender ID is required.")
        
        if len(value) > 11:
            raise serializers.ValidationError("Sender ID cannot exceed 11 characters.")
        
        if not value.replace(' ', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Sender ID can only contain letters, numbers, spaces, and hyphens.")
        
        return value.upper()

    def validate_sample_content(self, value):
        """Validate the sample content."""
        if not value:
            raise serializers.ValidationError("Sample content is required.")
        
        if len(value) > 170:
            raise serializers.ValidationError("Sample content cannot exceed 170 characters.")
        
        return value

    def validate(self, data):
        """Validate the entire request."""
        # Note: SMS purchase is now optional for normal users
        # They can request sender ID first, then purchase SMS credits later
        tenant = self.context.get('tenant')
        
        # Check if sender ID already exists for this tenant
        if tenant:
            existing_request = SenderIDRequest.objects.filter(
                tenant=tenant,
                requested_sender_id=data.get('requested_sender_id')
            ).exclude(status='rejected').first()
            
            if existing_request:
                raise serializers.ValidationError("A request for this sender ID already exists.")
        
        return data


class SenderIDRequestReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviewing sender ID requests (admin only)."""
    
    class Meta:
        model = SenderIDRequest
        fields = ['status', 'rejection_reason']

    def validate_status(self, value):
        """Validate the status change."""
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be either 'approved' or 'rejected'.")
        
        return value

    def validate(self, data):
        """Validate the review."""
        if data.get('status') == 'rejected' and not data.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting a request.")
        
        return data


class SenderIDUsageSerializer(serializers.ModelSerializer):
    """Serializer for sender ID usage tracking."""
    
    sender_id = serializers.CharField(source='sender_id_request.requested_sender_id', read_only=True)
    sms_package_name = serializers.CharField(source='sms_package.name', read_only=True)
    
    class Meta:
        model = SenderIDUsage
        fields = [
            'id', 'sender_id_request', 'sms_package', 'is_active',
            'attached_at', 'detached_at', 'created_at', 'updated_at',
            'sender_id', 'sms_package_name'
        ]
        read_only_fields = ['id', 'attached_at', 'detached_at', 'created_at', 'updated_at']


class SenderIDUsageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sender ID usage."""
    
    class Meta:
        model = SenderIDUsage
        fields = ['sender_id_request', 'sms_package']

    def validate(self, data):
        """Validate the usage creation."""
        sender_id_request = data.get('sender_id_request')
        sms_package = data.get('sms_package')
        
        # Check if sender ID request is approved
        if not sender_id_request.is_approved:
            raise serializers.ValidationError("Sender ID request must be approved before it can be used.")
        
        # Check if sender ID is already attached to this package
        existing_usage = SenderIDUsage.objects.filter(
            sender_id_request=sender_id_request,
            sms_package=sms_package,
            is_active=True
        ).first()
        
        if existing_usage:
            raise serializers.ValidationError("This sender ID is already attached to this SMS package.")
        
        return data
