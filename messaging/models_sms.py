"""
SMS-specific models for Mifumo WMS.
Extends the existing messaging system with SMS capabilities.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from tenants.models import Tenant
import uuid
import json

User = get_user_model()


class SMSProvider(models.Model):
    """
    Represents an SMS provider configuration (Beem, Twilio, etc.)
    """
    PROVIDER_CHOICES = [
        ('beem', 'Beem Africa'),
        ('twilio', 'Twilio'),
        ('africas_talking', 'Africa\'s Talking'),
        ('custom', 'Custom Provider'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_providers')

    # Provider details
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # API Configuration
    api_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    api_url = models.URLField()
    webhook_url = models.URLField(blank=True)

    # Provider-specific settings
    settings = models.JSONField(default=dict, blank=True)  # Custom settings per provider

    # Cost configuration
    cost_per_sms = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    currency = models.CharField(
        max_length=10, 
        default='USD',
        help_text="Currency code (e.g., USD, EUR, TZS, KES, NGN)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sms_providers'
        unique_together = ['tenant', 'name']
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f"{self.name} ({self.provider_type})"


class SMSSenderID(models.Model):
    """
    Represents a registered SMS sender ID for a tenant.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_sender_ids')
    provider = models.ForeignKey(SMSProvider, on_delete=models.CASCADE, related_name='sender_ids')

    # Sender ID details
    sender_id = models.CharField(max_length=11)  # Max 11 characters as per Beem
    sample_content = models.TextField(max_length=170)  # Max 170 characters
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Provider-specific data
    provider_sender_id = models.CharField(max_length=100, blank=True)  # ID from provider
    provider_data = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sms_sender_ids'
        unique_together = ['tenant', 'sender_id']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender_id} ({self.status})"


class SMSTemplate(models.Model):
    """
    SMS-specific templates that extend the base Template model.
    """
    CATEGORY_CHOICES = [
        ('PROMOTIONAL', 'Promotional'),
        ('TRANSACTIONAL', 'Transactional'),
        ('OTP', 'One-time Password'),
        ('ALERT', 'Alert'),
        ('NOTIFICATION', 'Notification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_templates')

    # Template details
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    language = models.CharField(max_length=5, default='en')
    message = models.TextField(max_length=160)  # Standard SMS length

    # Variables (JSON array of variable names)
    variables = models.JSONField(default=list, blank=True)

    # Provider-specific data
    provider_template_id = models.CharField(max_length=100, blank=True)
    provider_data = models.JSONField(default=dict, blank=True)

    # Status and approval
    is_active = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_sms_templates')

    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sms_templates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.category})"


class SMSMessage(models.Model):
    """
    SMS-specific message tracking that extends the base Message model.
    """
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('undelivered', 'Undelivered'),
        ('pending', 'Pending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_messages')

    # Reference to base message
    base_message = models.OneToOneField('messaging.Message', on_delete=models.CASCADE, related_name='sms_message')

    # SMS-specific details
    provider = models.ForeignKey(SMSProvider, on_delete=models.CASCADE, related_name='messages')
    sender_id = models.ForeignKey(SMSSenderID, on_delete=models.CASCADE, related_name='messages')
    template = models.ForeignKey(SMSTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    # Provider tracking
    provider_message_id = models.CharField(max_length=100, blank=True)
    provider_request_id = models.CharField(max_length=100, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    error_code = models.CharField(max_length=10, blank=True)
    error_message = models.TextField(blank=True)

    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    # Cost tracking
    cost_amount = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    cost_currency = models.CharField(max_length=3, default='USD')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sms_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS {self.id} - {self.status}"


class SMSDeliveryReport(models.Model):
    """
    Tracks delivery reports from SMS providers.
    """
    STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('undelivered', 'Undelivered'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_delivery_reports')
    sms_message = models.ForeignKey(SMSMessage, on_delete=models.CASCADE, related_name='delivery_reports')

    # Provider data
    provider_request_id = models.CharField(max_length=100)
    provider_message_id = models.CharField(max_length=100, blank=True)
    dest_addr = models.CharField(max_length=20)  # Phone number

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    error_code = models.CharField(max_length=10, blank=True)
    error_message = models.TextField(blank=True)

    # Provider response
    provider_response = models.JSONField(default=dict, blank=True)

    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'sms_delivery_reports'
        ordering = ['-received_at']

    def __str__(self):
        return f"Delivery Report {self.id} - {self.status}"


class SMSBulkUpload(models.Model):
    """
    Tracks bulk SMS uploads from Excel files.
    """
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_bulk_uploads')

    # Upload details
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveIntegerField()

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    successful_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)

    # Error tracking
    errors = models.JSONField(default=list, blank=True)

    # Campaign reference
    campaign = models.ForeignKey('messaging.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='sms_bulk_uploads')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sms_bulk_uploads'
        ordering = ['-created_at']

    def __str__(self):
        return f"Bulk Upload {self.file_name} - {self.status}"


class SMSSchedule(models.Model):
    """
    Advanced scheduling for SMS campaigns.
    """
    FREQUENCY_CHOICES = [
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sms_schedules')

    # Schedule details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Timing
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    time_zone = models.CharField(max_length=50, default='UTC')

    # Custom schedule (for complex patterns)
    custom_schedule = models.JSONField(default=dict, blank=True)

    # Campaign reference
    campaign = models.ForeignKey('messaging.Campaign', on_delete=models.CASCADE, related_name='sms_schedules')

    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sms_schedules'
        ordering = ['-created_at']

    def __str__(self):
        return f"Schedule {self.name} - {self.frequency}"


class SenderNameRequest(models.Model):
    """
    Model to store sender name registration requests from users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('requires_changes', 'Requires Changes'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sender_name_requests')

    # Request details
    sender_name = models.CharField(max_length=11, help_text="Sender name (max 11 alphanumeric characters)")
    use_case = models.TextField(help_text="Description of how the sender name will be used")

    # File attachments
    supporting_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of uploaded supporting document file paths"
    )

    # Status and processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Admin notes about the request")
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_sender_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    # Provider integration
    provider_request_id = models.CharField(max_length=100, blank=True, help_text="ID from SMS provider")
    provider_response = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'sender_name_requests'
        ordering = ['-created_at']
        unique_together = ['tenant', 'sender_name']

    def __str__(self):
        return f"Sender Request: {self.sender_name} - {self.status}"

    @property
    def supporting_documents_count(self):
        """Return count of supporting documents."""
        return len(self.supporting_documents) if self.supporting_documents else 0
