#!/usr/bin/env python3
"""
Production Data Setup Script
This script creates all necessary initial data for production
"""

import os
import sys
import django
from pathlib import Path
from datetime import timedelta

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils import timezone
from tenants.models import Tenant, Membership, Domain
from messaging.models_sms import SMSProvider, SMSSenderID, SMSTemplate
from accounts.models import UserProfile

User = get_user_model()

def create_default_tenant():
    """Create a default tenant for the system"""
    print("🏢 Creating default tenant...")
    try:
        tenant, created = Tenant.objects.get_or_create(
            subdomain='default',
            defaults={
                'name': 'Mifumo WMS Default',
                'business_name': 'Mifumo WMS',
                'business_type': 'Technology',
                'email': 'admin@mifumo.com',
                'phone_number': '+255700000000',
                'address': 'Dar es Salaam, Tanzania',
                'timezone': 'Africa/Dar_es_Salaam',
                'is_active': True,
                'trial_ends_at': timezone.now() + timedelta(days=30),  # 30-day trial
            }
        )
        
        if created:
            print(f"✅ Created default tenant: {tenant.name}")
        else:
            print(f"ℹ️  Default tenant already exists: {tenant.name}")
        
        return tenant
    except Exception as e:
        print(f"❌ Failed to create default tenant: {e}")
        return None

def create_tenant_domain(tenant):
    """Create domain mapping for tenant"""
    print("🌐 Creating tenant domain...")
    try:
        domain, created = Domain.objects.get_or_create(
            domain='104.131.116.55:8000',
            defaults={
                'tenant': tenant,
                'is_primary': True,
                'verified': True,
            }
        )
        
        if created:
            print(f"✅ Created domain: {domain.domain}")
        else:
            print(f"ℹ️  Domain already exists: {domain.domain}")
        
        return domain
    except Exception as e:
        print(f"❌ Failed to create domain: {e}")
        return None

def create_sms_provider(tenant):
    """Create default SMS provider (Beem)"""
    print("📱 Creating SMS provider...")
    try:
        provider, created = SMSProvider.objects.get_or_create(
            tenant=tenant,
            name='Beem Africa SMS',
            defaults={
                'provider_type': 'beem',
                'is_active': True,
                'is_default': True,
                'api_key': '62f8c3a2cb510335',
                'secret_key': 'YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ==',
                'api_url': 'https://apisms.beem.africa/v1/send',
                'cost_per_sms': 0.05,
                'currency': 'USD',
                'settings': {
                    'balance_url': 'https://apisms.beem.africa/public/v1/vendors/balance',
                    'delivery_url': 'https://dlrapi.beem.africa/public/v1/delivery-reports',
                    'sender_url': 'https://apisms.beem.africa/public/v1/sender-names',
                    'template_url': 'https://apisms.beem.africa/public/v1/sms-templates',
                }
            }
        )
        
        if created:
            print(f"✅ Created SMS provider: {provider.name}")
        else:
            print(f"ℹ️  SMS provider already exists: {provider.name}")
        
        return provider
    except Exception as e:
        print(f"❌ Failed to create SMS provider: {e}")
        return None

def create_sms_sender_id(tenant, provider):
    """Create default SMS sender ID"""
    print("📞 Creating SMS sender ID...")
    try:
        sender_id, created = SMSSenderID.objects.get_or_create(
            tenant=tenant,
            sender_id='MIFUMO',
            defaults={
                'provider': provider,
                'sample_content': 'Welcome to Mifumo WMS! This is a test message.',
                'status': 'active',
                'provider_sender_id': 'MIFUMO',
            }
        )
        
        if created:
            print(f"✅ Created SMS sender ID: {sender_id.sender_id}")
        else:
            print(f"ℹ️  SMS sender ID already exists: {sender_id.sender_id}")
        
        return sender_id
    except Exception as e:
        print(f"❌ Failed to create SMS sender ID: {e}")
        return None

