"""
Multi-tenant models for Mifumo WMS.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Tenant(models.Model):
    """
    Represents a business/organization using the platform.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subdomain = models.SlugField(unique=True, max_length=100)
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Business details
    business_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    # WhatsApp configuration
    wa_phone_number_id = models.CharField(max_length=100, blank=True)
    wa_phone_number = models.CharField(max_length=20, blank=True)
    wa_verified = models.BooleanField(default=False)
    
    # Subscription status
    is_active = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.subdomain})"
    
    @property
    def is_trial_active(self):
        """Check if tenant is still in trial period."""
        if not self.trial_ends_at:
            return False
        return timezone.now() < self.trial_ends_at


class Domain(models.Model):
    """
    Maps custom domains to tenants.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tenant_domains'
        ordering = ['-is_primary', 'domain']
    
    def __str__(self):
        return f"{self.domain} -> {self.tenant.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary domain per tenant
        if self.is_primary:
            Domain.objects.filter(tenant=self.tenant, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Membership(models.Model):
    """
    Represents a user's membership in a tenant.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('agent', 'Agent'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_memberships')
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tenant_memberships'
        unique_together = ['tenant', 'user']
        ordering = ['-joined_at', '-invited_at']
    
    def __str__(self):
        return f"{self.user.email} in {self.tenant.name} ({self.role})"
    
    def save(self, *args, **kwargs):
        if self.status == 'active' and not self.joined_at:
            self.joined_at = timezone.now()
        super().save(*args, **kwargs)


class TenantScopedQuerySet(models.QuerySet):
    """
    QuerySet that automatically filters by tenant.
    """
    
    def filter_by_tenant(self, tenant):
        """Filter queryset by tenant."""
        return self.filter(tenant=tenant)
    
    def for_tenant(self, tenant):
        """Alias for filter_by_tenant."""
        return self.filter_by_tenant(tenant)


class TenantScopedManager(models.Manager):
    """
    Manager that provides tenant-scoped querysets.
    """
    
    def get_queryset(self):
        return TenantScopedQuerySet(self.model, using=self._db)
    
    def filter_by_tenant(self, tenant):
        return self.get_queryset().filter_by_tenant(tenant)
    
    def for_tenant(self, tenant):
        return self.get_queryset().for_tenant(tenant)
