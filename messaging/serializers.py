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
        """Validate phone number format and uniqueness per tenant."""
        import phonenumbers
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError("Invalid phone number format.")
            formatted_phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

            # Check for duplicate phone number within the same tenant
            user = self.context['request'].user
            tenant = getattr(user, 'tenant', None)
            if tenant and Contact.objects.filter(tenant=tenant, phone_e164=formatted_phone).exists():
                raise serializers.ValidationError("A contact with this phone number already exists in your contact list.")

            return formatted_phone
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Invalid phone number format.")


class ContactBulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing contacts from CSV/Excel or phone contacts."""

    # CSV/Excel import
    csv_data = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True)
    
    # Phone contact import
    contacts = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        min_length=1,
        max_length=1000  # Increased limit for bulk operations
    )
    
    # Import options
    import_type = serializers.ChoiceField(
        choices=['csv', 'excel', 'phone_contacts'],
        default='csv'
    )
    skip_duplicates = serializers.BooleanField(default=True)
    update_existing = serializers.BooleanField(default=False)

    def validate(self, attrs):
        """Validate import data based on type."""
        import_type = attrs.get('import_type', 'csv')
        
        if import_type in ['csv', 'excel']:
            if not attrs.get('csv_data') and not attrs.get('file'):
                raise serializers.ValidationError(
                    f"For {import_type} import, either csv_data or file must be provided"
                )
        elif import_type == 'phone_contacts':
            if not attrs.get('contacts'):
                raise serializers.ValidationError(
                    "For phone contacts import, contacts data must be provided"
                )
        
        return attrs

    def validate_csv_data(self, value):
        """Validate CSV data format."""
        if not value:
            return value
            
        import csv
        from io import StringIO

        try:
            csv_reader = csv.DictReader(StringIO(value))
            required_fields = ['name', 'phone']
            optional_fields = ['local_number', 'email']

            for row in csv_reader:
                # Check required fields
                for field in required_fields:
                    if field not in row or not row[field].strip():
                        raise serializers.ValidationError(f"Missing required field: {field}")
                
                # Validate phone number format
                phone = row.get('phone', '').strip()
                if phone and not self._is_valid_phone_format(phone):
                    raise serializers.ValidationError(f"Invalid phone number format: {phone}")
                
                # If local_number is provided, validate it matches phone (optional validation)
                local_number = row.get('local_number', '').strip()
                if local_number and phone:
                    # Normalize both numbers for comparison
                    phone_normalized = phone.replace('+255', '').replace('255', '').lstrip('0')
                    local_normalized = local_number.lstrip('0')
                    if phone_normalized != local_normalized:
                        # This is just a warning, not an error
                        pass  # We'll allow it but log it

            return value
        except Exception as e:
            raise serializers.ValidationError(f"Invalid CSV format: {str(e)}")
    
    def _is_valid_phone_format(self, phone):
        """Check if phone number is in valid format."""
        import re
        # Accept formats: +255XXXXXXXXX, 255XXXXXXXXX, 0XXXXXXXXX, XXXXXXXXX
        patterns = [
            r'^\+255[0-9]{9}$',  # +255XXXXXXXXX
            r'^255[0-9]{9}$',    # 255XXXXXXXXX
            r'^0[0-9]{9}$',      # 0XXXXXXXXX
            r'^[0-9]{9}$'        # XXXXXXXXX (local format)
        ]
        return any(re.match(pattern, phone) for pattern in patterns)

    def validate_contacts(self, value):
        """Validate phone contact data."""
        if not value:
            return value
            
        validated_contacts = []

        for i, contact in enumerate(value):
            # Validate required fields
            if not contact.get('full_name') and not contact.get('phone') and not contact.get('email'):
                raise serializers.ValidationError(f"Contact {i+1}: At least one field (name, phone, or email) is required")

            # Normalize phone number if provided
            phone = contact.get('phone', '').strip()
            if phone:
                phone = self._normalize_phone(phone)
                if not phone:
                    raise serializers.ValidationError(f"Contact {i+1}: Invalid phone number format")

            validated_contact = {
                'full_name': contact.get('full_name', '').strip(),
                'phone': phone,
                'email': contact.get('email', '').strip() or None,
            }

            # Only include contacts that have at least name or phone
            if validated_contact['full_name'] or validated_contact['phone']:
                validated_contacts.append(validated_contact)

        if not validated_contacts:
            raise serializers.ValidationError("No valid contacts found")

        return validated_contacts

    def _normalize_phone(self, phone):
        """Normalize phone number to E.164 format."""
        import re

        if not phone:
            return ""

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        # Handle Tanzanian numbers
        if digits.startswith('255') and len(digits) == 12:
            return f"+{digits}"
        elif digits.startswith('0') and len(digits) == 10:
            return f"+255{digits[1:]}"
        elif digits.startswith('+'):
            return phone  # Already in correct format
        elif len(digits) >= 10:
            return f"+{digits}"

        return phone  # Return original if can't normalize


class ContactImportSerializer(serializers.Serializer):
    """Serializer for importing contacts from phone contact picker."""

    contacts = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=100  # Limit to prevent abuse
    )

    def validate_contacts(self, value):
        """Validate contact data from phone picker."""
        validated_contacts = []

        for i, contact in enumerate(value):
            # Validate required fields
            if not contact.get('full_name') and not contact.get('phone') and not contact.get('email'):
                raise serializers.ValidationError(f"Contact {i+1}: At least one field (name, phone, or email) is required")

            # Normalize phone number if provided
            phone = contact.get('phone', '').strip()
            if phone:
                phone = self._normalize_phone(phone)
                if not phone:
                    raise serializers.ValidationError(f"Contact {i+1}: Invalid phone number format")

            validated_contact = {
                'full_name': contact.get('full_name', '').strip(),
                'phone': phone,
                'email': contact.get('email', '').strip() or None,
            }

            # Only include contacts that have at least name or phone
            if validated_contact['full_name'] or validated_contact['phone']:
                validated_contacts.append(validated_contact)

        if not validated_contacts:
            raise serializers.ValidationError("No valid contacts found")

        return validated_contacts

    def _normalize_phone(self, phone):
        """Normalize phone number to E.164 format."""
        import re

        if not phone:
            return ""

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        # Handle Tanzanian numbers
        if digits.startswith('255') and len(digits) == 12:
            return f"+{digits}"
        elif digits.startswith('0') and len(digits) == 10:
            return f"+255{digits[1:]}"
        elif digits.startswith('+'):
            return phone  # Already in correct format
        elif len(digits) >= 10:
            return f"+{digits}"

        return phone  # Return original if can't normalize


class ContactBulkEditSerializer(serializers.Serializer):
    """Serializer for bulk editing contacts."""

    contact_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100  # Limit to prevent abuse
    )
    updates = serializers.DictField()

    def validate_contact_ids(self, value):
        """Validate contact IDs exist and belong to user."""
        if not value:
            raise serializers.ValidationError("At least one contact ID is required")
        
        # Check if all contact IDs are unique
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate contact IDs are not allowed")
        
        return value

    def validate_updates(self, value):
        """Validate update data."""
        if not value:
            raise serializers.ValidationError("Updates cannot be empty")
        
        # Allowed fields for bulk update
        allowed_fields = ['name', 'email', 'tags', 'attributes', 'is_active']
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(f"Field '{field}' is not allowed for bulk update")
        
        return value


class ContactBulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk deleting contacts."""

    contact_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100  # Limit to prevent abuse
    )

    def validate_contact_ids(self, value):
        """Validate contact IDs exist and belong to user."""
        if not value:
            raise serializers.ValidationError("At least one contact ID is required")
        
        # Check if all contact IDs are unique
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate contact IDs are not allowed")
        
        return value


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
    
    # Display fields
    status_display = serializers.ReadOnlyField()
    category_display = serializers.ReadOnlyField()
    language_display = serializers.ReadOnlyField()
    channel_display = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    # Computed fields
    variables_count = serializers.SerializerMethodField()
    last_used_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'category', 'category_display', 'language', 'language_display',
            'channel', 'channel_display', 'body_text', 'description', 'variables',
            'variables_count', 'status', 'status_display', 'approved', 'approval_status',
            'is_favorite', 'wa_template_name', 'wa_template_id', 'usage_count',
            'last_used_at', 'last_used_display', 'created_at', 'updated_at',
            'created_by', 'created_by_name'
        ]
        read_only_fields = [
            'id', 'variables', 'variables_count', 'usage_count', 'last_used_at',
            'last_used_display', 'created_at', 'updated_at', 'created_by', 'created_by_name'
        ]

    def get_created_by_name(self, obj):
        """Get creator's name."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return "Unknown"

    def get_variables_count(self, obj):
        """Get count of variables."""
        return len(obj.variables) if obj.variables else 0

    def get_last_used_display(self, obj):
        """Get formatted last used date."""
        if obj.last_used_at:
            return obj.last_used_at.strftime('%Y-%m-%d')
        return "Never used"


class TemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating templates."""
    
    class Meta:
        model = Template
        fields = [
            'name', 'category', 'language', 'channel', 'body_text', 'description',
            'status', 'is_favorite'
        ]

    def validate_name(self, value):
        """Validate template name uniqueness within tenant."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            tenant = getattr(request.user, 'tenant', None)
            channel = self.initial_data.get('channel', 'sms')
            
            existing = Template.objects.filter(
                name=value,
                tenant=tenant,
                channel=channel
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError(
                    f"A template with this name already exists for {channel} channel."
                )
        return value

    def validate_body_text(self, value):
        """Validate body text and extract variables."""
        if not value.strip():
            raise serializers.ValidationError("Body text cannot be empty.")
        
        # Check for valid variable format
        import re
        invalid_vars = re.findall(r'\{\{[^}]+\}\}', value)
        if invalid_vars:
            raise serializers.ValidationError(
                f"Invalid variable format found: {invalid_vars}. "
                "Variables should be in format {{variable_name}}."
            )
        
        return value

    def create(self, validated_data):
        """Create template."""
        template = super().create(validated_data)
        template.created_by = self.context['request'].user
        template.tenant = getattr(self.context['request'].user, 'tenant', None)
        template.save()
        return template


class TemplateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating templates."""
    
    class Meta:
        model = Template
        fields = [
            'name', 'category', 'language', 'channel', 'body_text', 'description',
            'status', 'approved', 'approval_status', 'is_favorite',
            'wa_template_name', 'wa_template_id'
        ]

    def validate_name(self, value):
        """Validate template name uniqueness within tenant."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            tenant = getattr(request.user, 'tenant', None)
            channel = self.initial_data.get('channel', self.instance.channel if self.instance else 'sms')
            
            existing = Template.objects.filter(
                name=value,
                tenant=tenant,
                channel=channel
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError(
                    f"A template with this name already exists for {channel} channel."
                )
        return value

    def validate_body_text(self, value):
        """Validate body text and extract variables."""
        if not value.strip():
            raise serializers.ValidationError("Body text cannot be empty.")
        
        # Check for valid variable format
        import re
        invalid_vars = re.findall(r'\{\{[^}]+\}\}', value)
        if invalid_vars:
            raise serializers.ValidationError(
                f"Invalid variable format found: {invalid_vars}. "
                "Variables should be in format {{variable_name}}."
            )
        
        return value


class TemplateDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for template view."""
    
    # Display fields
    status_display = serializers.ReadOnlyField()
    category_display = serializers.ReadOnlyField()
    language_display = serializers.ReadOnlyField()
    channel_display = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    # Computed fields
    variables_count = serializers.SerializerMethodField()
    last_used_display = serializers.SerializerMethodField()
    formatted_body_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'category', 'category_display', 'language', 'language_display',
            'channel', 'channel_display', 'body_text', 'formatted_body_text', 'description',
            'variables', 'variables_count', 'status', 'status_display', 'approved',
            'approval_status', 'is_favorite', 'wa_template_name', 'wa_template_id',
            'usage_count', 'last_used_at', 'last_used_display', 'created_at', 'updated_at',
            'created_by', 'created_by_name'
        ]

    def get_created_by_name(self, obj):
        """Get creator's name."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.email
        return "Unknown"

    def get_variables_count(self, obj):
        """Get count of variables."""
        return len(obj.variables) if obj.variables else 0

    def get_last_used_display(self, obj):
        """Get formatted last used date."""
        if obj.last_used_at:
            return obj.last_used_at.strftime('%Y-%m-%d')
        return "Never used"

    def get_formatted_body_text(self, obj):
        """Get formatted body text with highlighted variables."""
        import re
        text = obj.body_text
        
        # Highlight variables with a different color or format
        def replace_var(match):
            var_name = match.group(1)
            return f"<span class='variable'>{match.group(0)}</span>"
        
        formatted_text = re.sub(r'\{\{(\w+)\}\}', replace_var, text)
        return formatted_text


class TemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template list view."""
    
    # Display fields
    category_display = serializers.ReadOnlyField()
    language_display = serializers.ReadOnlyField()
    channel_display = serializers.ReadOnlyField()
    
    # Computed fields
    variables_count = serializers.SerializerMethodField()
    last_used_display = serializers.SerializerMethodField()
    preview_text = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'category', 'category_display', 'language', 'language_display',
            'channel', 'channel_display', 'preview_text', 'variables_count',
            'status', 'approved', 'is_favorite', 'usage_count', 'last_used_display',
            'created_at', 'updated_at'
        ]

    def get_variables_count(self, obj):
        """Get count of variables."""
        return len(obj.variables) if obj.variables else 0

    def get_last_used_display(self, obj):
        """Get formatted last used date."""
        if obj.last_used_at:
            return obj.last_used_at.strftime('%Y-%m-%d')
        return "Never used"

    def get_preview_text(self, obj):
        """Get preview of body text."""
        preview = obj.body_text[:100]
        if len(obj.body_text) > 100:
            preview += "..."
        return preview


class TemplateFilterSerializer(serializers.Serializer):
    """Serializer for template filtering options."""
    
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=Template.CATEGORY_CHOICES),
        required=False
    )
    languages = serializers.ListField(
        child=serializers.ChoiceField(choices=Template.LANGUAGE_CHOICES),
        required=False
    )
    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=Template.CHANNEL_CHOICES),
        required=False
    )
    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=Template.STATUS_CHOICES),
        required=False
    )
    search = serializers.CharField(required=False, allow_blank=True)
    favorites_only = serializers.BooleanField(default=False)
    approved_only = serializers.BooleanField(default=False)


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
