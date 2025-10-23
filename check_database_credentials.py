#!/usr/bin/env python3
"""
Check API credentials stored in the database
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.models_sms import SMSProvider
from django.conf import settings

def check_database_credentials():
    """Check API credentials stored in the database."""
    print("=" * 80)
    print("CHECKING DATABASE API CREDENTIALS")
    print("=" * 80)
    
    try:
        # Get all SMS providers
        providers = SMSProvider.objects.all()
        
        print(f"Found {providers.count()} SMS providers in database:")
        
        for provider in providers:
            print(f"\nProvider: {provider.name}")
            print(f"  ID: {provider.id}")
            print(f"  Type: {provider.provider_type}")
            print(f"  Active: {provider.is_active}")
            print(f"  Default: {provider.is_default}")
            print(f"  API Key: {provider.api_key[:10]}..." if provider.api_key else "  API Key: None")
            print(f"  Secret Key: {provider.secret_key[:10]}..." if provider.secret_key else "  Secret Key: None")
            print(f"  API URL: {provider.api_url}")
            print(f"  Tenant: {provider.tenant.name if provider.tenant else 'None'}")
        
        # Check environment variables
        print("\n" + "=" * 80)
        print("CHECKING ENVIRONMENT VARIABLES")
        print("=" * 80)
        
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        print(f"BEEM_API_KEY: {api_key[:10]}..." if api_key else "BEEM_API_KEY: None")
        print(f"BEEM_SECRET_KEY: {secret_key[:10]}..." if secret_key else "BEEM_SECRET_KEY: None")
        
        # Check if database credentials match environment
        print("\n" + "=" * 80)
        print("COMPARING DATABASE VS ENVIRONMENT")
        print("=" * 80)
        
        for provider in providers:
            if provider.provider_type == 'beem':
                db_api_key = provider.api_key
                db_secret_key = provider.secret_key
                
                print(f"\nProvider: {provider.name}")
                print(f"  Database API Key matches Environment: {db_api_key == api_key}")
                print(f"  Database Secret Key matches Environment: {db_secret_key == secret_key}")
                
                if db_api_key != api_key or db_secret_key != secret_key:
                    print("  ⚠️  MISMATCH: Database credentials don't match environment variables!")
                    print("  This could be why SMS sending is failing.")
                    
                    # Update database with environment credentials
                    print("  Updating database with environment credentials...")
                    provider.api_key = api_key
                    provider.secret_key = secret_key
                    provider.save()
                    print("  ✅ Database updated with environment credentials!")
                else:
                    print("  ✅ Database credentials match environment variables!")
        
    except Exception as e:
        print(f"Error checking credentials: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run credential check."""
    print("Checking Database API Credentials")
    print("=" * 80)
    
    check_database_credentials()

if __name__ == "__main__":
    main()
