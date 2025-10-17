#!/usr/bin/env python3
"""
Quick SMS Test
Simple test to send one SMS message
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
    print("📱 Quick SMS Test")
    print("=" * 30)
    
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
    
    # Test phone number (replace with real number)
    test_phone = "+255614853618"  # Change this to a real number
    message = "Hello from Mifumo WMS! This is a test message."
    
    print(f"\n📤 Sending SMS to: {test_phone}")
    print(f"📝 Message: {message}")
    
    # Send SMS
    sms_service = SMSService()
    result = sms_service.send_sms(
        tenant=tenant,
        recipient_number=test_phone,
        message=message,
        sender_id=sender_id.sender_id,
        provider=provider
    )
    
    if result.get('success'):
        print("✅ SMS sent successfully!")
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
        print(f"   Cost: {result.get('cost', 'N/A')}")
    else:
        print(f"❌ SMS failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
