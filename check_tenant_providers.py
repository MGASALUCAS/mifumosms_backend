#!/usr/bin/env python3
"""
Check SMS providers for specific tenant
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

def check_tenant_providers():
    """Check SMS providers for specific tenant."""
    print("=" * 80)
    print("CHECKING SMS PROVIDERS FOR TENANT")
    print("=" * 80)
    
    try:
        # Get the user from the test (admin@mifumo.com)
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        tenant = user.get_tenant()
        print(f"User: {user.email}")
        print(f"Tenant: {tenant.name} (ID: {tenant.id})")
        
        # Check SMS providers for this tenant
        providers = SMSProvider.objects.filter(tenant=tenant)
        print(f"Found {providers.count()} SMS providers for tenant {tenant.name}")
        
        for provider in providers:
            print(f"\nProvider: {provider.name}")
            print(f"  ID: {provider.id}")
            print(f"  Type: {provider.provider_type}")
            print(f"  Active: {provider.is_active}")
            print(f"  Default: {provider.is_default}")
            print(f"  API Key: {provider.api_key[:10] if provider.api_key else 'None'}...")
            print(f"  Secret Key: {provider.secret_key[:10] if provider.secret_key else 'None'}...")
            print(f"  API URL: {provider.api_url}")
        
        # Check environment variables
        print("\n" + "=" * 80)
        print("ENVIRONMENT VARIABLES")
        print("=" * 80)
        
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        print(f"BEEM_API_KEY: {api_key[:10]}..." if api_key else "BEEM_API_KEY: None")
        print(f"BEEM_SECRET_KEY: {secret_key[:10]}..." if secret_key else "BEEM_SECRET_KEY: None")
        
        # Check if database credentials match environment
        print("\n" + "=" * 80)
        print("COMPARING CREDENTIALS")
        print("=" * 80)
        
        for provider in providers:
            if provider.provider_type == 'beem':
                db_api_key = provider.api_key
                db_secret_key = provider.secret_key
                
                print(f"\nProvider: {provider.name}")
                print(f"  Database API Key matches Environment: {db_api_key == api_key}")
                print(f"  Database Secret Key matches Environment: {db_secret_key == secret_key}")
                
                if db_api_key != api_key or db_secret_key != secret_key:
                    print("  MISMATCH: Database credentials don't match environment variables!")
                    print("  Updating database with environment credentials...")
                    provider.api_key = api_key
                    provider.secret_key = secret_key
                    provider.save()
                    print("  Database updated with environment credentials!")
                else:
                    print("  Database credentials match environment variables!")
        
    except Exception as e:
        print(f"Error checking tenant providers: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run check."""
    print("Checking SMS Providers for Tenant")
    print("=" * 80)
    
    check_tenant_providers()

if __name__ == "__main__":
    main()
