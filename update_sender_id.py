#!/usr/bin/env python
"""
Script to update sender ID to match the working Beem credentials.
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

def update_sender_id():
    """Update sender ID to match working Beem credentials."""
    print("🔧 Updating SMS Sender ID...")
    
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
                'api_key': '62f8c3a2cb510335',  # Your working API key
                'secret_key': 'YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ==',  # Your working secret
                'api_url': 'https://apisms.beem.africa/v1/send',
                'cost_per_sms': 0.05,
                'currency': 'USD'
            }
        )
        
        if created:
            print("✅ Created Beem SMS provider with your credentials")
        else:
            # Update existing provider with your credentials
            provider.api_key = '62f8c3a2cb510335'
            provider.secret_key = 'YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ=='
            provider.save()
            print("✅ Updated Beem SMS provider with your credentials")
        
        # Update or create sender ID
        sender_id, created = SMSSenderID.objects.update_or_create(
            tenant=tenant,
            sender_id='Taarifa-SMS',
            defaults={
                'provider': provider,
                'sample_content': 'SMS Test from Python API',
                'status': 'active'
            }
        )
        
        if created:
            print("✅ Created sender ID: Taarifa-SMS")
        else:
            print("✅ Updated sender ID: Taarifa-SMS")
        
        print(f"✅ Sender ID Status: {sender_id.status}")
        print(f"✅ Provider: {sender_id.provider.name}")
        print(f"✅ API Key: {sender_id.provider.api_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating sender ID: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Updating SMS Configuration...")
    print("=" * 50)
    
    success = update_sender_id()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SMS configuration updated successfully!")
        print("📱 You can now test SMS sending with sender ID: Taarifa-SMS")
        print("🔑 Using your working Beem API credentials")
    else:
        print("❌ SMS configuration update failed!")
    print("=" * 50)

if __name__ == '__main__':
    main()
