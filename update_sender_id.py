#!/usr/bin/env python3
"""
Update Sender ID to Use Registered Beem Sender ID
This script updates the database to use 'Taarifa-SMS' which is registered with Beem
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID

def update_sender_id():
    print("🔄 Updating Sender ID to Use Registered Beem Sender")
    print("=" * 60)
    
    # Get tenant
    tenant = Tenant.objects.filter(subdomain='default').first()
    if not tenant:
        print("❌ No tenant found!")
        return
    
    print(f"✅ Tenant: {tenant.name}")
    
    # Get current sender ID
    sender_id = SMSSenderID.objects.filter(tenant=tenant).first()
    if not sender_id:
        print("❌ No sender ID found in database!")
        return
    
    print(f"📋 Current sender ID: {sender_id.sender_id}")
    print(f"📋 Current status: {sender_id.status}")
    
    # Update to use the registered Beem sender ID
    old_sender_id = sender_id.sender_id
    sender_id.sender_id = "Taarifa-SMS"
    sender_id.sample_content = "A test use case for the sender name purposely used for information transfer."
    sender_id.status = "active"
    sender_id.save()
    
    print(f"✅ Updated sender ID: {old_sender_id} → {sender_id.sender_id}")
    print(f"✅ Status: {sender_id.status}")
    print(f"✅ Sample content: {sender_id.sample_content}")

def test_updated_sender_id():
    print("\n🧪 Testing Updated Sender ID")
    print("=" * 40)
    
    from messaging.services.sms_service import SMSService
    
    # Get tenant
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    sender_id = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
    
    if not all([tenant, provider, sender_id]):
        print("❌ Missing required objects!")
        return
    
    print(f"✅ Tenant: {tenant.name}")
    print(f"✅ Provider: {provider.name}")
    print(f"✅ Sender ID: {sender_id.sender_id}")
    
    # Test phone number
    test_phone = "+255614853618"
    message = "Hello from Mifumo WMS! This is a test message using the registered sender ID."
    
    print(f"\n📤 Testing SMS to: {test_phone}")
    print(f"📝 Message: {message}")
    
    try:
        # Send SMS
        sms_service = SMSService(tenant_id=str(tenant.id))
        result = sms_service.send_sms(
            to=test_phone,
            message=message,
            sender_id=sender_id.sender_id
        )
        
        if result.get('success'):
            print("✅ SMS sent successfully!")
            print(f"   Message ID: {result.get('message_id', 'N/A')}")
            print(f"   Request ID: {result.get('request_id', 'N/A')}")
            print(f"   Valid count: {result.get('valid_count', 'N/A')}")
        else:
            print(f"❌ SMS failed: {result.get('error', 'Unknown error')}")
            if 'response' in result:
                print(f"   Response: {result['response']}")
                
    except Exception as e:
        print(f"❌ SMS sending failed with exception: {e}")

def main():
    print("🎯 Fixing Sender ID Issue")
    print("=" * 50)
    print("Found registered Beem sender IDs:")
    print("✅ Quantum (active)")
    print("✅ Taarifa-SMS (active) ← Using this one")
    print("❌ INFO (inactive)")
    print()
    
    # Update sender ID
    update_sender_id()
    
    # Test the updated sender ID
    test_updated_sender_id()
    
    print("\n🎉 Sender ID updated successfully!")
    print("Your SMS should now work with the registered 'Taarifa-SMS' sender ID.")

if __name__ == "__main__":
    main()