#!/usr/bin/env python
"""
Script to create a sender ID for SMS testing.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from messaging.models_sms import SMSProvider, SMSSenderID

User = get_user_model()

def setup_sender_id():
    """Set up sender ID for SMS testing."""
    print("🔧 Setting up SMS Sender ID...")
    
    try:
        # Get admin user and tenant
        user = User.objects.get(email='admin@mifumo.com')
        tenant = user.tenant
        
        if not tenant:
            print("❌ User has no tenant!")
            return False
        
        print(f"✅ User: {user.email}")
        print(f"✅ Tenant: {tenant.name}")
        
        # Get or create Beem provider
        provider, created = SMSProvider.objects.get_or_create(
            tenant=tenant,
            provider_type='beem',
            defaults={
                'name': 'Beem Africa SMS',
                'is_active': True,
                'is_default': True,
                'api_key': '',  # Will be set from environment
                'secret_key': '',  # Will be set from environment
                'api_url': 'https://apisms.beem.africa/v1/send',
                'cost_per_sms': 0.05,
                'currency': 'USD'
            }
        )
        
        if created:
            print("✅ Created Beem SMS provider")
        else:
            print("ℹ️  Beem SMS provider already exists")
        
        # Create sender ID
        sender_id, created = SMSSenderID.objects.get_or_create(
            tenant=tenant,
            sender_id='MIFUMO',
            defaults={
                'provider': provider,
                'sample_content': 'Hello from Mifumo WMS! This is a test message.',
                'status': 'active'
            }
        )
        
        if created:
            print("✅ Created sender ID: MIFUMO")
        else:
            print("ℹ️  Sender ID MIFUMO already exists")
        
        print(f"✅ Sender ID Status: {sender_id.status}")
        print(f"✅ Provider: {sender_id.provider.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up sender ID: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Setting up SMS Sender ID...")
    print("=" * 50)
    
    success = setup_sender_id()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Sender ID setup completed!")
        print("📱 You can now test SMS sending with sender ID: MIFUMO")
    else:
        print("❌ Sender ID setup failed!")
    print("=" * 50)

if __name__ == '__main__':
    main()
