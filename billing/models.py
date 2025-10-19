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
    
    # Sender ID Configuration
    default_sender_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Default sender ID for this package (e.g., Taarifa-SMS, Quantum)"
    )
    allowed_sender_ids = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of allowed sender IDs for this package"
    )
    sender_id_restriction = models.CharField(
        max_length=20,
        choices=[
            ('none', 'No Restriction'),
            ('default_only', 'Default Sender ID Only'),
            ('allowed_list', 'Allowed List Only'),
            ('custom_only', 'Custom Sender IDs Only'),
        ],
        default='none',
        help_text="Sender ID restriction policy"
    )
    
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
    
    def is_sender_id_allowed(self, sender_id):
        """
        Check if a sender ID is allowed for this package.
        
        Args:
            sender_id (str): The sender ID to check
            
        Returns:
            bool: True if sender ID is allowed, False otherwise
        """
        if not sender_id:
            return False
            
        # No restriction - all sender IDs allowed
        if self.sender_id_restriction == 'none':
            return True
            
        # Only default sender ID allowed
        if self.sender_id_restriction == 'default_only':
            return sender_id == self.default_sender_id
            
        # Only allowed list sender IDs
        if self.sender_id_restriction == 'allowed_list':
            return sender_id in (self.allowed_sender_ids or [])
            
        # Custom sender IDs only (for custom packages)
        if self.sender_id_restriction == 'custom_only':
            return self.package_type == 'custom'
            
        return False
    
    def get_available_sender_ids(self):
        """
        Get list of available sender IDs for this package.
        
        Returns:
            list: List of available sender IDs
        """
        if self.sender_id_restriction == 'none':
            # Return all registered sender IDs from Beem
            from messaging.services.sms_service import SMSService
            try:
                sms_service = SMSService(tenant_id=None)  # Get from any tenant
                result = sms_service.get_sender_ids()
                if result.get('success'):
                    return [sender.get('senderid') for sender in result.get('sender_ids', []) 
                           if sender.get('status') == 'active']
            except:
                pass
            return []
            
        elif self.sender_id_restriction == 'default_only':
            return [self.default_sender_id] if self.default_sender_id else []
            
        elif self.sender_id_restriction == 'allowed_list':
            return self.allowed_sender_ids or []
            
        elif self.sender_id_restriction == 'custom_only':
            return []  # Custom packages don't have predefined sender IDs
            
        return []
    
    def get_effective_sender_id(self, requested_sender_id=None):
        """
        Get the effective sender ID to use for this package.
        
        Args:
            requested_sender_id (str, optional): The requested sender ID
            
        Returns:
            str: The effective sender ID to use
        """
        # If no sender ID requested, use default
        if not requested_sender_id:
            return self.default_sender_id or 'Taarifa-SMS'
            
        # Check if requested sender ID is allowed
        if self.is_sender_id_allowed(requested_sender_id):
            return requested_sender_id
            
        # Fall back to default if requested is not allowed
        return self.default_sender_id or 'Taarifa-SMS'


