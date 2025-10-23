#!/usr/bin/env python3
"""
Fix SMS provider for admin9@mifumo.com user
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from messaging.models_sms import SMSProvider
from django.conf import settings

def fix_admin9_sms():
    """Fix SMS provider for admin9@mifumo.com user."""
    print("=" * 80)
    print("FIXING SMS PROVIDER FOR ADMIN9@MIFUMO.COM USER")
    print("=" * 80)
    
    try:
        # Get the admin9 user
        user = User.objects.filter(phone_number='0614853618').first()
        if not user:
            print("User with phone 0614853618 not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Tenant: {user.get_tenant().name}")
        
        # Get or create SMS provider for this tenant
        tenant = user.get_tenant()
        provider = SMSProvider.objects.filter(tenant=tenant).first()
        
        if provider:
            print(f"Found existing provider: {provider.name}")
            print(f"Current API Key: {provider.api_key[:10] if provider.api_key else 'None'}...")
            print(f"Current Secret Key: {provider.secret_key[:10] if provider.secret_key else 'None'}...")
            
            # Update with correct credentials
            provider.api_key = getattr(settings, 'BEEM_API_KEY', None)
            provider.secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
            provider.save()
            
            print("Updated provider with correct credentials!")
        else:
            print("No provider found, creating one...")
            provider = SMSProvider.objects.create(
                tenant=tenant,
                name='Beem Africa Provider',
                provider_type='beem',
                api_key=getattr(settings, 'BEEM_API_KEY', None),
                secret_key=getattr(settings, 'BEEM_SECRET_KEY', None),
                api_url='https://apisms.beem.africa/v1',
                is_active=True,
                is_default=True
            )
            print("Created new provider with correct credentials!")
        
        print(f"Provider API Key: {provider.api_key[:10]}...")
        print(f"Provider Secret Key: {provider.secret_key[:10]}...")
        
    except Exception as e:
        print(f"Error fixing admin9 SMS: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run fix."""
    print("Fixing SMS Provider for admin9@mifumo.com User")
    print("=" * 80)
    
    fix_admin9_sms()

if __name__ == "__main__":
    main()
