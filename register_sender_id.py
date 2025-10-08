#!/usr/bin/env python
"""
Script to register SMS sender IDs in the database.
This ensures sender IDs are available for the API validation.
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

def register_sender_id():
    """Register Taarifa-SMS sender ID for the admin tenant."""
    try:
        # Get the admin tenant
        tenant = Tenant.objects.filter(subdomain='admin').first()
        if not tenant:
            print("❌ No admin tenant found. Please run create_superuser.py first.")
            return False
        
        # Get or create Beem provider
        provider, created = SMSProvider.objects.get_or_create(
            tenant=tenant,
            provider_type='beem',
            defaults={
                'name': 'Beem Africa SMS',
                'api_key': '',  # Will use environment variables
                'secret_key': '',  # Will use environment variables
                'api_url': 'https://apisms.beem.africa/v1/send',
                'is_active': True,
                'is_default': True,
                'cost_per_sms': 0.05,
                'currency': 'USD'
            }
        )
        
        if created:
            print("✅ Created Beem SMS provider")
        else:
            print("ℹ️  Beem SMS provider already exists")
        
        # Register Taarifa-SMS sender ID
        sender_id, created = SMSSenderID.objects.get_or_create(
            tenant=tenant,
            sender_id='Taarifa-SMS',
            defaults={
                'provider': provider,
                'sample_content': 'This is a test message from Taarifa-SMS',
                'status': 'active',
                'provider_sender_id': 'Taarifa-SMS',
                'provider_data': {}
            }
        )
        
        if created:
            print("✅ Registered 'Taarifa-SMS' sender ID")
        else:
            # Update existing sender ID to active
            sender_id.status = 'active'
            sender_id.save()
            print("✅ Updated 'Taarifa-SMS' sender ID to active")
        
        # Also register MIFUMO as backup
        mifumo_sender, created = SMSSenderID.objects.get_or_create(
            tenant=tenant,
            sender_id='MIFUMO',
            defaults={
                'provider': provider,
                'sample_content': 'This is a test message from MIFUMO',
                'status': 'active',
                'provider_sender_id': 'MIFUMO',
                'provider_data': {}
            }
        )
        
        if created:
            print("✅ Registered 'MIFUMO' sender ID")
        else:
            mifumo_sender.status = 'active'
            mifumo_sender.save()
            print("✅ Updated 'MIFUMO' sender ID to active")
        
        print("\n🎉 Sender ID registration completed!")
        print(f"📱 Available sender IDs for tenant '{tenant.name}':")
        
        active_senders = SMSSenderID.objects.filter(tenant=tenant, status='active')
        for sender in active_senders:
            print(f"   - {sender.sender_id} ({sender.status})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error registering sender ID: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Registering SMS sender IDs...")
    print("=" * 50)
    
    success = register_sender_id()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("📱 You can now use 'Taarifa-SMS' or 'MIFUMO' as sender_id in your API calls.")
    else:
        print("\n❌ Setup failed!")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
