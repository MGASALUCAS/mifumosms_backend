"""
SMS-specific serializers for Mifumo WMS.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models_sms import (
    SMSProvider, SMSSenderID, SMSTemplate, SMSMessage, 
    SMSDeliveryReport, SMSBulkUpload, SMSSchedule
)
from .models import Contact, Campaign

User = get_user_model()


class SMSProviderSerializer(serializers.ModelSerializer):
    """Serializer for SMS providers."""
    
    class Meta:
        model = SMSProvider
        fields = [
            'id', 'name', 'provider_type', 'is_active', 'is_default',
            'api_url', 'webhook_url', 'cost_per_sms', 'currency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate provider data."""
        if data.get('is_default') and data.get('is_active'):
            # Check if there's already a default provider
            existing_default = SMSProvider.objects.filter(
                tenant=self.context['request'].tenant,
                is_default=True,
                is_active=True
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_default.exists():
                raise serializers.ValidationError(
                    "Only one provider can be set as default"
                )
        
        return data


class SMSSenderIDSerializer(serializers.ModelSerializer):
    """Serializer for SMS sender IDs."""
    
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = SMSSenderID
        fields = [
            'id', 'sender_id', 'sample_content', 'status',
            'provider', 'provider_name', 'provider_sender_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider_sender_id', 'created_at', 'updated_at']
    
    def validate_sender_id(self, value):
        """Validate sender ID format."""
        if len(value) > 11:
            raise serializers.ValidationError("Sender ID cannot exceed 11 characters")
        
        # Check for valid characters (letters, numbers, space, hyphen, dot)
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', value):
            raise serializers.ValidationError(
                "Sender ID can only contain letters, numbers, space, hyphen, and dot"
            )
        
        return value
    
    def validate_sample_content(self, value):
        """Validate sample content."""
        if len(value) > 170:
            raise serializers.ValidationError("Sample content cannot exceed 170 characters")
        
        if len(value) < 15:
            raise serializers.ValidationError("Sample content must be at least 15 characters")
        
        return value


class SMSTemplateSerializer(serializers.ModelSerializer):
    """Serializer for SMS templates."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = SMSTemplate
        fields = [
            'id', 'name', 'category', 'language', 'message', 'variables',
            'provider_template_id', 'is_active', 'approval_status',
            'approved_at', 'approved_by_name', 'usage_count',
            'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'provider_template_id', 'approved_at', 'usage_count',
            'created_at', 'updated_at'
        ]
    
    def validate_message(self, value):
        """Validate message length."""
        if len(value) > 160:
            raise serializers.ValidationError("SMS message cannot exceed 160 characters")
        
        return value


class SMSMessageSerializer(serializers.ModelSerializer):
    """Serializer for SMS messages."""
    
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    sender_id_value = serializers.CharField(source='sender_id.sender_id', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    contact_name = serializers.CharField(source='base_message.conversation.contact.name', read_only=True)
    contact_phone = serializers.CharField(source='base_message.conversation.contact.phone_e164', read_only=True)
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'provider_name', 'sender_id_value', 'template_name',
            'provider_message_id', 'provider_request_id', 'status',
            'error_code', 'error_message', 'sent_at', 'delivered_at',
            'failed_at', 'cost_amount', 'cost_currency', 'contact_name',
            'contact_phone', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'provider_message_id', 'provider_request_id',
            'sent_at', 'delivered_at', 'failed_at', 'created_at', 'updated_at'
        ]


class SMSDeliveryReportSerializer(serializers.ModelSerializer):
    """Serializer for SMS delivery reports."""
    
    class Meta:
        model = SMSDeliveryReport
        fields = [
            'id', 'provider_request_id', 'provider_message_id',
            'dest_addr', 'status', 'error_code', 'error_message',
            'received_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'received_at']


class SMSBulkUploadSerializer(serializers.ModelSerializer):
    """Serializer for SMS bulk uploads."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    
    class Meta:
        model = SMSBulkUpload
        fields = [
            'id', 'file_name', 'file_size', 'status', 'total_rows',
            'processed_rows', 'successful_rows', 'failed_rows',
            'errors', 'campaign', 'campaign_name', 'created_at',
            'completed_at', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'file_size', 'total_rows', 'processed_rows',
            'successful_rows', 'failed_rows', 'errors', 'created_at',
            'completed_at'
        ]


class SMSScheduleSerializer(serializers.ModelSerializer):
    """Serializer for SMS schedules."""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    
    class Meta:
        model = SMSSchedule
        fields = [
            'id', 'name', 'description', 'frequency', 'start_date',
            'end_date', 'time_zone', 'custom_schedule', 'campaign',
            'campaign_name', 'is_active', 'last_run', 'next_run',
            'created_at', 'updated_at', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'last_run', 'next_run', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate schedule data."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        
        return data


class SMSBulkSendSerializer(serializers.Serializer):
    """Serializer for bulk SMS sending."""
    
    contacts = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of contacts with phone numbers and optional data"
    )
    message = serializers.CharField(max_length=160)
    sender_id = serializers.CharField(max_length=11)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    campaign_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_contacts(self, value):
        """Validate contacts list."""
        if not value:
            raise serializers.ValidationError("At least one contact is required")
        
        if len(value) > 1000:
            raise serializers.ValidationError("Cannot send to more than 1000 contacts at once")
        
        for i, contact in enumerate(value):
            if 'phone' not in contact:
                raise serializers.ValidationError(f"Contact {i+1} missing phone number")
            
            # Validate phone number format
            phone = str(contact['phone']).strip()
            if phone.startswith('+'):
                phone = phone[1:]
            
            if not phone.isdigit() or len(phone) < 10:
                raise serializers.ValidationError(f"Invalid phone number for contact {i+1}")
        
        return value


class SMSExcelUploadSerializer(serializers.Serializer):
    """Serializer for Excel file upload."""
    
    file = serializers.FileField()
    campaign_id = serializers.UUIDField(required=False, allow_null=True)
    template_id = serializers.UUIDField(required=False, allow_null=True)
    sender_id = serializers.CharField(max_length=11, required=False)
    
    def validate_file(self, value):
        """Validate uploaded file."""
        if not value.name.endswith(('.xlsx', '.xls')):
            raise serializers.ValidationError("File must be an Excel file (.xlsx or .xls)")
        
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        return value


class SMSBalanceSerializer(serializers.Serializer):
    """Serializer for SMS balance response."""
    
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    provider_name = serializers.CharField(max_length=100)


class SMSStatsSerializer(serializers.Serializer):
    """Serializer for SMS statistics."""
    
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    delivery_rate = serializers.FloatField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
