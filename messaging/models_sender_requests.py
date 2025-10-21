"""
Sender ID request models for Mifumo WMS.
Users can request to use default or custom sender IDs after purchasing SMS credits.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from tenants.models import Tenant
import uuid

User = get_user_model()


class SenderIDRequest(models.Model):
    """
    Represents a user's request to use a sender ID.
    Users must have purchased SMS credits before requesting a sender ID.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('requires_changes', 'Requires Changes'),
        ('cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('default', 'Default Sender ID'),
        ('custom', 'Custom Sender ID'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sender_id_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_id_requests')
    
    # Request details
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='default')
    requested_sender_id = models.CharField(max_length=11, help_text="Requested sender ID (max 11 characters)")
    sample_content = models.TextField(max_length=170, help_text="Sample message content (max 170 characters)")
    
    # Status and approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_sender_id_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")
    
    # SMS Package association
    sms_package = models.ForeignKey('billing.SMSPackage', on_delete=models.SET_NULL, null=True, blank=True, related_name='sender_id_requests')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sender_id_requests'
        ordering = ['-created_at']
        unique_together = ['tenant', 'requested_sender_id']

    def __str__(self):
        return f"{self.requested_sender_id} - {self.get_status_display()}"

    def approve(self, reviewed_by_user):
        """Approve the sender ID request."""
        self.status = 'approved'
        self.reviewed_by = reviewed_by_user
        self.reviewed_at = timezone.now()
        self.save()
        
        # Create the actual sender ID
        self.create_sender_id()

    def reject(self, reviewed_by_user, reason=""):
        """Reject the sender ID request."""
        self.status = 'rejected'
        self.reviewed_by = reviewed_by_user
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save()

    def create_sender_id(self):
        """Create the actual sender ID after approval."""
        from .models_sms import SMSProvider, SMSSenderID
        
        # Get the SMS provider for this tenant
        sms_provider = SMSProvider.objects.filter(tenant=self.tenant, is_active=True).first()
        if not sms_provider:
            raise ValueError("No active SMS provider found for this tenant")
        
        # Create the sender ID
        sender_id = SMSSenderID.objects.create(
            tenant=self.tenant,
            sender_id=self.requested_sender_id,
            provider=sms_provider,
            status='active',
            sample_content=self.sample_content,
            created_by=self.user
        )
        
        return sender_id

    @property
    def can_be_approved(self):
        """Check if the request can be approved."""
        return self.status == 'pending'

    @property
    def is_approved(self):
        """Check if the request is approved."""
        return self.status == 'approved'

    @property
    def is_rejected(self):
        """Check if the request is rejected."""
        return self.status == 'rejected'


class SenderIDUsage(models.Model):
    """
    Track usage of sender IDs with SMS packages.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sender_id_usage')
    sender_id_request = models.ForeignKey(SenderIDRequest, on_delete=models.CASCADE, related_name='usage_records')
    sms_package = models.ForeignKey('billing.SMSPackage', on_delete=models.CASCADE, related_name='sender_id_usage')
    
    # Usage tracking
    is_active = models.BooleanField(default=True)
    attached_at = models.DateTimeField(auto_now_add=True)
    detached_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sender_id_usage'
        ordering = ['-attached_at']

    def __str__(self):
        return f"{self.sender_id_request.requested_sender_id} with {self.sms_package.name}"

    def detach(self):
        """Detach the sender ID from the SMS package."""
        self.is_active = False
        self.detached_at = timezone.now()
        self.save()
