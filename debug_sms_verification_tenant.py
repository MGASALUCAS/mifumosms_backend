#!/usr/bin/env python3
"""
Debug SMS verification tenant issue
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.services.sms_verification import SMSVerificationService
from tenants.models import Tenant
from messaging.models_sms import SMSProvider

def debug_sms_verification_tenant():
    """Debug SMS verification tenant issue."""
    print("=" * 80)
    print("DEBUGGING SMS VERIFICATION TENANT ISSUE")
    print("=" * 80)
    
    try:
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found!")
            return
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Check SMS providers for this tenant
        providers = SMSProvider.objects.filter(tenant=tenant)
        print(f"Found {providers.count()} SMS providers for tenant {tenant.name}")
        
        for provider in providers:
            print(f"  Provider: {provider.name}")
            print(f"    Type: {provider.provider_type}")
            print(f"    Active: {provider.is_active}")
            print(f"    Default: {provider.is_default}")
            print(f"    API Key: {provider.api_key[:10] if provider.api_key else 'None'}...")
        
        # Test SMS verification service
        print("\n" + "=" * 80)
        print("TESTING SMS VERIFICATION SERVICE")
        print("=" * 80)
        
        sms_verification = SMSVerificationService(str(tenant.id))
        print(f"SMS Verification Service initialized with tenant ID: {sms_verification.tenant_id}")
        
        # Test sending verification code
        phone_number = "+255614853618"
        code = "123456"
        
        print(f"Sending verification SMS to: {phone_number}")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=code,
            message_type="verification"
        )
        
        print(f"SMS verification result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Verification SMS sent!")
        else:
            print("FAILED: Verification SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"Error debugging SMS verification: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging SMS Verification Tenant Issue")
    print("=" * 80)
    
    debug_sms_verification_tenant()

if __name__ == "__main__":
    main()
