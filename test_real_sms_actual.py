"""
Test Real SMS Delivery with Actual SMS Service
This will send real SMS messages to the phone number
"""
import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api/integration"

def test_real_sms_actual():
    """Test sending real SMS using the actual SMS service"""
    
    print("=" * 70)
    print("  REAL SMS DELIVERY TEST - ACTUAL SMS SERVICE")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Phone: +255757347863")
    print()
    
    # Step 1: Login to get authentication token
    print("=" * 70)
    print("  1. USER AUTHENTICATION")
    print("=" * 70)
    
    login_data = {
        "email": "admin@mifumo.com",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("X Login failed!")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    access_token = login_data.get('tokens', {}).get('access')
    
    if not access_token:
        print("X No access token received!")
        return
    
    print("OK Login successful!")
    print(f"Access Token: {access_token[:20]}...")
    print()
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get API Settings and create API key
    print("=" * 70)
    print("  2. CREATE API KEY FOR REAL SMS")
    print("=" * 70)
    
    key_data = {
        "key_name": "Real SMS Production Key",
        "permissions": ["read", "write"],
        "expires_at": None
    }
    
    key_response = requests.post(f"{API_BASE}/user/keys/create/", 
                                json=key_data, headers=headers)
    print(f"Create Key Status: {key_response.status_code}")
    
    if key_response.status_code == 201:
        key_data = key_response.json()
        api_key = key_data['data']['api_key']
        secret_key = key_data['data']['secret_key']
        print("OK API Key created successfully!")
        print(f"API Key: {api_key}")
        print(f"Secret Key: {secret_key}")
    else:
        print("X Failed to create API key!")
        print(f"Response: {key_response.text}")
        return
    
    print()
    
    # Step 3: Test Real SMS API using the actual SMS service
    print("=" * 70)
    print("  3. SEND REAL SMS USING ACTUAL SMS SERVICE")
    print("=" * 70)
    
    sms_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Real SMS data - using the actual SMS API endpoint
    sms_data = {
        "message": "REAL SMS TEST: This is a real SMS message sent via Mifumo SMS API to +255757347863. If you receive this, the real SMS service is working!",
        "recipients": ["+255757347863"],
        "sender_id": "MIFUMO"
    }
    
    print(f"Sending REAL SMS to: {sms_data['recipients'][0]}")
    print(f"Message: {sms_data['message'][:80]}...")
    print(f"Sender ID: {sms_data['sender_id']}")
    print()
    print("NOTE: This will send a REAL SMS message to your phone!")
    print("Proceeding with SMS sending...")
    
    # Use the actual SMS API endpoint (not the test endpoint)
    sms_response = requests.post(f"{API_BASE}/v1/sms/send/", 
                                json=sms_data, headers=sms_headers)
    print(f"SMS Status: {sms_response.status_code}")
    print(f"SMS Response: {sms_response.text}")
    
    if sms_response.status_code == 200:
        sms_data = sms_response.json()
        print("OK Real SMS sent successfully!")
        print(f"Message ID: {sms_data['data']['message_id']}")
        print(f"Status: {sms_data['data']['status']}")
        print(f"Cost: {sms_data['data']['cost']} {sms_data['data']['currency']}")
        message_id = sms_data['data']['message_id']
        
        print()
        print("=" * 70)
        print("  4. CHECK MESSAGE STATUS")
        print("=" * 70)
        
        print("Waiting 5 seconds before checking status...")
        time.sleep(5)
        
        status_response = requests.get(f"{API_BASE}/v1/sms/status/{message_id}/", 
                                      headers=sms_headers)
        print(f"Status Check: {status_response.status_code}")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print("OK Message status retrieved!")
            print(f"Message ID: {status_data['data']['message_id']}")
            print(f"Status: {status_data['data']['status']}")
            print(f"Delivery Time: {status_data['data'].get('delivery_time', 'N/A')}")
            
            # Check individual recipient status
            for recipient in status_data['data'].get('recipients', []):
                print(f"Recipient: {recipient['phone']} - {recipient['status']}")
        else:
            print("X Failed to get message status!")
            print(f"Response: {status_response.text}")
        
        print()
        print("=" * 70)
        print("  5. CHECK ACCOUNT BALANCE")
        print("=" * 70)
        
        balance_response = requests.get(f"{API_BASE}/v1/sms/balance/", 
                                       headers=sms_headers)
        print(f"Balance Check: {balance_response.status_code}")
        
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            print("OK Balance retrieved!")
            print(f"Balance: {balance_data['data']['balance']} {balance_data['data']['currency']}")
            print(f"Last Updated: {balance_data['data']['last_updated']}")
        else:
            print("X Failed to get balance!")
            print(f"Response: {balance_response.text}")
    
    else:
        print("X Failed to send real SMS!")
        print(f"Response: {sms_response.text}")
        print()
        print("This might be because:")
        print("1. Beem Africa API credentials are not configured")
        print("2. The SMS service is not properly set up")
        print("3. The phone number format is incorrect")
        print("4. There's an issue with the SMS provider")
    
    print()
    print("=" * 70)
    print("  REAL SMS TEST SUMMARY")
    print("=" * 70)
    print("Test completed!")
    print("If you received the SMS message on +255757347863, the real SMS service is working!")
    print("If not, check the Beem Africa API configuration and credentials.")
    print()
    print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    test_real_sms_actual()
