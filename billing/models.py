"""
Billing models for Mifumo WMS.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class SMSPackage(models.Model):
    """
    SMS credit packages available for purchase.
    """
    PACKAGE_TYPES = [
        ('lite', 'Lite'),
        ('standard', 'Standard'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES)
    credits = models.PositiveIntegerField(help_text="Number of SMS credits")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in TZS")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per SMS in TZS")
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    features = models.JSONField(default=list, blank=True, help_text="List of features")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sms_packages'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.credits} credits"
    
    @property
    def savings_percentage(self):
        """Calculate savings compared to standard rate."""
        standard_rate = 30  # TZS per SMS
        if self.unit_price < standard_rate:
            return round(((standard_rate - self.unit_price) / standard_rate) * 100, 1)
        return 0


class SMSBalance(models.Model):
    """
    SMS credit balance for each user.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sms_balance')
    credits = models.PositiveIntegerField(default=0)
    total_purchased = models.PositiveIntegerField(default=0)
    total_used = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_balances'
    
    def __str__(self):
        return f"{self.user.email} - {self.credits} credits"
    
    def add_credits(self, amount):
        """Add credits to balance."""
        self.credits += amount
        self.total_purchased += amount
        self.save()
    
    def use_credits(self, amount):
        """Use credits from balance."""
        if self.credits >= amount:
            self.credits -= amount
            self.total_used += amount
            self.save()
            return True
        return False


class Purchase(models.Model):
    """
    SMS credit purchase transactions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('tigopesa', 'Tigo Pesa'),
        ('airtelmoney', 'Airtel Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    package = models.ForeignKey(SMSPackage, on_delete=models.CASCADE, related_name='purchases')
    
    # Transaction details
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credits = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sms_purchases'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Purchase {self.invoice_number} - {self.credits} credits"
    
    def complete_purchase(self):
        """Mark purchase as completed and add credits to balance."""
        if self.status == 'pending':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
            # Add credits to user balance
            balance, created = SMSBalance.objects.get_or_create(user=self.user)
            balance.add_credits(self.credits)
            
            return True
        return False


class UsageRecord(models.Model):
    """
    Track SMS usage for billing and analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_records')
    message = models.ForeignKey('messaging.SMSMessage', on_delete=models.CASCADE, related_name='usage_record', null=True, blank=True)
    credits_used = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_usage_records'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Usage {self.user.email} - {self.credits_used} credits"


class BillingPlan(models.Model):
    """
    Subscription plans for the platform.
    """
    PLAN_TYPES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TZS')
    billing_cycle = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    
    # Limits
    max_contacts = models.PositiveIntegerField(null=True, blank=True)
    max_campaigns = models.PositiveIntegerField(null=True, blank=True)
    max_sms_per_month = models.PositiveIntegerField(null=True, blank=True)
    
    # Features
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billing_plans'
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.price} {self.currency}/{self.billing_cycle}"


class Subscription(models.Model):
    """
    User subscription to billing plans.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('past_due', 'Past Due'),
        ('suspended', 'Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(BillingPlan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Billing periods
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions'
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    
    @property
    def is_active(self):
        """Check if subscription is currently active."""
        now = timezone.now()
        return (
            self.status == 'active' and 
            self.current_period_start <= now <= self.current_period_end
        )