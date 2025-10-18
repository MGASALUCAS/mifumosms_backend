"""
SMS Serializers for Beem Integration

This module provides serializers for SMS functionality with Beem Africa integration.
It includes validation, data transformation, and error handling for SMS operations.
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
import re

from .models_sms import SMSProvider, SMSSenderID, SMSTemplate, SMSMessage, SMSDeliveryReport


class SMSSendSerializer(serializers.Serializer):
    """
    Serializer for sending single SMS via Beem
    """
    message = serializers.CharField(
        max_length=160,
        help_text="SMS message content (max 160 characters)"
    )
    recipients = serializers.ListField(
        child=serializers.CharField(max_length=20),
        min_length=1,
        max_length=1000,
        help_text="List of recipient phone numbers in international format"
    )
    sender_id = serializers.CharField(
        max_length=11,
        required=True,
        help_text="Sender ID (max 11 characters) - Must be registered and active"
    )
    template_id = serializers.UUIDField(
        required=False,
        help_text="SMS template ID to use"
    )
    schedule_time = serializers.DateTimeField(
        required=False,
        help_text="When to send the message (ISO format)"
    )
    encoding = serializers.IntegerField(
        default=0,
        min_value=0,
        max_value=1,
        help_text="Message encoding (0=GSM7, 1=UCS2)"
    )
    
    def validate_message(self, value):
        """Validate message content"""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        
        # Check for special characters that might cause issues
        if len(value) > 160:
            raise serializers.ValidationError("Message too long (max 160 characters)")
        
        # Check for Unicode characters and provide helpful message
        has_unicode = any(ord(char) > 127 for char in value)
        if has_unicode:
            # Log that Unicode characters were detected
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Unicode characters detected in message: {value[:50]}...")
        
        return value.strip()
    
    def validate_recipients(self, value):
        """Validate recipient phone numbers"""
        if not value:
            raise serializers.ValidationError("At least one recipient is required")
        
        # Basic phone number validation
        phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        invalid_numbers = []
        
        for phone in value:
            # Remove spaces and dashes
            cleaned = re.sub(r'[\s\-]', '', phone)
            if not phone_pattern.match(cleaned):
                invalid_numbers.append(phone)
        
        if invalid_numbers:
            raise serializers.ValidationError(
                f"Invalid phone numbers: {', '.join(invalid_numbers)}"
            )
        
        return value
    
    def validate_sender_id(self, value):
        """Validate sender ID"""
        if value:
            # Remove spaces and special characters
            cleaned = re.sub(r'[^a-zA-Z0-9]', '', value)
            if len(cleaned) > 11:
                raise serializers.ValidationError("Sender ID too long (max 11 characters)")
            if len(cleaned) < 3:
                raise serializers.ValidationError("Sender ID too short (min 3 characters)")
        return value
    
    def validate_schedule_time(self, value):
        """Validate schedule time"""
        if value:
            now = timezone.now()
            if value <= now:
                raise serializers.ValidationError("Schedule time must be in the future")
            
            # Check if too far in the future (max 1 year)
            max_future = now + timezone.timedelta(days=365)
            if value > max_future:
                raise serializers.ValidationError("Schedule time cannot be more than 1 year in the future")
        
        return value


class SMSBulkSendSerializer(serializers.Serializer):
    """
    Serializer for sending bulk SMS via Beem
    """
    messages = serializers.ListField(
        child=SMSSendSerializer(),
        min_length=1,
        max_length=100,
        help_text="List of SMS messages to send"
    )
    schedule_time = serializers.DateTimeField(
        required=False,
        help_text="When to send all messages (ISO format)"
    )
    
    def validate_messages(self, value):
        """Validate messages list"""
        if not value:
            raise serializers.ValidationError("At least one message is required")
        
        # Check total recipient count
        total_recipients = sum(len(msg.get('recipients', [])) for msg in value)
        if total_recipients > 10000:
            raise serializers.ValidationError("Total recipients cannot exceed 10,000")
        
        return value


class SMSScheduleSerializer(serializers.Serializer):
    """
    Serializer for scheduling SMS messages
    """
    message = serializers.CharField(max_length=160)
    recipients = serializers.ListField(
        child=serializers.CharField(max_length=20),
        min_length=1
    )
    sender_id = serializers.CharField(max_length=11, required=False)
    schedule_time = serializers.DateTimeField()
    frequency = serializers.ChoiceField(
        choices=['once', 'daily', 'weekly', 'monthly'],
        default='once'
    )
    end_date = serializers.DateTimeField(required=False)
    
    def validate_schedule_time(self, value):
        """Validate schedule time"""
        now = timezone.now()
        if value <= now:
            raise serializers.ValidationError("Schedule time must be in the future")
        return value


class SMSMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for SMS message model
    """
    base_message_id = serializers.UUIDField(source='base_message.id', read_only=True)
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    sender_id_value = serializers.CharField(source='sender_id.sender_id', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = SMSMessage
        fields = [
            'id', 'base_message_id', 'provider_name', 'sender_id_value',
            'template_name', 'status', 'error_code', 'error_message',
            'sent_at', 'delivered_at', 'failed_at', 'cost_amount',
            'cost_currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SMSDeliveryReportSerializer(serializers.ModelSerializer):
    """
    Serializer for SMS delivery reports
    """
    message_id = serializers.UUIDField(source='sms_message.id', read_only=True)
    
    class Meta:
        model = SMSDeliveryReport
        fields = [
            'id', 'message_id', 'provider_request_id', 'provider_message_id',
            'dest_addr', 'status', 'error_code', 'error_message',
            'received_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'received_at']


class SMSProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for SMS provider configuration
    """
    class Meta:
        model = SMSProvider
        fields = [
            'id', 'name', 'provider_type', 'is_active', 'is_default',
            'api_url', 'webhook_url', 'cost_per_sms', 'currency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SMSSenderIDSerializer(serializers.ModelSerializer):
    """
    Serializer for SMS sender ID
    """
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    
    class Meta:
        model = SMSSenderID
        fields = [
            'id', 'sender_id', 'sample_content', 'status',
            'provider_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SMSTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for SMS templates
    """
    class Meta:
        model = SMSTemplate
        fields = [
            'id', 'name', 'category', 'language', 'message',
            'variables', 'is_active', 'approval_status', 'usage_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BeemConnectionTestSerializer(serializers.Serializer):
    """
    Serializer for Beem connection test
    """
    test_message = serializers.CharField(
        max_length=160,
        default="Test message from Mifumo WMS",
        help_text="Test message to send"
    )
    test_recipient = serializers.CharField(
        max_length=20,
        default="255700000000",
        help_text="Test recipient phone number"
    )


class PhoneValidationSerializer(serializers.Serializer):
    """
    Serializer for phone number validation
    """
    phone_number = serializers.CharField(
        max_length=20,
        help_text="Phone number to validate"
    )
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if not value:
            raise serializers.ValidationError("Phone number is required")
        
        # Remove spaces, dashes, and parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', value)
        
        # Check if it starts with + or country code
        if not (cleaned.startswith('+') or cleaned.startswith('255')):
            raise serializers.ValidationError(
                "Phone number must include country code (e.g., +255 or 255)"
            )
        
        # Basic length validation
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise serializers.ValidationError(
                "Phone number must be between 10 and 15 digits"
            )
        
        return value
