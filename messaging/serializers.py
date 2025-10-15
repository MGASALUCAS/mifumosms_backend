"""
Serializers for messaging models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Contact, Segment, Template, Conversation, Message, Attachment,
    Campaign, Flow
)
from django.utils import timezone

User = get_user_model()


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for Contact model."""

    is_opted_in = serializers.BooleanField(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    created_by_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id', 'name', 'phone_e164', 'email', 'attributes', 'tags',
            'opt_in_at', 'opt_out_at', 'opt_out_reason', 'is_active',
            'last_contacted_at', 'is_opted_in', 'created_by', 'created_by_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_contacted_at', 'created_by', 'created_by_id']


class ContactCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating contacts."""

    class Meta:
        model = Contact
        fields = [
            'name', 'phone_e164', 'email', 'attributes', 'tags'
        ]

    def validate_phone_e164(self, value):
        """Validate phone number format."""
        import phonenumbers
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError("Invalid phone number format.")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number format.")


class ContactBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing contacts from CSV."""

    csv_data = serializers.CharField()

    def validate_csv_data(self, value):
        """Validate CSV data format."""
        import csv
        from io import StringIO

        try:
            csv_reader = csv.DictReader(StringIO(value))
            required_fields = ['name', 'phone_e164']

            for row in csv_reader:
                for field in required_fields:
                    if field not in row or not row[field].strip():
                        raise serializers.ValidationError(f"Missing required field: {field}")

            return value
        except Exception as e:
            raise serializers.ValidationError(f"Invalid CSV format: {str(e)}")


class SegmentSerializer(serializers.ModelSerializer):
    """Serializer for Segment model."""

    class Meta:
        model = Segment
        fields = [
            'id', 'name', 'description', 'filter_json', 'contact_count',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'contact_count', 'created_at', 'updated_at']


class SegmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating segments."""

    class Meta:
        model = Segment
        fields = ['name', 'description', 'filter_json']

    def create(self, validated_data):
        """Create segment and update contact count."""
        segment = super().create(validated_data)
        segment.created_by = self.context['request'].user
        segment.save()
        segment.update_contact_count()
        return segment


class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for Template model."""

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'category', 'language', 'body_text', 'variables',
            'wa_template_name', 'wa_template_id', 'approved', 'approval_status',
            'usage_count', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


class TemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating templates."""

    class Meta:
        model = Template
        fields = [
            'name', 'category', 'language', 'body_text', 'variables'
        ]

    def create(self, validated_data):
        """Create template."""
        template = super().create(validated_data)
        template.created_by = self.context['request'].user
        template.save()
        return template


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""

    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone_e164', read_only=True)
    last_message_text = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'contact', 'contact_name', 'contact_phone', 'status', 'subject',
            'ai_summary', 'ai_suggestions', 'message_count', 'unread_count',
            'last_message_at', 'last_message_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'message_count', 'unread_count', 'created_at', 'updated_at']

    def get_last_message_text(self, obj):
        """Get the text of the last message."""
        last_message = obj.messages.first()
        return last_message.text if last_message else ''


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""

    contact_name = serializers.CharField(source='conversation.contact.name', read_only=True)
    cost_dollars = serializers.DecimalField(max_digits=10, decimal_places=6, read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'contact_name', 'direction', 'provider',
            'provider_message_id', 'text', 'media_url', 'media_type',
            'status', 'error_message', 'sent_at', 'delivered_at', 'read_at',
            'cost_micro', 'cost_dollars', 'template', 'template_variables',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'cost_dollars', 'created_at', 'updated_at',
            'sent_at', 'delivered_at', 'read_at'
        ]


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""

    class Meta:
        model = Message
        fields = [
            'conversation', 'text', 'media_url', 'media_type', 'template',
            'template_variables'
        ]

    def create(self, validated_data):
        """Create message."""
        message = super().create(validated_data)
        message.direction = 'out'
        message.created_by = self.context['request'].user
        message.save()
        return message


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Attachment model."""

    class Meta:
        model = Attachment
        fields = [
            'id', 'message', 'file_name', 'file_size', 'file_type',
            'file_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model."""

    template_name = serializers.CharField(source='template.name', read_only=True)
    segment_name = serializers.CharField(source='segment.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'template', 'template_name',
            'segment', 'segment_name', 'status', 'schedule_at',
            'started_at', 'completed_at', 'total_contacts', 'sent_count',
            'delivered_count', 'read_count', 'failed_count',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_contacts', 'sent_count', 'delivered_count',
            'read_count', 'failed_count', 'started_at', 'completed_at',
            'created_at', 'updated_at'
        ]


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns."""

    class Meta:
        model = Campaign
        fields = [
            'name', 'description', 'template', 'segment', 'schedule_at'
        ]

    def create(self, validated_data):
        """Create campaign."""
        campaign = super().create(validated_data)
        campaign.created_by = self.context['request'].user
        campaign.save()

        # Update total contacts count
        campaign.total_contacts = campaign.segment.contact_count
        campaign.save()

        return campaign


class FlowSerializer(serializers.ModelSerializer):
    """Serializer for Flow model."""

    class Meta:
        model = Flow
        fields = [
            'id', 'name', 'description', 'nodes', 'active', 'trigger_count',
            'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'trigger_count', 'created_at', 'updated_at']


class FlowCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating flows."""

    class Meta:
        model = Flow
        fields = ['name', 'description', 'nodes']

    def create(self, validated_data):
        """Create flow."""
        flow = super().create(validated_data)
        flow.created_by = self.context['request'].user
        flow.save()
        return flow


class ConversationSummarySerializer(serializers.Serializer):
    """Serializer for conversation summary."""

    conversation_id = serializers.UUIDField()
    summary = serializers.ListField(child=serializers.CharField())


class AISuggestionsSerializer(serializers.Serializer):
    """Serializer for AI suggestions."""

    conversation_id = serializers.UUIDField()
    suggestions = serializers.ListField(child=serializers.CharField())


# =============================================
# PURCHASE HISTORY SERIALIZERS
# =============================================

class PurchaseHistorySerializer(serializers.Serializer):
    """Serializer for purchase history display."""
    
    id = serializers.UUIDField(read_only=True)
    invoice_number = serializers.CharField(read_only=True)
    package_name = serializers.CharField(read_only=True)
    package_type = serializers.CharField(read_only=True)
    credits = serializers.IntegerField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    payment_method = serializers.CharField(read_only=True)
    payment_method_display = serializers.CharField(read_only=True)
    payment_reference = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True)


class PurchaseHistorySummarySerializer(serializers.Serializer):
    """Serializer for purchase history summary statistics."""
    
    total_purchases = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_credits = serializers.IntegerField(read_only=True)
    completed_purchases = serializers.IntegerField(read_only=True)
    pending_purchases = serializers.IntegerField(read_only=True)
    failed_purchases = serializers.IntegerField(read_only=True)
    average_purchase_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    last_purchase_date = serializers.DateTimeField(read_only=True, allow_null=True)


# =============================================
# CAMPAIGN SERIALIZERS
# =============================================

