"""
Messaging models for Mifumo WMS.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()

# Import SMS models
from .models_sms import *


class Contact(models.Model):
    """
    Represents a contact that can receive messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Owner information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contacts', null=True, blank=True)

    # Basic information
    name = models.CharField(max_length=255)
    phone_e164 = models.CharField(max_length=20, unique=True)  # E.164 format
    email = models.EmailField(blank=True)

    # Additional attributes (JSON field for flexibility)
    attributes = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)  # Array of tag strings

    # Opt-in/out tracking
    opt_in_at = models.DateTimeField(null=True, blank=True)
    opt_out_at = models.DateTimeField(null=True, blank=True)
    opt_out_reason = models.CharField(max_length=100, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_contacted_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        db_table = 'contacts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone_e164})"

    @property
    def is_opted_in(self):
        """Check if contact has opted in and not opted out."""
        return self.opt_in_at and not self.opt_out_at

    def opt_in(self):
        """Mark contact as opted in."""
        self.opt_in_at = timezone.now()
        self.opt_out_at = None
        self.opt_out_reason = ''
        self.save()

    def opt_out(self, reason=''):
        """Mark contact as opted out."""
        self.opt_out_at = timezone.now()
        self.opt_out_reason = reason
        self.save()


class Segment(models.Model):
    """
    Represents a saved contact filter for targeting campaigns.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Filter criteria (JSON field for flexible filtering)
    filter_json = models.JSONField(default=dict)

    # Statistics
    contact_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'segments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.contact_count} contacts)"

    def update_contact_count(self):
        """Update the contact count based on current filter."""
        from django.db.models import Q
        from django.db import connection

        # Build Q object from filter_json
        q = Q(is_active=True)

        if 'tags' in self.filter_json:
            tags = self.filter_json['tags']
            if tags:
                # Use icontains for SQLite compatibility
                q &= Q(tags__icontains=str(tags))

        if 'attributes' in self.filter_json:
            # For SQLite, we'll use a simpler approach
            if connection.vendor == 'sqlite':
                # For SQLite, we'll just count all contacts for now
                # In production, you might want to implement a more sophisticated approach
                pass
            else:
                for key, value in self.filter_json['attributes'].items():
                    q &= Q(attributes__contains={key: value})

        if 'opt_in_status' in self.filter_json:
            if self.filter_json['opt_in_status'] == 'opted_in':
                q &= Q(opt_in_at__isnull=False, opt_out_at__isnull=True)
            elif self.filter_json['opt_in_status'] == 'opted_out':
                q &= Q(opt_out_at__isnull=False)

        self.contact_count = Contact.objects.filter(q).count()
        self.save(update_fields=['contact_count'])


class Template(models.Model):
    """
    Represents a message template for campaigns.
    """
    CATEGORY_CHOICES = [
        ('AUTHENTICATION', 'Authentication'),
        ('MARKETING', 'Marketing'),
        ('UTILITY', 'Utility'),
        ('OTP', 'One-time password'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('sw', 'Swahili'),
        ('fr', 'French'),
        ('ar', 'Arabic'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Template details
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    body_text = models.TextField()

    # Variables (JSON array of variable names)
    variables = models.JSONField(default=list, blank=True)

    # WhatsApp specific
    wa_template_name = models.CharField(max_length=100, blank=True)
    wa_template_id = models.CharField(max_length=100, blank=True)
    approved = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=20, default='pending')  # pending, approved, rejected

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'templates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Conversation(models.Model):
    """
    Represents a conversation thread with a contact.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='conversations')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='conversations')

    # Conversation details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    subject = models.CharField(max_length=255, blank=True)

    # AI assistance
    ai_summary = models.TextField(blank=True)
    ai_suggestions = models.JSONField(default=list, blank=True)

    # Statistics
    message_count = models.PositiveIntegerField(default=0)
    unread_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'conversations'
        unique_together = ['tenant', 'contact']
        ordering = ['-last_message_at', '-created_at']

    def __str__(self):
        return f"Conversation with {self.contact.name}"

    def close(self):
        """Close the conversation."""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()

    def archive(self):
        """Archive the conversation."""
        self.status = 'archived'
        self.save()


class Message(models.Model):
    """
    Represents a message in a conversation.
    """
    DIRECTION_CHOICES = [
        ('in', 'Inbound'),
        ('out', 'Outbound'),
    ]

    PROVIDER_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('telegram', 'Telegram'),
    ]

    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)

    # Message details
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default='whatsapp')
    provider_message_id = models.CharField(max_length=100, blank=True)

    # Content
    text = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    media_type = models.CharField(max_length=50, blank=True)  # image, video, audio, document

    # Recipient information
    recipient_number = models.CharField(max_length=20, blank=True, help_text="Phone number of the recipient")

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    error_message = models.TextField(blank=True)

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Cost tracking (in micro-units for precision)
    cost_micro = models.PositiveIntegerField(default=0)  # Cost in micro-units (e.g., cents * 10000)

    # Template reference
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)
    template_variables = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        if self.conversation and self.conversation.contact:
            return f"{self.direction} message to {self.conversation.contact.name} ({self.conversation.contact.phone_number})"
        elif self.conversation:
            return f"{self.direction} message in conversation {self.conversation.id}"
        elif self.recipient_number:
            return f"{self.direction} message to {self.recipient_number}"
        else:
            return f"{self.direction} message (no conversation)"

    @property
    def cost_dollars(self):
        """Return cost in dollars."""
        return self.cost_micro / 1000000

    def mark_sent(self):
        """Mark message as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()

    def mark_delivered(self):
        """Mark message as delivered."""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()

    def mark_read(self):
        """Mark message as read."""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()

    def mark_failed(self, error_message=''):
        """Mark message as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save()