class SMSBalance(models.Model):
    """
    SMS credit balance for each tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='sms_balance')
    credits = models.PositiveIntegerField(default=0)
    total_purchased = models.PositiveIntegerField(default=0)
    total_used = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sms_balances'

    def __str__(self):
        return f"{self.tenant.name} - {self.credits} credits"

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


class PaymentTransaction(models.Model):
    """
    Payment transactions for ZenoPay integration.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('zenopay_mobile_money', 'ZenoPay Mobile Money'),
        ('mpesa', 'M-Pesa'),
        ('tigopesa', 'Tigo Pesa'),
        ('airtelmoney', 'Airtel Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='payment_transactions')

    # ZenoPay specific fields
    zenopay_order_id = models.CharField(max_length=100, unique=True, help_text="ZenoPay order ID")
    zenopay_reference = models.CharField(max_length=100, blank=True, help_text="ZenoPay reference number")
    zenopay_transid = models.CharField(max_length=100, blank=True, help_text="ZenoPay transaction ID")
    zenopay_channel = models.CharField(max_length=50, blank=True, help_text="Payment channel (e.g., MPESA-TZ)")
    zenopay_msisdn = models.CharField(max_length=20, blank=True, help_text="Customer phone number")

    # Transaction details
    order_id = models.CharField(max_length=100, unique=True, help_text="Internal order ID")
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='TZS')

    # Customer details
    buyer_email = models.EmailField()
    buyer_name = models.CharField(max_length=100)
    buyer_phone = models.CharField(max_length=20)

    # Payment details
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)
    payment_reference = models.CharField(max_length=100, blank=True)
    mobile_money_provider = models.CharField(
        max_length=20,
        choices=[
            ('vodacom', 'Vodacom M-Pesa'),
            ('halotel', 'Halotel'),
            ('tigo', 'Tigo Pesa'),
            ('airtel', 'Airtel Money')
        ],
        blank=True,
        help_text='Mobile money provider for payment'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Webhook and callback
    webhook_url = models.URLField(blank=True)
    webhook_received = models.BooleanField(default=False)
    webhook_data = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'payment_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.order_id} - {self.amount} {self.currency}"

    def mark_as_processing(self):
        """Mark transaction as processing."""
        self.status = 'processing'
        self.save()

    def mark_as_completed(self, zenopay_data=None):
        """Mark transaction as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if zenopay_data:
            self.webhook_data = zenopay_data
            self.webhook_received = True
        self.save()

    def mark_as_failed(self, error_message=None):
        """Mark transaction as failed."""
        self.status = 'failed'
        self.failed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save()

    def mark_as_cancelled(self):
        """Mark transaction as cancelled."""
        self.status = 'cancelled'
        self.save()

    def mark_as_expired(self, error_message=None):
        """Mark transaction as expired."""
        self.status = 'expired'
        self.failed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save()


class Purchase(models.Model):
    """
    SMS credit purchase transactions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHODS = [
        ('zenopay_mobile_money', 'ZenoPay Mobile Money'),
        ('mpesa', 'M-Pesa'),
        ('tigopesa', 'Tigo Pesa'),
        ('airtelmoney', 'Airtel Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='purchases')
    package = models.ForeignKey(SMSPackage, on_delete=models.CASCADE, related_name='purchases')

    # Link to payment transaction
    payment_transaction = models.OneToOneField(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase'
    )

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
        if self.status == 'pending' or self.status == 'processing':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()

            # Add credits to tenant balance
            balance, created = SMSBalance.objects.get_or_create(tenant=self.tenant)
            balance.add_credits(self.credits)

            return True
        return False

    def mark_as_processing(self):
        """Mark purchase as processing."""
        self.status = 'processing'
        self.save()

    def mark_as_failed(self):
        """Mark purchase as failed."""
        self.status = 'failed'
        self.save()

    def mark_as_expired(self):
        """Mark purchase as expired."""
        self.status = 'expired'
        self.save()


class UsageRecord(models.Model):
    """
    Track SMS usage for billing and analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='usage_records')
    message = models.ForeignKey('messaging.SMSMessage', on_delete=models.CASCADE, related_name='usage_record', null=True, blank=True)
    credits_used = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sms_usage_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"Usage {self.tenant.name} - {self.credits_used} credits"


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
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='subscription')
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
        return f"{self.tenant.name} - {self.plan.name}"

    @property
    def is_active(self):
        """Check if subscription is currently active."""
        now = timezone.now()
        return (
            self.status == 'active' and
            self.current_period_start <= now <= self.current_period_end
        )


class CustomSMSPurchase(models.Model):
    """
    Custom SMS purchase for flexible credit amounts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='custom_sms_purchases')
    
    # Custom purchase details
    credits = models.PositiveIntegerField(help_text="Number of SMS credits (minimum 100)")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per SMS in TZS")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price in TZS")
    
    # Pricing tier information
    active_tier = models.CharField(max_length=50, help_text="Active pricing tier (e.g., 'Lite', 'Standard')")
    tier_min_credits = models.PositiveIntegerField(help_text="Minimum credits for this tier")
    tier_max_credits = models.PositiveIntegerField(help_text="Maximum credits for this tier")
    
    # Payment information
    payment_transaction = models.OneToOneField(
        'PaymentTransaction', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='custom_sms_purchase'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'custom_sms_purchases'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Custom SMS Purchase - {self.credits} credits - {self.total_price} TZS"
    
    def calculate_pricing(self, credits):
        """
        Calculate pricing based on credit amount and active tier.
        Returns (unit_price, total_price, active_tier, tier_min, tier_max)
        """
        # Define pricing tiers
        tiers = [
            {'name': 'Lite', 'min': 1, 'max': 5000, 'unit_price': 30.00},
            {'name': 'Standard', 'min': 5001, 'max': 50000, 'unit_price': 25.00},
            {'name': 'Pro', 'min': 50001, 'max': 250000, 'unit_price': 18.00},
            {'name': 'Enterprise', 'min': 250001, 'max': 1000000, 'unit_price': 12.00},
        ]
        
        # Find the appropriate tier
        active_tier = None
        for tier in tiers:
            if tier['min'] <= credits <= tier['max']:
                active_tier = tier
                break
        
        # If credits exceed all tiers, use Enterprise pricing
        if not active_tier and credits > 1000000:
            active_tier = {'name': 'Enterprise+', 'min': 1000001, 'max': 9999999, 'unit_price': 12.00}
        
        if not active_tier:
            # Default to highest tier if no match
            active_tier = tiers[-1]
        
        unit_price = active_tier['unit_price']
        total_price = credits * unit_price
        
        return unit_price, total_price, active_tier['name'], active_tier['min'], active_tier['max']
    
    def save(self, *args, **kwargs):
        # Auto-calculate pricing if not set
        if not self.unit_price or not self.total_price:
            self.unit_price, self.total_price, self.active_tier, self.tier_min_credits, self.tier_max_credits = self.calculate_pricing(self.credits)
        super().save(*args, **kwargs)
    
    def complete_purchase(self):
        """Complete the custom SMS purchase."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Add credits to tenant's SMS balance
        sms_balance, created = SMSBalance.objects.get_or_create(tenant=self.tenant)
        sms_balance.credits += self.credits
        sms_balance.total_purchased += self.credits
        sms_balance.save()
    
    def mark_as_failed(self, error_message=None):
        """Mark the purchase as failed."""
        self.status = 'failed'
        if error_message:
            self.error_message = error_message
        self.save()
