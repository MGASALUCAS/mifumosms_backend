#!/usr/bin/env python3
"""
Check ZenoPay Configuration
==========================

This script checks if ZenoPay is properly configured for real payments.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def check_zenopay_config():
    """Check ZenoPay configuration"""
    print("ZenoPay Configuration Check")
    print("=" * 40)
    
    # Check environment variables
    print("\n1. Environment Variables:")
    
    zenopay_api_key = getattr(settings, 'ZENOPAY_API_KEY', None)
    zenopay_timeout = getattr(settings, 'ZENOPAY_API_TIMEOUT', 30)
    zenopay_webhook_secret = getattr(settings, 'ZENOPAY_WEBHOOK_SECRET', None)
    base_url = getattr(settings, 'BASE_URL', None)
    
    print(f"   ZENOPAY_API_KEY: {'Set' if zenopay_api_key else 'Not set'}")
    print(f"   ZENOPAY_API_TIMEOUT: {zenopay_timeout}")
    print(f"   ZENOPAY_WEBHOOK_SECRET: {'Set' if zenopay_webhook_secret else 'Not set'}")
    print(f"   BASE_URL: {base_url if base_url else 'Not set'}")
    
    # Check if API key is valid
    if zenopay_api_key:
        print(f"   API Key (first 10 chars): {zenopay_api_key[:10]}...")
        
        # Test ZenoPay service
        print("\n2. Testing ZenoPay Service:")
        
        try:
            from billing.zenopay_service import ZenoPayService
            zenopay_service = ZenoPayService()
            
            print("   SUCCESS: ZenoPayService imported successfully")
            print(f"   SUCCESS: API Key configured: {zenopay_service.api_key[:10]}...")
            print(f"   SUCCESS: Base URL: {zenopay_service.base_url}")
            print(f"   SUCCESS: Timeout: {zenopay_service.timeout}s")
            
            # Test phone number validation
            test_phone = "0744963858"
            validated_phone = zenopay_service._validate_phone_number(test_phone)
            print(f"   SUCCESS: Phone validation test: {test_phone} -> {validated_phone}")
            
        except Exception as e:
            print(f"   ERROR: Error testing ZenoPayService: {str(e)}")
    else:
        print("\n2. ZenoPay Service:")
        print("   ERROR: Cannot test service - API key not configured")
    
    # Check webhook URL
    print("\n3. Webhook Configuration:")
    if base_url:
        webhook_url = f"{base_url}/api/billing/payments/webhook/"
        print(f"   SUCCESS: Webhook URL: {webhook_url}")
    else:
        print("   ERROR: BASE_URL not set - webhook URL cannot be determined")
    
    # Summary
    print("\n4. Configuration Summary:")
    
    if zenopay_api_key and base_url:
        print("   SUCCESS: ZenoPay is properly configured for real payments")
        print("   SUCCESS: You can initiate real payments that will trigger push notifications")
    elif zenopay_api_key:
        print("   WARNING: ZenoPay API key is set but BASE_URL is missing")
        print("   WARNING: Payments will be simulated (no real push notifications)")
    else:
        print("   ERROR: ZenoPay is not configured for real payments")
        print("   ERROR: Payments will be simulated (no real push notifications)")
    
    print("\n5. Next Steps:")
    
    if zenopay_api_key and base_url:
        print("   SUCCESS: You can run the real payment test")
        print("   Run: python test_real_payment_simple.py")
    else:
        print("   To enable real payments:")
        print("   1. Set ZENOPAY_API_KEY in your environment")
        print("   2. Set BASE_URL in your environment")
        print("   3. Restart the server")
        print("   4. Run: python test_real_payment_simple.py")

def main():
    check_zenopay_config()

if __name__ == '__main__':
    main()
