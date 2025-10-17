#!/usr/bin/env python3
"""
Test Beem API Directly
This script tests the Beem API directly to see the actual error
"""

import os
import sys
import django
import requests
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant
from messaging.models_sms import SMSProvider, SMSSenderID

def test_beem_api_direct():
    print("🔧 Testing Beem API Directly")
    print("=" * 40)
    
    # Get provider
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    sender_id = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
    
    if not provider:
        print("❌ No provider found!")
        return
    
    print(f"✅ Provider: {provider.name}")
    print(f"✅ API Key: {provider.api_key}")
    print(f"✅ Secret Key: {provider.secret_key[:20]}...")
    print(f"✅ API URL: {provider.api_url}")
    
    # Test phone number
    test_phone = "+255614853618"
    message = "Hello from Mifumo WMS! This is a test message."
    
    print(f"\n📤 Testing SMS to: {test_phone}")
    print(f"📝 Message: {message}")
    
    # Prepare request data
    recipients = [{
        "recipient_id": 1,
        "dest_addr": test_phone
    }]
    
    data = {
        "source_addr": sender_id.sender_id,
        "message": message,
        "encoding": 0,
        "recipients": recipients
    }
    
    print(f"\n📋 Request data: {json.dumps(data, indent=2)}")
    
    # Prepare headers
    import base64
    auth_string = f"{provider.api_key}:{provider.secret_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_b64}'
    }
    
    print(f"\n🔑 Headers: {json.dumps(headers, indent=2)}")
    
    try:
        # Make API request
        print(f"\n🚀 Making request to: {provider.api_url}")
        response = requests.post(
            provider.api_url,
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📊 Response JSON: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📊 Response Text: {response.text}")
        
        # Analyze response
        if response.status_code == 200:
            if response_data.get('successful'):
                print("✅ SMS sent successfully!")
                print(f"   Request ID: {response_data.get('request_id')}")
                print(f"   Valid: {response_data.get('valid', 0)}")
                print(f"   Invalid: {response_data.get('invalid', 0)}")
            else:
                print("❌ SMS failed!")
                print(f"   Error: {response_data.get('message', 'No error message')}")
                print(f"   Code: {response_data.get('code', 'No error code')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Error: {response_data.get('message', 'No error message')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_balance_check():
    print("\n💰 Testing Balance Check")
    print("=" * 30)
    
    # Get provider
    tenant = Tenant.objects.filter(subdomain='default').first()
    provider = SMSProvider.objects.filter(tenant=tenant, is_active=True).first()
    
    if not provider:
        print("❌ No provider found!")
        return
    
    # Balance URL from settings
    balance_url = provider.settings.get('balance_url', 'https://apisms.beem.africa/public/v1/vendors/balance')
    
    print(f"💰 Balance URL: {balance_url}")
    
    # Prepare headers
    import base64
    auth_string = f"{provider.api_key}:{provider.secret_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}'
    }
    
    try:
        response = requests.get(balance_url, headers=headers, timeout=30)
        print(f"📊 Balance Status: {response.status_code}")
        
        try:
            balance_data = response.json()
            print(f"📊 Balance Data: {json.dumps(balance_data, indent=2)}")
        except:
            print(f"📊 Balance Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Balance check failed: {e}")

def main():
    print("🧪 Beem API Direct Test")
    print("=" * 40)
    
    test_balance_check()
    test_beem_api_direct()
    
    print("\n💡 Common issues:")
    print("1. Invalid API credentials")
    print("2. Sender ID not registered")
    print("3. Insufficient balance")
    print("4. Invalid phone number format")
    print("5. Network connectivity issues")

if __name__ == "__main__":
    main()
