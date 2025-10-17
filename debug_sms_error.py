#!/usr/bin/env python3
"""
Debug SMS Error
This script helps debug the SMS sending error
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID
from messaging.services.sms_service import SMSService, BeemSMSService
import traceback

def debug_sms_error():
    print("🔍 Debugging SMS Error")
    print("=" * 30)
    
    # Get tenant and provider
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    sender_id = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
    
    print(f"✅ Tenant: {tenant.name}")
    print(f"✅ Provider: {provider.name}")
    print(f"✅ Sender ID: {sender_id.sender_id}")
    
    # Test phone number
    test_phone = "+255614853618"
    message = "Hello from Mifumo WMS! This is a test message."
    
    print(f"\n📤 Testing SMS to: {test_phone}")
    print(f"📝 Message: {message}")
    
    try:
        # Test Beem service directly
        print("\n🔧 Testing BeemSMSService directly...")
        beem_service = BeemSMSService(provider)
        
        # Test balance first
        print("💰 Checking balance...")
        balance_result = beem_service.check_balance()
        print(f"Balance result: {balance_result}")
        
        # Test sending SMS
        print("\n📤 Sending SMS via BeemSMSService...")
        sms_result = beem_service.send_sms(
            to=test_phone,
            message=message,
            sender_id=sender_id.sender_id
        )
        print(f"SMS result: {sms_result}")
        
    except Exception as e:
        print(f"❌ BeemSMSService error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
    
    try:
        # Test SMSService
        print("\n🔧 Testing SMSService...")
        sms_service = SMSService(tenant_id=str(tenant.id))
        
        sms_result = sms_service.send_sms(
            to=test_phone,
            message=message,
            sender_id=sender_id.sender_id
        )
        print(f"SMSService result: {sms_result}")
        
    except Exception as e:
        print(f"❌ SMSService error: {e}")
        print(f"Traceback: {traceback.format_exc()}")

def check_beem_config():
    print("\n🔧 Checking Beem Configuration")
    print("=" * 40)
    
    from django.conf import settings
    
    print(f"BEEM_API_KEY: {getattr(settings, 'BEEM_API_KEY', 'Not set')}")
    print(f"BEEM_SECRET_KEY: {getattr(settings, 'BEEM_SECRET_KEY', 'Not set')[:20]}...")
    print(f"BEEM_SEND_URL: {getattr(settings, 'BEEM_SEND_URL', 'Not set')}")
    
    # Check provider settings
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    
    if provider:
        print(f"\nProvider API Key: {provider.api_key}")
        print(f"Provider Secret: {provider.secret_key[:20]}...")
        print(f"Provider URL: {provider.api_url}")
        print(f"Provider Settings: {provider.settings}")

def main():
    print("🐛 SMS Error Debugger")
    print("=" * 40)
    
    check_beem_config()
    debug_sms_error()
    
    print("\n💡 If you see 'Unknown error', check:")
    print("1. Beem API credentials are correct")
    print("2. Network connectivity to Beem API")
    print("3. Phone number format is correct")
    print("4. Sender ID is registered with Beem")

if __name__ == "__main__":
    main()