def create_sms_templates(tenant):
    """Create default SMS templates"""
    print("📝 Creating SMS templates...")
    
    templates = [
        {
            'name': 'Welcome Message',
            'category': 'TRANSACTIONAL',
            'message': 'Welcome to {company_name}! Thank you for joining us.',
            'variables': ['company_name'],
        },
        {
            'name': 'OTP Verification',
            'category': 'OTP',
            'message': 'Your verification code is {otp_code}. Valid for 5 minutes.',
            'variables': ['otp_code'],
        },
        {
            'name': 'Order Confirmation',
            'category': 'TRANSACTIONAL',
            'message': 'Your order #{order_number} has been confirmed. Total: {amount} {currency}.',
            'variables': ['order_number', 'amount', 'currency'],
        },
        {
            'name': 'Payment Reminder',
            'category': 'TRANSACTIONAL',
            'message': 'Reminder: Your payment of {amount} {currency} is due on {due_date}.',
            'variables': ['amount', 'currency', 'due_date'],
        },
        {
            'name': 'Promotional Offer',
            'category': 'PROMOTIONAL',
            'message': 'Special offer! Get {discount}% off on {product}. Use code {promo_code}.',
            'variables': ['discount', 'product', 'promo_code'],
        },
    ]
    
    created_count = 0
    for template_data in templates:
        try:
            template, created = SMSTemplate.objects.get_or_create(
                tenant=tenant,
                name=template_data['name'],
                defaults={
                    'category': template_data['category'],
                    'language': 'en',
                    'message': template_data['message'],
                    'variables': template_data['variables'],
                    'is_active': True,
                    'approval_status': 'approved',
                    'approved_at': timezone.now(),
                }
            )
            
            if created:
                created_count += 1
                print(f"  ✅ Created template: {template.name}")
            else:
                print(f"  ℹ️  Template already exists: {template.name}")
                
        except Exception as e:
            print(f"  ❌ Failed to create template {template_data['name']}: {e}")
    
    print(f"✅ Created {created_count} SMS templates")

def create_user_membership(tenant, user):
    """Create membership for user in tenant"""
    print(f"👤 Creating membership for {user.email}...")
    try:
        membership, created = Membership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={
                'role': 'owner',
                'status': 'active',
                'joined_at': timezone.now(),
            }
        )
        
        if created:
            print(f"✅ Created membership: {user.email} as {membership.role}")
        else:
            print(f"ℹ️  Membership already exists: {user.email}")
        
        return membership
    except Exception as e:
        print(f"❌ Failed to create membership: {e}")
        return None

def create_user_profile(user):
    """Create user profile if it doesn't exist"""
    print(f"👤 Creating profile for {user.email}...")
    try:
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'job_title': 'System Administrator',
                'company': 'Mifumo WMS',
                'industry': 'Technology',
                'preferred_language': 'en',
                'date_format': 'MM/DD/YYYY',
                'time_format': '12h',
            }
        )
        
        if created:
            print(f"✅ Created user profile for {user.email}")
        else:
            print(f"ℹ️  User profile already exists for {user.email}")
        
        return profile
    except Exception as e:
        print(f"❌ Failed to create user profile: {e}")
        return None

def main():
    print("🚀 Production Data Setup")
    print("=" * 50)
    
    # Get or create superuser
    print("👤 Checking for superuser...")
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("❌ No superuser found! Please create one first.")
        return
    
    print(f"✅ Found superuser: {superuser.email}")
    
    # Create default tenant
    tenant = create_default_tenant()
    if not tenant:
        print("❌ Cannot proceed without tenant")
        return
    
    # Create tenant domain
    create_tenant_domain(tenant)
    
    # Create SMS provider
    provider = create_sms_provider(tenant)
    if not provider:
        print("❌ Cannot proceed without SMS provider")
        return
    
    # Create SMS sender ID
    sender_id = create_sms_sender_id(tenant, provider)
    
    # Create SMS templates
    create_sms_templates(tenant)
    
    # Create user membership
    create_user_membership(tenant, superuser)
    
    # Create user profile
    create_user_profile(superuser)
    
    print("\n" + "=" * 50)
    print("🎉 Production data setup completed!")
    print("\nYou should now see:")
    print("✅ Tenants in admin panel")
    print("✅ Domains in admin panel")
    print("✅ SMS Providers in admin panel")
    print("✅ SMS Sender IDs in admin panel")
    print("✅ SMS Templates in admin panel")
    print("✅ User Profiles in admin panel")
    print("\nAccess admin at: http://104.131.116.55:8000/admin/")

if __name__ == "__main__":
    main()
