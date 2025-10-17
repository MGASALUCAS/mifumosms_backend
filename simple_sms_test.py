#!/usr/bin/env python3
"""
Simple SMS Test - Fixed Version
This script tests SMS sending with correct method signatures
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID
from messaging.services.sms_service import SMSService

def main():
    print("📱 Simple SMS Test - Fixed Version")
    print("=" * 40)
    
    # Get tenant and provider
    tenant = Tenant.objects.filter(subdomain='default').first()
    if not tenant:
        print("❌ No tenant found!")
        return
    
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    if not provider:
        print("❌ No SMS provider found!")
        return
    
    sender_id = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
    if not sender_id:
        print("❌ No sender ID found!")
        return
    
    print(f"✅ Tenant: {tenant.name}")
    print(f"✅ Provider: {provider.name}")
    print(f"✅ Sender ID: {sender_id.sender_id}")
    
    # Test phone number
    test_phone = "+255614853618"
    message = "Hello from Mifumo WMS! This is a test message."
    
    print(f"\n📤 Sending SMS to: {test_phone}")
    print(f"📝 Message: {message}")
    
    try:
        # Send SMS with correct method signature
        sms_service = SMSService(tenant_id=str(tenant.id))
        result = sms_service.send_sms(
            to=test_phone,
            message=message,
            sender_id=sender_id.sender_id
        )
        
        if result.get('success'):
            print("✅ SMS sent successfully!")
            print(f"   Message ID: {result.get('message_id', 'N/A')}")
            print(f"   Cost: {result.get('cost', 'N/A')}")
        else:
            print(f"❌ SMS failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ SMS sending failed with exception: {e}")

if __name__ == "__main__":
    main()