class Attachment(models.Model):
    """
    Represents file attachments for messages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')

    # File details
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=100)
    file_url = models.URLField()

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attachments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Attachment: {self.file_name}"


class Campaign(models.Model):
    """
    Smart campaign model with user-specific tracking and management.
    """
    CAMPAIGN_TYPES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('mixed', 'Mixed'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_campaigns')

    # Basic campaign info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, default='sms')

    # Content
    message_text = models.TextField()
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True)

    # Targeting
    target_segments = models.ManyToManyField(Segment, blank=True, related_name='campaigns')
    target_contacts = models.ManyToManyField(Contact, blank=True, related_name='campaigns')
    target_criteria = models.JSONField(default=dict, blank=True)  # Advanced targeting

    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Statistics (computed fields)
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    read_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)

    # Cost tracking
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Settings
    settings = models.JSONField(default=dict, blank=True)  # Campaign-specific settings
    is_recurring = models.BooleanField(default=False)
    recurring_schedule = models.JSONField(default=dict, blank=True)  # For recurring campaigns

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by']),
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['campaign_type', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def progress_percentage(self):
        """Calculate campaign progress percentage."""
        if self.total_recipients == 0:
            return 0
        return min(100, int((self.sent_count / self.total_recipients) * 100))

    @property
    def delivery_rate(self):
        """Calculate delivery rate percentage."""
        if self.sent_count == 0:
            return 0
        return round((self.delivered_count / self.sent_count) * 100, 2)

    @property
    def read_rate(self):
        """Calculate read rate percentage."""
        if self.delivered_count == 0:
            return 0
        return round((self.read_count / self.delivered_count) * 100, 2)

    @property
    def is_active(self):
        """Check if campaign is currently active."""
        return self.status in ['running', 'scheduled']

    @property
    def can_edit(self):
        """Check if campaign can be edited."""
        return self.status in ['draft', 'scheduled']

    @property
    def can_start(self):
        """Check if campaign can be started."""
        return self.status in ['draft', 'scheduled', 'paused']

    @property
    def can_pause(self):
        """Check if campaign can be paused."""
        return self.status == 'running'

    @property
    def can_cancel(self):
        """Check if campaign can be cancelled."""
        return self.status in ['draft', 'scheduled', 'running', 'paused']

    def calculate_recipients(self):
        """Calculate total recipients based on targeting."""
        if self.target_contacts.exists():
            return self.target_contacts.filter(is_active=True).count()

        if self.target_segments.exists():
            total = 0
            for segment in self.target_segments.all():
                total += segment.contact_count
            return total

        # If no specific targeting, use tenant contacts
        return self.tenant.contacts.filter(is_active=True).count()

    def update_statistics(self):
        """Update campaign statistics."""
        self.total_recipients = self.calculate_recipients()
        self.save(update_fields=['total_recipients'])

    def start_campaign(self):
        """Start the campaign."""
        if not self.can_start:
            raise ValueError(f"Cannot start campaign in {self.status} status")

        self.status = 'running'
        self.started_at = timezone.now()
        self.update_statistics()
        self.save()

    def pause_campaign(self):
        """Pause the campaign."""
        if not self.can_pause:
            raise ValueError(f"Cannot pause campaign in {self.status} status")

        self.status = 'paused'
        self.save()

    def complete_campaign(self):
        """Mark campaign as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def cancel_campaign(self):
        """Cancel the campaign."""
        if not self.can_cancel:
            raise ValueError(f"Cannot cancel campaign in {self.status} status")

        self.status = 'cancelled'
        self.completed_at = timezone.now()
        self.save()

    def complete(self):
        """Mark campaign as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def pause(self):
        """Pause the campaign."""
        self.status = 'paused'
        self.save()

    def cancel(self):
        """Cancel the campaign."""
        self.status = 'cancelled'
        self.save()


class Flow(models.Model):
    """
    Represents an automated flow for handling conversations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='flows')

    # Flow details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    nodes = models.JSONField(default=list)  # Array of flow nodes
    active = models.BooleanField(default=False)

    # Statistics
    trigger_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'flows'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({'Active' if self.active else 'Inactive'})"

    def activate(self):
        """Activate the flow."""
        self.active = True
        self.save()

    def deactivate(self):
        """Deactivate the flow."""
        self.active = False
        self.save()
