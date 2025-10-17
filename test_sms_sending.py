#!/usr/bin/env python3
"""
Test SMS Sending Functionality
This script tests the complete SMS sending process
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID, SMSTemplate, SMSMessage
from messaging.models import Message, Contact
from messaging.services.sms_service import SMSService
from django.utils import timezone
import json

User = get_user_model()

def test_sms_provider():
    """Test SMS provider configuration"""
    print("📱 Testing SMS Provider Configuration")
    print("-" * 40)
    
    try:
        # Get default tenant
        tenant = Tenant.objects.filter(subdomain='default').first()
        if not tenant:
            print("❌ No default tenant found!")
            return False
        
        print(f"✅ Tenant: {tenant.name}")
        
        # Get SMS provider
        provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
        if not provider:
            print("❌ No active SMS provider found!")
            return False
        
        print(f"✅ SMS Provider: {provider.name} ({provider.provider_type})")
        print(f"   API URL: {provider.api_url}")
        print(f"   Cost per SMS: {provider.cost_per_sms} {provider.currency}")
        
        # Get sender ID
        sender_id = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
        if not sender_id:
            print("❌ No active sender ID found!")
            return False
        
        print(f"✅ Sender ID: {sender_id.sender_id}")
        
        return True
    except Exception as e:
        print(f"❌ SMS provider test failed: {e}")
        return False

def test_beem_connection():
    """Test connection to Beem SMS API"""
    print("\n🔗 Testing Beem API Connection")
    print("-" * 40)
    
    try:
        from messaging.services.sms_service import BeemSMSService
        
        # Get provider for Beem service
        tenant = Tenant.objects.filter(subdomain='default').first()
        provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
        
        if not provider:
            print("❌ No SMS provider found for Beem test")
            return False
        
        # Initialize Beem service
        beem_service = BeemSMSService(provider)
        
        # Test balance check
        print("💰 Checking Beem balance...")
        balance_response = beem_service.check_balance()
        
        if balance_response.get('success'):
            balance = balance_response.get('data', {}).get('balance', 'Unknown')
            print(f"✅ Beem balance: {balance}")
        else:
            print(f"⚠️  Balance check failed: {balance_response.get('error', 'Unknown error')}")
        
        return True
    except Exception as e:
        print(f"❌ Beem connection test failed: {e}")
        return False

def test_sms_sending():
    """Test actual SMS sending"""
    print("\n📤 Testing SMS Sending")
    print("-" * 40)
    
    try:
        # Get required objects
        tenant = Tenant.objects.filter(subdomain='default').first()
        provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
        sender_id = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
        
        if not all([tenant, provider, sender_id]):
            print("❌ Missing required objects for SMS sending")
            return False
        
        # Create a test contact
        test_phone = "+255614853618"  # Replace with a real test number
        contact, created = Contact.objects.get_or_create(
            phone_e164=test_phone,
            created_by=User.objects.filter(is_superuser=True).first(),
            defaults={
                'name': 'Test Contact',
                'email': 'test@example.com',
            }
        )
        
        if created:
            print(f"✅ Created test contact: {contact.name} ({contact.phone_e164})")
        else:
            print(f"ℹ️  Using existing contact: {contact.name} ({contact.phone_e164})")
        
        # Create a test message
        message_text = "Hello from Mifumo WMS! This is a test message. Reply STOP to opt out."
        
        # Create base message
        base_message = Message.objects.create(
            tenant=tenant,
            direction='out',
            provider='sms',
            text=message_text,
            recipient_number=test_phone,
            status='queued',
        )
        
        print(f"✅ Created base message: {base_message.id}")
        
        # Create SMS message
        sms_message = SMSMessage.objects.create(
            tenant=tenant,
            base_message=base_message,
            provider=provider,
            sender_id=sender_id,
            status='queued',
            cost_amount=provider.cost_per_sms,
            cost_currency=provider.currency,
        )
        
        print(f"✅ Created SMS message: {sms_message.id}")
        
        # Test SMS service
        sms_service = SMSService(tenant_id=str(tenant.id))
        
        print("🚀 Sending SMS...")
        send_result = sms_service.send_sms(
            to=test_phone,
            message=message_text,
            sender_id=sender_id.sender_id
        )
        
        if send_result.get('success'):
            print("✅ SMS sent successfully!")
            print(f"   Provider Message ID: {send_result.get('message_id', 'N/A')}")
            print(f"   Cost: {send_result.get('cost', 'N/A')}")
            
            # Update message status
            sms_message.status = 'sent'
            sms_message.provider_message_id = send_result.get('message_id', '')
            sms_message.sent_at = timezone.now()
            sms_message.save()
            
            base_message.status = 'sent'
            base_message.sent_at = timezone.now()
            base_message.save()
            
            print("✅ Message status updated to 'sent'")
            
        else:
            print(f"❌ SMS sending failed: {send_result.get('error', 'Unknown error')}")
            
            # Update message status
            sms_message.status = 'failed'
            sms_message.error_message = send_result.get('error', 'Unknown error')
            sms_message.failed_at = timezone.now()
            sms_message.save()
            
            base_message.status = 'failed'
            base_message.error_message = send_result.get('error', 'Unknown error')
            base_message.save()
            
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ SMS sending test failed: {e}")
        return False

def test_api_endpoints():
    """Test SMS API endpoints"""
    print("\n🌐 Testing SMS API Endpoints")
    print("-" * 40)
    
    try:
        from django.test import Client
        
        client = Client()
        
        # Test endpoints
        endpoints = [
            '/api/messaging/sms/send/',
            '/api/messaging/sms/providers/',
            '/api/messaging/sms/sender-ids/',
            '/api/messaging/sms/templates/',
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            status = "✅" if response.status_code in [200, 401, 403] else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def main():
    print("🧪 SMS Sending Test Suite")
    print("=" * 50)
    
    # Test 1: SMS Provider Configuration
    provider_ok = test_sms_provider()
    
    # Test 2: Beem API Connection
    connection_ok = test_beem_connection()
    
    # Test 3: API Endpoints
    api_ok = test_api_endpoints()
    
    # Test 4: SMS Sending (only if provider is configured)
    if provider_ok:
        sending_ok = test_sms_sending()
    else:
        print("\n⏭️  Skipping SMS sending test (provider not configured)")
        sending_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"SMS Provider Config: {'✅ PASS' if provider_ok else '❌ FAIL'}")
    print(f"Beem API Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"SMS Sending: {'✅ PASS' if sending_ok else '❌ FAIL'}")
    
    if all([provider_ok, connection_ok, api_ok]):
        print("\n🎉 All tests passed! SMS functionality is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("\n💡 To test with a real phone number:")
    print("1. Update the test_phone variable in the script")
    print("2. Make sure the number is in international format (+255xxxxxxxxx)")
    print("3. Run the script again")

if __name__ == "__main__":
    main()
