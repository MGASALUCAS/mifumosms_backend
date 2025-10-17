#!/usr/bin/env python3
"""
Fix Missing Models in Production
Quick fix for missing Tenant and SMS Provider data
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership, Domain
from messaging.models_sms import SMSProvider, SMSSenderID
from accounts.models import UserProfile
from django.utils import timezone

User = get_user_model()

def main():
    print("🔧 Fixing Missing Models in Production")
    print("=" * 45)
    
    # Get superuser
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("❌ No superuser found!")
        return
    
    print(f"✅ Found superuser: {superuser.email}")
    
    # Create default tenant
    print("🏢 Creating default tenant...")
    tenant, created = Tenant.objects.get_or_create(
        subdomain='default',
        defaults={
            'name': 'Mifumo WMS Default',
            'business_name': 'Mifumo WMS',
            'email': 'admin@mifumo.com',
            'is_active': True,
        }
    )
    print(f"✅ Tenant: {tenant.name}")
    
    # Create domain for tenant
    print("🌐 Creating domain...")
    domain, created = Domain.objects.get_or_create(
        domain='104.131.116.55:8000',
        defaults={
            'tenant': tenant,
            'is_primary': True,
            'verified': True,
        }
    )
    print(f"✅ Domain: {domain.domain}")
    
    # Create SMS provider
    print("📱 Creating SMS provider...")
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
        }
    )
    print(f"✅ SMS Provider: {provider.name}")
    
    # Create SMS sender ID
    print("📞 Creating SMS sender ID...")
    sender_id, created = SMSSenderID.objects.get_or_create(
        tenant=tenant,
        sender_id='MIFUMO',
        defaults={
            'provider': provider,
            'sample_content': 'Welcome to Mifumo WMS!',
            'status': 'active',
        }
    )
    print(f"✅ SMS Sender ID: {sender_id.sender_id}")
    
    # Create user membership
    print("👤 Creating user membership...")
    membership, created = Membership.objects.get_or_create(
        tenant=tenant,
        user=superuser,
        defaults={
            'role': 'owner',
            'status': 'active',
            'joined_at': timezone.now(),
        }
    )
    print(f"✅ Membership: {superuser.email} as {membership.role}")
    
    # Create user profile
    print("👤 Creating user profile...")
    profile, created = UserProfile.objects.get_or_create(
        user=superuser,
        defaults={
            'job_title': 'System Administrator',
            'company': 'Mifumo WMS',
        }
    )
    print(f"✅ User Profile: {profile}")
    
    print("\n🎉 All models created successfully!")
    print("You should now see Tenants and SMS Providers in admin panel.")

if __name__ == "__main__":
    main()
