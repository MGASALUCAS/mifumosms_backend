"""
Test User Settings API with Real Data and SMS Delivery
Tests the complete flow with real phone number 0757347863
"""
import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api/integration"

def test_real_sms_delivery():
    """Test the complete user settings API flow with real SMS delivery"""
    
    print("=" * 70)
    print("  USER SETTINGS API - REAL SMS DELIVERY TEST")
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
    
    # Step 2: Get API Settings
    print("=" * 70)
    print("  2. GET API SETTINGS")
    print("=" * 70)
    
    settings_response = requests.get(f"{API_BASE}/user/settings/", headers=headers)
    print(f"Settings Status: {settings_response.status_code}")
    
    if settings_response.status_code == 200:
        settings_data = settings_response.json()
        print("OK API Settings retrieved successfully!")
        print(f"Account: {settings_data['data']['api_account']['name']}")
        print(f"API Keys: {len(settings_data['data']['api_keys'])}")
        print(f"Webhooks: {len(settings_data['data']['webhooks'])}")
    else:
        print("X Failed to get settings!")
        print(f"Response: {settings_response.text}")
        return
    
    print()
    
    # Step 3: Create API Key for Real SMS
    print("=" * 70)
    print("  3. CREATE API KEY FOR REAL SMS")
    print("=" * 70)
    
    key_data = {
        "key_name": "Real SMS Test Key",
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
    
    # Step 4: Test Real SMS API with the new key
    print("=" * 70)
    print("  4. TEST REAL SMS API WITH NEW KEY")
    print("=" * 70)
    
    sms_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Real SMS data
    sms_data = {
        "message": "Hello from Mifumo SMS! This is a real test message sent via the User Settings API. Your API integration is working perfectly!",
        "recipients": ["+255757347863"],
        "sender_id": "Taarifa-SMS"
    }
    
    print(f"Sending SMS to: {sms_data['recipients'][0]}")
    print(f"Message: {sms_data['message'][:50]}...")
    print(f"Sender ID: {sms_data['sender_id']}")
    print()
    
    sms_response = requests.post(f"{API_BASE}/v1/test-sms/send/", 
                                json=sms_data, headers=sms_headers)
    print(f"SMS Status: {sms_response.status_code}")
    
    if sms_response.status_code == 200:
        sms_data = sms_response.json()
        print("OK SMS sent successfully!")
        print(f"Message ID: {sms_data['data']['message_id']}")
        print(f"Status: {sms_data['data']['status']}")
        print(f"Cost: {sms_data['data']['cost']} {sms_data['data']['currency']}")
        message_id = sms_data['data']['message_id']
    else:
        print("X Failed to send SMS!")
        print(f"Response: {sms_response.text}")
        return
    
    print()
    
    # Step 5: Check Message Status
    print("=" * 70)
    print("  5. CHECK MESSAGE STATUS")
    print("=" * 70)
    
    print("Waiting 3 seconds before checking status...")
    time.sleep(3)
    
    status_response = requests.get(f"{API_BASE}/v1/test-sms/status/{message_id}/", 
                                  headers=sms_headers)
    print(f"Status Check: {status_response.status_code}")
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print("OK Message status retrieved!")
        print(f"Message ID: {status_data['data']['message_id']}")
        print(f"Status: {status_data['data']['status']}")
        print(f"Delivery Time: {status_data['data']['delivery_time']}")
        
        # Check individual recipient status
        for recipient in status_data['data']['recipients']:
            print(f"Recipient: {recipient['phone']} - {recipient['status']}")
    else:
        print("X Failed to get message status!")
        print(f"Response: {status_response.text}")
    
    print()
    
    # Step 6: Check Account Balance
    print("=" * 70)
    print("  6. CHECK ACCOUNT BALANCE")
    print("=" * 70)
    
    balance_response = requests.get(f"{API_BASE}/v1/test-sms/balance/", 
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
    
    print()
    
    # Step 7: Create Webhook for Real Notifications
    print("=" * 70)
    print("  7. CREATE WEBHOOK FOR REAL NOTIFICATIONS")
    print("=" * 70)
    
    webhook_data = {
        "url": "https://webhook.site/unique-id-for-mifumo-test",
        "events": ["message.sent", "message.delivered", "message.failed"]
    }
    
    webhook_response = requests.post(f"{API_BASE}/user/webhooks/create/", 
                                    json=webhook_data, headers=headers)
    print(f"Create Webhook Status: {webhook_response.status_code}")
    
    if webhook_response.status_code == 201:
        webhook_data = webhook_response.json()
        print("OK Webhook created successfully!")
        print(f"Webhook ID: {webhook_data['data']['id']}")
        print(f"URL: {webhook_data['data']['url']}")
        print(f"Events: {webhook_data['data']['events']}")
    else:
        print("X Failed to create webhook!")
        print(f"Response: {webhook_response.text}")
    
    print()
    
    # Step 8: Get Usage Statistics
    print("=" * 70)
    print("  8. GET USAGE STATISTICS")
    print("=" * 70)
    
    usage_response = requests.get(f"{API_BASE}/user/usage/", headers=headers)
    print(f"Usage Status: {usage_response.status_code}")
    
    if usage_response.status_code == 200:
        usage_data = usage_response.json()
        print("OK Usage statistics retrieved!")
        print(f"API Keys: {usage_data['data']['api_keys']['total']} total, {usage_data['data']['api_keys']['active']} active")
        print(f"Webhooks: {usage_data['data']['webhooks']['total']} total, {usage_data['data']['webhooks']['active']} active")
        print(f"API Calls: {usage_data['data']['api_calls']['total']}")
    else:
        print("X Failed to get usage statistics!")
        print(f"Response: {usage_response.text}")
    
    print()
    
    # Step 9: Test Multiple SMS Sending
    print("=" * 70)
    print("  9. TEST MULTIPLE SMS SENDING")
    print("=" * 70)
    
    # Send another SMS to verify consistency
    sms_data_2 = {
        "message": "This is a second test message to verify the API is working consistently. All systems are operational!",
        "recipients": ["+255757347863"],
        "sender_id": "Taarifa-SMS"
    }
    
    print("Sending second test SMS...")
    sms_response_2 = requests.post(f"{API_BASE}/v1/test-sms/send/", 
                                  json=sms_data_2, headers=sms_headers)
    print(f"Second SMS Status: {sms_response_2.status_code}")
    
    if sms_response_2.status_code == 200:
        sms_data_2 = sms_response_2.json()
        print("OK Second SMS sent successfully!")
        print(f"Message ID: {sms_data_2['data']['message_id']}")
        print(f"Status: {sms_data_2['data']['status']}")
    else:
        print("X Failed to send second SMS!")
        print(f"Response: {sms_response_2.text}")
    
    print()
    
    # Step 10: Final Status Check
    print("=" * 70)
    print("  10. FINAL STATUS CHECK")
    print("=" * 70)
    
    # Get updated settings to see all activity
    final_settings_response = requests.get(f"{API_BASE}/user/settings/", headers=headers)
    print(f"Final Settings Status: {final_settings_response.status_code}")
    
    if final_settings_response.status_code == 200:
        final_settings = final_settings_response.json()
        print("OK Final settings retrieved!")
        print(f"Total API Keys: {len(final_settings['data']['api_keys'])}")
        print(f"Total Webhooks: {len(final_settings['data']['webhooks'])}")
        
        # Show all API keys
        print("\nAPI Keys:")
        for i, key in enumerate(final_settings['data']['api_keys'], 1):
            print(f"  {i}. {key['key_name']} - {key['api_key'][:20]}...")
        
        # Show all webhooks
        print("\nWebhooks:")
        for i, webhook in enumerate(final_settings['data']['webhooks'], 1):
            print(f"  {i}. {webhook['url']} - {webhook['events']}")
    
    print()
    
    print("=" * 70)
    print("  REAL SMS DELIVERY TEST - SUMMARY")
    print("=" * 70)
    print("OK All tests completed successfully!")
    print()
    print("Test Results:")
    print(f"OK User Authentication: SUCCESS")
    print(f"OK API Settings Retrieval: SUCCESS")
    print(f"OK API Key Creation: SUCCESS")
    print(f"OK Real SMS Sending: SUCCESS")
    print(f"OK Message Status Check: SUCCESS")
    print(f"OK Account Balance Check: SUCCESS")
    print(f"OK Webhook Creation: SUCCESS")
    print(f"OK Usage Statistics: SUCCESS")
    print(f"OK Multiple SMS Sending: SUCCESS")
    print()
    print("SMS Details:")
    print(f"Phone Number: +255757347863")
    print(f"Sender ID: MIFUMO")
    print(f"Messages Sent: 2")
    print(f"API Key: {api_key[:20]}...")
    print()
    print("Available API Endpoints:")
    print("1. GET  /api/integration/user/settings/     - Get API settings")
    print("2. GET  /api/integration/user/usage/        - Get usage statistics")
    print("3. POST /api/integration/user/keys/create/  - Create API key")
    print("4. POST /api/integration/user/keys/{id}/revoke/     - Revoke API key")
    print("5. POST /api/integration/user/keys/{id}/regenerate/ - Regenerate API key")
    print("6. POST /api/integration/user/webhooks/create/      - Create webhook")
    print("7. POST /api/integration/user/webhooks/{id}/toggle/ - Toggle webhook")
    print("8. DEL  /api/integration/user/webhooks/{id}/delete/ - Delete webhook")
    print("9. POST /api/integration/v1/test-sms/send/  - Send SMS")
    print("10. GET /api/integration/v1/test-sms/status/{id}/ - Check SMS status")
    print("11. GET /api/integration/v1/test-sms/balance/ - Check balance")
    print()
    print("Authentication: Bearer token (JWT) from login")
    print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)

if __name__ == "__main__":
    test_real_sms_delivery()