class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for campaign display."""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    campaign_type_display = serializers.CharField(source='get_campaign_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    delivery_rate = serializers.ReadOnlyField()
    read_rate = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    can_edit = serializers.ReadOnlyField()
    can_start = serializers.ReadOnlyField()
    can_pause = serializers.ReadOnlyField()
    can_cancel = serializers.ReadOnlyField()

    # Target information
    target_contact_count = serializers.SerializerMethodField()
    target_segment_names = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'description', 'campaign_type', 'campaign_type_display',
            'message_text', 'template', 'status', 'status_display',
            'scheduled_at', 'started_at', 'completed_at',
            'total_recipients', 'sent_count', 'delivered_count', 'read_count', 'failed_count',
            'estimated_cost', 'actual_cost',
            'progress_percentage', 'delivery_rate', 'read_rate',
            'is_active', 'can_edit', 'can_start', 'can_pause', 'can_cancel',
            'is_recurring', 'recurring_schedule', 'settings',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'target_contact_count', 'target_segment_names'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'total_recipients', 'sent_count', 'delivered_count', 'read_count', 'failed_count',
            'actual_cost', 'started_at', 'completed_at'
        ]

    def get_target_contact_count(self, obj):
        """Get count of target contacts."""
        return obj.target_contacts.count()

    def get_target_segment_names(self, obj):
        """Get names of target segments."""
        return list(obj.target_segments.values_list('name', flat=True))


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns."""
    target_contact_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    target_segment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Campaign
        fields = [
            'name', 'description', 'campaign_type', 'message_text', 'template',
            'scheduled_at', 'target_contact_ids', 'target_segment_ids',
            'target_criteria', 'settings', 'is_recurring', 'recurring_schedule'
        ]

    def validate_name(self, value):
        """Validate campaign name."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Campaign name must be at least 3 characters long")
        return value.strip()

    def validate_message_text(self, value):
        """Validate message text."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message text must be at least 10 characters long")
        return value.strip()

    def validate_scheduled_at(self, value):
        """Validate scheduled time."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value

    def validate(self, attrs):
        """Validate campaign data."""
        # Check if at least one targeting method is provided
        target_contact_ids = attrs.get('target_contact_ids', [])
        target_segment_ids = attrs.get('target_segment_ids', [])
        target_criteria = attrs.get('target_criteria', {})

        if not any([target_contact_ids, target_segment_ids, target_criteria]):
            raise serializers.ValidationError(
                "At least one targeting method must be specified (contacts, segments, or criteria)"
            )

        return attrs

    def create(self, validated_data):
        """Create campaign with targeting."""
        target_contact_ids = validated_data.pop('target_contact_ids', [])
        target_segment_ids = validated_data.pop('target_segment_ids', [])

        # Create campaign
        campaign = Campaign.objects.create(**validated_data)

        # Set targeting
        if target_contact_ids:
            contacts = Contact.objects.filter(
                id__in=target_contact_ids
            )
            campaign.target_contacts.set(contacts)

        if target_segment_ids:
            segments = Segment.objects.filter(
                id__in=target_segment_ids
            )
            campaign.target_segments.set(segments)

        # Update statistics
        campaign.update_statistics()

        return campaign


class CampaignUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating campaigns."""
    target_contact_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    target_segment_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Campaign
        fields = [
            'name', 'description', 'message_text', 'template',
            'scheduled_at', 'target_contact_ids', 'target_segment_ids',
            'target_criteria', 'settings', 'is_recurring', 'recurring_schedule'
        ]

    def validate_name(self, value):
        """Validate campaign name."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Campaign name must be at least 3 characters long")
        return value.strip()

    def validate_message_text(self, value):
        """Validate message text."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message text must be at least 10 characters long")
        return value.strip()

    def validate_scheduled_at(self, value):
        """Validate scheduled time."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value

    def update(self, instance, validated_data):
        """Update campaign with targeting."""
        # Check if campaign can be edited
        if not instance.can_edit:
            raise serializers.ValidationError(f"Cannot edit campaign in {instance.status} status")

        target_contact_ids = validated_data.pop('target_contact_ids', None)
        target_segment_ids = validated_data.pop('target_segment_ids', None)

        # Update campaign fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update targeting if provided
        if target_contact_ids is not None:
            contacts = Contact.objects.filter(
                id__in=target_contact_ids
            )
            instance.target_contacts.set(contacts)

        if target_segment_ids is not None:
            segments = Segment.objects.filter(
                id__in=target_segment_ids
            )
            instance.target_segments.set(segments)

        # Update statistics
        instance.update_statistics()
        instance.save()

        return instance
