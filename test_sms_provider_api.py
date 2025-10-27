#!/usr/bin/env python3
"""
Test SMS Provider API functionality.
This script demonstrates how to use the SMS Provider API.
"""

import os
import sys
import django
import requests
import json
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

# API Configuration
API_BASE_URL = 'http://127.0.0.1:8000/api/sms-provider'
TEST_PHONE = '255757347857'  # Your test phone number

def test_sms_provider_registration():
    """Test SMS provider registration."""
    print("=" * 80)
    print("TESTING SMS PROVIDER REGISTRATION")
    print("=" * 80)
    
    registration_data = {
        "company_name": "Test SMS Provider Ltd",
        "contact_email": "test@smsprovider.com",
        "contact_phone": "255712345678",
        "contact_name": "Test User",
        "description": "Test SMS provider for API integration"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/register/",
            json=registration_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Registration Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print("✅ Registration successful!")
                return data['data']
            else:
                print("❌ Registration failed!")
                return None
        else:
            print("❌ Registration failed!")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_send_sms(api_key, phone_number):
    """Test sending SMS."""
    print("\n" + "=" * 80)
    print("TESTING SMS SENDING")
    print("=" * 80)
    
    sms_data = {
        "to": phone_number,
        "message": f"Hello from SMS Provider API! This is a test message sent at {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "sender_id": "Taarifa-SMS"
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/send/",
            json=sms_data,
            headers=headers,
            timeout=30
        )
        
        print(f"SMS Send Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ SMS sent successfully!")
                return data['data']
            else:
                print("❌ SMS sending failed!")
                return None
        else:
            print("❌ SMS sending failed!")
            return None
            
    except Exception as e:
        print(f"❌ SMS sending error: {e}")
        return None

def test_message_status(api_key, message_id):
    """Test getting message status."""
    print("\n" + "=" * 80)
    print("TESTING MESSAGE STATUS")
    print("=" * 80)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/status/{message_id}/",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Check: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Status retrieved successfully!")
                return data['data']
            else:
                print("❌ Status retrieval failed!")
                return None
        else:
            print("❌ Status retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def test_delivery_reports(api_key):
    """Test getting delivery reports."""
    print("\n" + "=" * 80)
    print("TESTING DELIVERY REPORTS")
    print("=" * 80)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/reports/",
            headers=headers,
            timeout=30
        )
        
        print(f"Reports Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Reports retrieved successfully!")
                return data['data']
            else:
                print("❌ Reports retrieval failed!")
                return None
        else:
            print("❌ Reports retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ Reports error: {e}")
        return None

def test_api_info(api_key):
    """Test getting API info."""
    print("\n" + "=" * 80)
    print("TESTING API INFO")
    print("=" * 80)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/info/",
            headers=headers,
            timeout=30
        )
        
        print(f"API Info Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API info retrieved successfully!")
                return data['data']
            else:
                print("❌ API info retrieval failed!")
                return None
        else:
            print("❌ API info retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ API info error: {e}")
        return None

def main():
    """Run all SMS Provider API tests."""
    print("SMS Provider API Test Suite")
    print("=" * 80)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Phone: {TEST_PHONE}")
    print("=" * 80)
    
    # Test 1: Registration
    registration_result = test_sms_provider_registration()
    if not registration_result:
        print("\n❌ Registration failed. Cannot continue with other tests.")
        return
    
    api_key = registration_result['api_key']
    user_id = registration_result['user_id']
    account_id = registration_result['account_id']
    
    print(f"\n📋 Registration Details:")
    print(f"   User ID: {user_id}")
    print(f"   Account ID: {account_id}")
    print(f"   API Key: {api_key[:20]}...")
    
    # Test 2: Send SMS
    sms_result = test_send_sms(api_key, TEST_PHONE)
    if not sms_result:
        print("\n❌ SMS sending failed. Cannot continue with status tests.")
        return
    
    message_id = sms_result['message_id']
    print(f"\n📱 SMS Details:")
    print(f"   Message ID: {message_id}")
    print(f"   To: {sms_result['to']}")
    print(f"   Status: {sms_result['status']}")
    
    # Test 3: API Info
    test_api_info(api_key)
    
    # Test 4: Delivery Reports
    test_delivery_reports(api_key)
    
    # Test 5: Message Status (wait a bit first)
    print(f"\n⏳ Waiting 3 seconds before checking message status...")
    time.sleep(3)
    test_message_status(api_key, message_id)
    
    print("\n" + "=" * 80)
    print("🎉 SMS Provider API Test Complete!")
    print("=" * 80)
    print("📱 Check your phone for the SMS message!")
    print(f"📞 Phone number: {TEST_PHONE}")
    print("📤 Sender ID: Taarifa-SMS")

if __name__ == "__main__":
    main()






