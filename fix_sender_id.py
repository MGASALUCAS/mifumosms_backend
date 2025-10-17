#!/usr/bin/env python3
"""
Fix Sender ID Issue
This script helps register a valid sender ID with Beem
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID
import requests
import base64
import json

def check_beem_sender_ids():
    """Check what sender IDs are available with Beem"""
    print("🔍 Checking Beem Sender IDs")
    print("=" * 40)
    
    # Get provider
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    
    if not provider:
        print("❌ No provider found!")
        return
    
    # Sender IDs URL
    sender_url = provider.settings.get('sender_url', 'https://apisms.beem.africa/public/v1/sender-names')
    
    # Prepare headers
    auth_string = f"{provider.api_key}:{provider.secret_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}'
    }
    
    try:
        response = requests.get(sender_url, headers=headers, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            
            # Check if there are any sender IDs
            if 'data' in data and isinstance(data['data'], list):
                print(f"\n✅ Found {len(data['data'])} sender IDs:")
                for sender in data['data']:
                    print(f"   - {sender.get('name', 'Unknown')} (Status: {sender.get('status', 'Unknown')})")
            else:
                print("❌ No sender IDs found or unexpected response format")
        else:
            print(f"❌ Failed to get sender IDs: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking sender IDs: {e}")

def register_sender_id():
    """Register a new sender ID with Beem"""
    print("\n📝 Registering New Sender ID")
    print("=" * 40)
    
    # Get provider
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    
    if not provider:
        print("❌ No provider found!")
        return
    
    # Sender registration URL
    sender_url = provider.settings.get('sender_url', 'https://apisms.beem.africa/public/v1/sender-names')
    
    # Prepare headers
    auth_string = f"{provider.api_key}:{provider.secret_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_b64}'
    }
    
    # Sender ID data
    sender_data = {
        "name": "MIFUMO",
        "sample_content": "Hello from Mifumo WMS! This is a test message to verify our sender ID."
    }
    
    print(f"📋 Sender Data: {json.dumps(sender_data, indent=2)}")
    
    try:
        response = requests.post(sender_url, json=sender_data, headers=headers, timeout=30)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            print(f"✅ Sender ID registered successfully!")
            print(f"📊 Response: {json.dumps(data, indent=2)}")
        else:
            data = response.json() if response.content else {}
            print(f"❌ Failed to register sender ID: {response.status_code}")
            print(f"📊 Response: {json.dumps(data, indent=2)}")
            
    except Exception as e:
        print(f"❌ Error registering sender ID: {e}")

def update_sender_id_status():
    """Update the sender ID status in our database"""
    print("\n🔄 Updating Sender ID Status")
    print("=" * 40)
    
    tenant = Tenant.objects.filter(subdomain='default').first()
    sender_id = SMSSenderID.objects.filter(tenant=tenant, sender_id='MIFUMO').first()
    
    if sender_id:
        # For now, let's try a different approach - use a generic sender ID
        print("🔄 Trying alternative approach...")
        
        # Update to use a generic sender ID that might work
        sender_id.sender_id = "SMS"
        sender_id.sample_content = "Hello from Mifumo WMS!"
        sender_id.status = 'active'
        sender_id.save()
        
        print(f"✅ Updated sender ID to: {sender_id.sender_id}")
        print("ℹ️  Note: 'SMS' is a generic sender ID that might work")
    else:
        print("❌ No sender ID found in database")

def test_alternative_sender_ids():
    """Test with alternative sender IDs"""
    print("\n🧪 Testing Alternative Sender IDs")
    print("=" * 40)
    
    # Common sender IDs that might work
    alternative_senders = ["SMS", "INFO", "ALERT", "NOTIFY"]
    
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    
    for sender in alternative_senders:
        print(f"\n📤 Testing sender ID: {sender}")
        
        # Test phone number
        test_phone = "+255614853618"
        message = f"Test message from {sender}"
        
        # Prepare request data
        recipients = [{
            "recipient_id": 1,
            "dest_addr": test_phone
        }]
        
        data = {
            "source_addr": sender,
            "message": message,
            "encoding": 0,
            "recipients": recipients
        }
        
        # Prepare headers
        auth_string = f"{provider.api_key}:{provider.secret_key}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_b64}'
        }
        
        try:
            response = requests.post(provider.api_url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('successful'):
                    print(f"✅ {sender} works! Request ID: {response_data.get('request_id')}")
                    return sender
                else:
                    print(f"❌ {sender} failed: {response_data.get('message', 'Unknown error')}")
            else:
                print(f"❌ {sender} failed: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {sender} error: {e}")
    
    return None

def main():
    print("🔧 Fixing Sender ID Issue")
    print("=" * 40)
    
    print("The issue is: Sender ID 'MIFUMO' is not registered with Beem Africa")
    print("Error Code 111: Invalid Sender Id")
    print()
    
    # Check current sender IDs
    check_beem_sender_ids()
    
    # Try to register sender ID
    register_sender_id()
    
    # Test alternative sender IDs
    working_sender = test_alternative_sender_ids()
    
    if working_sender:
        print(f"\n🎉 Found working sender ID: {working_sender}")
        print("Update your database to use this sender ID")
    else:
        print("\n⚠️  No working sender ID found")
        print("You may need to:")
        print("1. Contact Beem Africa support to register 'MIFUMO'")
        print("2. Use a different sender ID")
        print("3. Check Beem Africa documentation for valid sender IDs")

if __name__ == "__main__":
    main()
