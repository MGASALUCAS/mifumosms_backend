"""
Django signals for user management.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import User, UserProfile
from tenants.models import Tenant, Membership, Domain
from messaging.models_sms import SMSProvider, SMSSenderID


@receiver(post_save, sender=User)
def create_user_profile_and_tenant(sender, instance, created, **kwargs):
    """
    Automatically create user profile and tenant information when a user is created.
    This ensures SMS functionality works immediately for new users.
    """
    if created:
        # Create user profile if it doesn't exist
        UserProfile.objects.get_or_create(user=instance)
        
        # Create a default tenant for the user
        create_default_tenant_for_user(instance)


def create_default_tenant_for_user(user):
    """
    Create a default tenant, membership, and domain for a new user.
    This ensures SMS functionality is available immediately.
    """
    try:
        # Generate a unique subdomain based on user's email
        subdomain = generate_unique_subdomain(user.email)
        
        # Create tenant
        tenant = Tenant.objects.create(
            name=f"{user.get_full_name()}'s Organization",
            subdomain=subdomain,
            business_name=user.get_full_name() or "My Business",
            business_type="General",
            email=user.email,
            phone_number=user.phone_number or "",
            timezone=user.timezone or "UTC",
            is_active=True,
            trial_ends_at=timezone.now() + timedelta(days=30)  # 30-day trial
        )
        
        # Create membership for the user as owner
        Membership.objects.create(
            tenant=tenant,
            user=user,
            role='owner',
            status='active',
            joined_at=timezone.now()
        )
        
        # Create default domain
        Domain.objects.create(
            tenant=tenant,
            domain=f"{tenant.subdomain}.mifumo.local",
            is_primary=True,
            verified=True
        )
        
        # Set up basic SMS configuration
        setup_basic_sms_config(tenant, user)
        
        print(f"Created tenant '{tenant.name}' for user {user.email}")
        
    except Exception as e:
        print(f"Failed to create tenant for user {user.email}: {e}")


def generate_unique_subdomain(email):
    """
    Generate a unique subdomain based on user's email.
    """
    # Extract username part from email
    username = email.split('@')[0].lower()
    
    # Clean the username (remove special characters, keep only alphanumeric and hyphens)
    import re
    username = re.sub(r'[^a-z0-9-]', '', username)
    
    # Ensure it's not empty and starts with a letter
    if not username or username[0].isdigit():
        username = f"user{username}" if username else "user"
    
    # Truncate to reasonable length
    username = username[:20]
    
    # Check if subdomain is unique, if not append numbers
    subdomain = username
    counter = 1
    while Tenant.objects.filter(subdomain=subdomain).exists():
        subdomain = f"{username}{counter}"
        counter += 1
    
    return subdomain


def setup_basic_sms_config(tenant, user):
    """
    Set up basic SMS configuration for the tenant using shared sender ID.
    """
    try:
        # Get the owner user for this tenant
        owner = tenant.memberships.filter(role='owner').first()
        if not owner:
            print(f"No owner found for tenant {tenant.name}")
            return
            
        # Create a default SMS provider for the tenant
        sms_provider = SMSProvider.objects.create(
            tenant=tenant,
            name="Default Beem Provider",
            provider_type="beem",
            is_active=True,
            is_default=True,
            api_key="",  # Will be configured later
            secret_key="",  # Will be configured later
            api_url="https://apisms.beem.africa/v1/send",
            cost_per_sms=0.0,
            currency="TZS",
            created_by=owner.user
        )
        
        # Create default sender ID for all users (both admin and regular users)
        sender_id = SMSSenderID.objects.create(
            tenant=tenant,
            sender_id="Taarifa-SMS",  # Default sender ID for all users
            provider=sms_provider,
            status='active',  # Auto-approve for all users
            sample_content="A test use case for the sender name purposely used for information transfer.",
            created_by=owner.user
        )
        print(f"Created default sender ID '{sender_id.sender_id}' for user {user.email}")
        
        # Also create a default sender ID request for tracking purposes
        from messaging.models_sender_requests import SenderIDRequest
        default_request = SenderIDRequest.objects.create(
            tenant=tenant,
            user=owner.user,
            request_type='default',
            requested_sender_id='Taarifa-SMS',
            sample_content="A test use case for the sender name purposely used for information transfer.",
            status='approved'  # Auto-approve since we created the sender ID
        )
        print(f"Created default sender ID request for user {user.email}")
        
        # Create SMS balance with zero credits (user must purchase)
        from billing.models import SMSBalance
        SMSBalance.objects.create(
            tenant=tenant,
            credits=0,  # Zero credits - user must purchase
            total_purchased=0,
            total_used=0
        )
        
        print(f"Created SMS provider for tenant {tenant.name}")
        print(f"Created SMS balance with 0 credits - user must purchase SMS packages first")
        print(f"Created default sender ID 'Taarifa-SMS' - ready for immediate use")
            
    except Exception as e:
        print(f"Failed to setup SMS config for tenant {tenant.name}: {e}")
