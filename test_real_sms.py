#!/usr/bin/env python
"""
Test script to verify SMS functionality with real Beem credentials.
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

def test_sms_with_real_credentials():
    """Test SMS with your working Beem credentials."""
    print("🔍 Testing SMS with Real Beem Credentials...")
    
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Step 1: Login to get JWT token
        print("📝 Step 1: Logging in...")
        login_data = {
            "email": "admin@mifumo.com",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{base_url}/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()['tokens']['access']
            print("✅ Login successful!")
        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
        
        # Step 2: Test SMS endpoint with working sender ID
        print("📝 Step 2: Testing SMS with 'Taarifa-SMS' sender ID...")
        sms_data = {
            "message": "Test message from Mifumo WMS via API!",
            "recipients": ["255689726060"],  # Your working phone number
            "sender_id": "Taarifa-SMS"  # Your working sender ID
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        sms_response = requests.post(
            f"{base_url}/api/messaging/sms/sms/beem/send/",
            json=sms_data,
            headers=headers
        )
        
        print(f"📊 SMS Response Status: {sms_response.status_code}")
        print(f"📊 SMS Response: {sms_response.text}")
        
        if sms_response.status_code == 201:
            print("✅ SMS sent successfully via API!")
            response_data = sms_response.json()
            if response_data.get('success'):
                print(f"✅ Message ID: {response_data['data']['message_id']}")
                print(f"✅ Status: {response_data['data']['status']}")
                print(f"✅ Cost: ${response_data['data']['cost_estimate']}")
            return True
        else:
            print("❌ SMS sending failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SMS: {e}")
        return False

def test_direct_beem_api():
    """Test direct Beem API call (like your working Python code)."""
    print("\n🔍 Testing Direct Beem API Call...")
    
    try:
        import requests
        from requests.auth import HTTPBasicAuth

        url = "https://apisms.beem.africa/v1/send"

        data = {
            "source_addr": "Taarifa-SMS",
            "encoding": 0,
            "message": "Direct API Test from Python",
            "recipients": [
                {
                    "recipient_id": 1,
                    "dest_addr": "255689726060"
                }
            ]
        }

        username = "62f8c3a2cb510335"
        password = "YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ=="

        response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            print("✅ Direct Beem API call successful!")
            print(f"✅ Response: {response.text}")
            return True
        else:
            print(f"❌ Direct Beem API call failed. Status: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error with direct API call: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing SMS with Real Credentials...")
    print("=" * 60)
    
    # Test 1: Direct Beem API (should work)
    direct_ok = test_direct_beem_api()
    
    # Test 2: Via Django API
    api_ok = test_sms_with_real_credentials()
    
    print("\n" + "=" * 60)
    if direct_ok and api_ok:
        print("🎉 All tests passed! SMS is working perfectly!")
        print("📱 You can now use Postman with sender ID: Taarifa-SMS")
    elif direct_ok:
        print("✅ Direct Beem API works, but Django API needs fixing")
    else:
        print("❌ Both tests failed. Check your Beem credentials.")
    print("=" * 60)

if __name__ == '__main__':
    main()
