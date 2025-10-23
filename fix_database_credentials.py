#!/usr/bin/env python3
"""
Fix database API credentials by updating them with environment variables
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

def fix_database_credentials():
    """Fix database API credentials by updating them with environment variables."""
    print("=" * 80)
    print("FIXING DATABASE API CREDENTIALS")
    print("=" * 80)
    
    try:
        # Get environment variables
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not api_key or not secret_key:
            print("ERROR: Environment variables not found!")
            return
        
        print(f"Environment API Key: {api_key[:10]}...")
        print(f"Environment Secret Key: {secret_key[:10]}...")
        
        # Get all Beem providers
        beem_providers = SMSProvider.objects.filter(provider_type='beem')
        
        print(f"\nFound {beem_providers.count()} Beem providers in database")
        
        updated_count = 0
        for provider in beem_providers:
            if not provider.api_key or not provider.secret_key:
                print(f"Updating provider: {provider.name} (ID: {provider.id})")
                provider.api_key = api_key
                provider.secret_key = secret_key
                provider.save()
                updated_count += 1
                print(f"  Updated API Key and Secret Key")
            else:
                print(f"Skipping provider: {provider.name} (already has credentials)")
        
        print(f"\nUpdated {updated_count} providers with environment credentials")
        
        # Test one provider
        print("\n" + "=" * 80)
        print("TESTING UPDATED PROVIDER")
        print("=" * 80)
        
        # Get the first updated provider
        test_provider = beem_providers.filter(api_key=api_key).first()
        if test_provider:
            print(f"Testing provider: {test_provider.name}")
            
            # Test using the working messaging system approach
            from messaging.services.sms_service import BeemSMSService
            
            beem_service = BeemSMSService(test_provider)
            print("BeemSMSService initialized successfully")
            
            # Test sending SMS
            phone_number = "255614853618"
            
            print(f"Sending SMS to: {phone_number}")
            print(f"Using sender ID: Taarifa-SMS")
            
            result = beem_service.send_sms(
                to=phone_number,
                message="Test message after fixing database credentials",
                sender_id="Taarifa-SMS",
                recipient_id="test_fixed_credentials"
            )
            
            print(f"Result: {result}")
            
            if result.get('success'):
                print("SUCCESS: SMS sent after fixing database credentials!")
            else:
                print("FAILED: SMS still not sent")
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Response: {result.get('response', {})}")
        else:
            print("No updated provider found for testing")
        
    except Exception as e:
        print(f"Error fixing credentials: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run credential fix."""
    print("Fixing Database API Credentials")
    print("=" * 80)
    
    fix_database_credentials()

if __name__ == "__main__":
    main()
