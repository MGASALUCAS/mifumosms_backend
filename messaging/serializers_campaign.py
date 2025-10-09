"""
Campaign serializers for Mifumo WMS.
Smart and simple serialization for campaign management.
"""
from rest_framework import serializers
from .models_campaign import Campaign, CampaignMessage, CampaignAnalytics
from .models import Contact, Segment, Template


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
                id__in=target_contact_ids,
                tenant=campaign.tenant
            )
            campaign.target_contacts.set(contacts)
        
        if target_segment_ids:
            segments = Segment.objects.filter(
                id__in=target_segment_ids,
                tenant=campaign.tenant
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
                id__in=target_contact_ids,
                tenant=instance.tenant
            )
            instance.target_contacts.set(contacts)
        
        if target_segment_ids is not None:
            segments = Segment.objects.filter(
                id__in=target_segment_ids,
                tenant=instance.tenant
            )
            instance.target_segments.set(segments)
        
        # Update statistics
        instance.update_statistics()
        instance.save()
        
        return instance


class CampaignMessageSerializer(serializers.ModelSerializer):
    """Serializer for campaign messages."""
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_phone = serializers.CharField(source='contact.phone_e164', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CampaignMessage
        fields = [
            'id', 'contact', 'contact_name', 'contact_phone',
            'status', 'status_display', 'sent_at', 'delivered_at', 'read_at', 'failed_at',
            'error_message', 'retry_count', 'cost', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CampaignAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for campaign analytics."""
    
    class Meta:
        model = CampaignAnalytics
        fields = [
            'id', 'date', 'sent_count', 'delivered_count', 'read_count', 'failed_count',
            'cost', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CampaignSummarySerializer(serializers.Serializer):
    """Serializer for campaign summary."""
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    completed_campaigns = serializers.IntegerField()
    total_recipients = serializers.IntegerField()
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_read = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    recent_campaigns = CampaignSerializer(many=True)
