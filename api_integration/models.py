"""
API Integration models for external system integration.
"""
import uuid
import secrets
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()


class APIAccount(models.Model):
    """
    API Account for external integrations.
    Each account has a unique account_id and can have multiple API keys.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.CharField(max_length=32, unique=True, help_text="Public account identifier")
    name = models.CharField(max_length=100, help_text="Account name for identification")
    description = models.TextField(blank=True, help_text="Account description")
    
    # Owner information
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_accounts')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='api_accounts')
    
    # Status and limits
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    
    # Rate limiting
    rate_limit_per_minute = models.PositiveIntegerField(default=100, help_text="API calls per minute")
    rate_limit_per_hour = models.PositiveIntegerField(default=1000, help_text="API calls per hour")
    rate_limit_per_day = models.PositiveIntegerField(default=10000, help_text="API calls per day")
    
    # Usage tracking
    total_api_calls = models.PositiveBigIntegerField(default=0)
    last_api_call = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Account expiration date")
    
    class Meta:
        db_table = 'api_accounts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"API Account: {self.name} ({self.account_id})"
    
    def generate_account_id(self):
        """Generate a unique account ID."""
        if not self.account_id:
            self.account_id = secrets.token_urlsafe(16).upper()
        return self.account_id
    
    def is_rate_limited(self, time_window='minute'):
        """Check if account is rate limited."""
        from .utils import check_rate_limit
        return check_rate_limit(self, time_window)
    
    def increment_api_call(self):
        """Increment API call counter."""
        self.total_api_calls += 1
        self.last_api_call = timezone.now()
        self.save(update_fields=['total_api_calls', 'last_api_call'])


class APIKey(models.Model):
    """
    API Keys for authentication.
    Each API Account can have multiple keys for different integrations.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_account = models.ForeignKey(APIAccount, on_delete=models.CASCADE, related_name='api_keys')
    
    # Key information
    key_name = models.CharField(max_length=100, help_text="Name for this API key")
    api_key = models.CharField(max_length=64, unique=True, help_text="The actual API key")
    secret_key = models.CharField(max_length=64, help_text="Secret key for additional security")
    
    # Status and permissions
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    
    # Permissions (JSON field for flexibility)
    permissions = models.JSONField(
        default=dict,
        help_text="JSON object defining what this key can access"
    )
    
    # Usage tracking
    total_uses = models.PositiveBigIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Key expiration date")
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"API Key: {self.key_name} ({self.api_key[:8]}...)"
    
    def generate_keys(self):
        """Generate API key and secret key."""
        if not self.api_key:
            self.api_key = f"mif_{secrets.token_urlsafe(32)}"
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
        return self.api_key, self.secret_key
    
    def is_valid(self):
        """Check if key is valid and not expired."""
        if not self.is_active or self.status != 'active':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def revoke(self):
        """Revoke the API key."""
        self.status = 'revoked'
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save()
    
    def increment_use(self, ip_address=None):
        """Increment usage counter."""
        self.total_uses += 1
        self.last_used = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.save(update_fields=['total_uses', 'last_used', 'last_used_ip'])


class APIIntegration(models.Model):
    """
    Track external integrations using our API.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_account = models.ForeignKey(APIAccount, on_delete=models.CASCADE, related_name='integrations')
    
    # Integration details
    name = models.CharField(max_length=100, help_text="Integration name")
    description = models.TextField(blank=True, help_text="Integration description")
    platform = models.CharField(max_length=50, help_text="Platform (e.g., 'webhook', 'mobile', 'desktop')")
    webhook_url = models.URLField(blank=True, help_text="Webhook URL for notifications")
    
    # Status and configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    
    # Configuration (JSON field for flexibility)
    config = models.JSONField(
        default=dict,
        help_text="Integration-specific configuration"
    )
    
    # Usage statistics
    total_requests = models.PositiveBigIntegerField(default=0)
    successful_requests = models.PositiveBigIntegerField(default=0)
    failed_requests = models.PositiveBigIntegerField(default=0)
    last_request = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_integrations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Integration: {self.name} ({self.platform})"
    
    def increment_request(self, success=True):
        """Increment request counter."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.last_request = timezone.now()
        self.save(update_fields=[
            'total_requests', 'successful_requests', 'failed_requests', 'last_request'
        ])


class APIUsageLog(models.Model):
    """
    Log API usage for monitoring and analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_account = models.ForeignKey(APIAccount, on_delete=models.CASCADE, related_name='usage_logs')
    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, blank=True, related_name='usage_logs')
    integration = models.ForeignKey(APIIntegration, on_delete=models.SET_NULL, null=True, blank=True, related_name='usage_logs')
    
    # Request details
    endpoint = models.CharField(max_length=200, help_text="API endpoint called")
    method = models.CharField(max_length=10, help_text="HTTP method")
    status_code = models.PositiveIntegerField(help_text="HTTP status code")
    
    # Request metadata
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_size = models.PositiveIntegerField(default=0, help_text="Request size in bytes")
    response_size = models.PositiveIntegerField(default=0, help_text="Response size in bytes")
    
    # Timing
    response_time_ms = models.PositiveIntegerField(help_text="Response time in milliseconds")
    
    # Error details
    error_message = models.TextField(blank=True, help_text="Error message if any")
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_usage_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['api_account', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['status_code', 'timestamp']),
        ]
    
    def __str__(self):
        return f"API Usage: {self.endpoint} - {self.status_code} ({self.timestamp})"


class Webhook(models.Model):
    """
    Webhook configuration for receiving notifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_account = models.ForeignKey(APIAccount, on_delete=models.CASCADE, related_name='webhooks')
    
    # Webhook details
    url = models.URLField(help_text="Webhook URL to receive notifications")
    events = models.JSONField(
        default=list,
        help_text="List of events this webhook should receive"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Usage tracking
    total_calls = models.PositiveBigIntegerField(default=0)
    successful_calls = models.PositiveBigIntegerField(default=0)
    failed_calls = models.PositiveBigIntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, help_text="Last error message")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_webhooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook: {self.url} ({'active' if self.is_active else 'inactive'})"
    
    def trigger(self, event_data):
        """Trigger the webhook with event data."""
        # This would typically make an HTTP request to the webhook URL
        # For now, we'll just update the counters
        self.total_calls += 1
        self.last_triggered = timezone.now()
        self.save(update_fields=['total_calls', 'last_triggered'])
    
    def mark_success(self):
        """Mark webhook call as successful."""
        self.successful_calls += 1
        self.save(update_fields=['successful_calls'])
    
    def mark_failure(self, error_message=""):
        """Mark webhook call as failed."""
        self.failed_calls += 1
        if error_message:
            self.last_error = error_message
        self.save(update_fields=['failed_calls', 'last_error'])
