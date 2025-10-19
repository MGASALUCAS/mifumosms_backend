#!/usr/bin/env python3
"""
Test Real SMS Functionality
Tests the actual SMS sending capability with real Beem API
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.beem_sms import BeemSMSService
from tenants.models import Tenant

def test_real_sms():
    """Test real SMS sending"""
    print("🧪 Testing Real SMS Functionality")
    print("=" * 40)
    
    try:
        # Get the first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("❌ No tenant found. Run setup_real_data.py first.")
            return
        
        print(f"🏢 Using tenant: {tenant.name}")
        
        # Initialize SMS service
        sms_service = BeemSMSService(tenant_id=tenant.id)
        
        # Test 1: Check account balance
        print("\n1. Checking account balance...")
        balance_result = sms_service.get_balance()
        if balance_result['success']:
            print(f"   ✅ Balance: {balance_result['balance']} {balance_result['currency']}")
        else:
            print(f"   ❌ Balance check failed: {balance_result['error']}")
        
        # Test 2: Get sender IDs
        print("\n2. Getting sender IDs...")
        sender_result = sms_service.get_sender_ids()
        if sender_result['success']:
            sender_ids = sender_result['sender_ids']
            print(f"   ✅ Found {len(sender_ids)} sender IDs:")
            for sender in sender_ids[:3]:  # Show first 3
                print(f"      - {sender.get('senderid', 'N/A')} ({sender.get('status', 'N/A')})")
        else:
            print(f"   ❌ Sender IDs check failed: {sender_result['error']}")
        
        # Test 3: Send test SMS
        print("\n3. Sending test SMS...")
        test_phone = input("Enter phone number to test (e.g., +255700000000): ").strip()
        
        if test_phone:
            test_message = "Hello! This is a test message from Mifumo SMS Backend. Your system is working correctly! 🚀"
            
            send_result = sms_service.send_sms(
                phone_number=test_phone,
                message=test_message,
                sender_id=getattr(settings, 'BEEM_DEFAULT_SENDER_ID', 'Taarifa-SMS')
            )
            
            if send_result['success']:
                print(f"   ✅ SMS sent successfully!")
                print(f"   📱 Request ID: {send_result.get('request_id')}")
                print(f"   📊 Valid recipients: {len(send_result.get('valid', []))}")
            else:
                print(f"   ❌ SMS sending failed: {send_result['error']}")
        else:
            print("   ⏭️  Skipping SMS test (no phone number provided)")
        
        # Test 4: Get delivery reports
        print("\n4. Getting delivery reports...")
        reports_result = sms_service.get_delivery_reports()
        if reports_result['success']:
            reports = reports_result['reports']
            print(f"   ✅ Found {len(reports)} delivery reports")
        else:
            print(f"   ❌ Delivery reports check failed: {reports_result['error']}")
        
        print("\n" + "=" * 40)
        print("🎉 SMS functionality test completed!")
        
    except Exception as e:
        print(f"❌ Error during SMS test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_sms()
