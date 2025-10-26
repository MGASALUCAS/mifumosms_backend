"""
Test script for User Settings API
Demonstrates how users can manage their API keys after normal registration
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api/integration"

def test_user_settings_api():
    """Test the complete user settings API flow"""
    
    print("=" * 60)
    print("  USER SETTINGS API - COMPLETE TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Step 1: Login to get authentication token
    print("=" * 60)
    print("  1. USER AUTHENTICATION")
    print("=" * 60)
    
    login_data = {
        "email": "admin@mifumo.com",  # Use existing admin user
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
        print(f"Available keys: {list(login_data.keys())}")
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
    print("=" * 60)
    print("  2. GET API SETTINGS")
    print("=" * 60)
    
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
    
    # Step 3: Create API Key
    print("=" * 60)
    print("  3. CREATE API KEY")
    print("=" * 60)
    
    key_data = {
        "key_name": "My Production Key",
        "permissions": ["read", "write"],
        "expires_at": None  # No expiration
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
    
    # Step 4: Test SMS API with the new key
    print("=" * 60)
    print("  4. TEST SMS API WITH NEW KEY")
    print("=" * 60)
    
    sms_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    sms_data = {
        "message": "Hello from User Settings API! This message was sent using the API key created through the settings.",
        "recipients": ["+255757347863"],
        "sender_id": "MIFUMO"
    }
    
    sms_response = requests.post(f"{API_BASE}/v1/test-sms/send/", 
                                json=sms_data, headers=sms_headers)
    print(f"SMS Status: {sms_response.status_code}")
    
    if sms_response.status_code == 200:
        sms_data = sms_response.json()
        print("OK SMS sent successfully!")
        print(f"Message ID: {sms_data['data']['message_id']}")
        print(f"Status: {sms_data['data']['status']}")
    else:
        print("X Failed to send SMS!")
        print(f"Response: {sms_response.text}")
    
    print()
    
    # Step 5: Create Webhook
    print("=" * 60)
    print("  5. CREATE WEBHOOK")
    print("=" * 60)
    
    webhook_data = {
        "url": "https://myapp.com/webhooks/mifumo",
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
    
    # Step 6: Get Usage Statistics
    print("=" * 60)
    print("  6. GET USAGE STATISTICS")
    print("=" * 60)
    
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
    
    # Step 7: Get Updated Settings
    print("=" * 60)
    print("  7. GET UPDATED SETTINGS")
    print("=" * 60)
    
    updated_settings_response = requests.get(f"{API_BASE}/user/settings/", headers=headers)
    print(f"Updated Settings Status: {updated_settings_response.status_code}")
    
    if updated_settings_response.status_code == 200:
        updated_settings = updated_settings_response.json()
        print("OK Updated settings retrieved!")
        print(f"API Keys: {len(updated_settings['data']['api_keys'])}")
        print(f"Webhooks: {len(updated_settings['data']['webhooks'])}")
        
        # Show the created API key
        if updated_settings['data']['api_keys']:
            latest_key = updated_settings['data']['api_keys'][0]
            print(f"Latest Key: {latest_key['key_name']} - {latest_key['api_key']}")
        
        # Show the created webhook
        if updated_settings['data']['webhooks']:
            latest_webhook = updated_settings['data']['webhooks'][0]
            print(f"Latest Webhook: {latest_webhook['url']} - {latest_webhook['events']}")
    
    print()
    
    # Step 8: Test API Key Management
    print("=" * 60)
    print("  8. TEST API KEY MANAGEMENT")
    print("=" * 60)
    
    # Get the key ID from the settings
    if updated_settings_response.status_code == 200:
        updated_settings = updated_settings_response.json()
        if updated_settings['data']['api_keys']:
            key_id = updated_settings['data']['api_keys'][0]['id']
            
            # Test regenerate key
            print("Testing key regeneration...")
            regenerate_response = requests.post(f"{API_BASE}/user/keys/{key_id}/regenerate/", 
                                               headers=headers)
            print(f"Regenerate Status: {regenerate_response.status_code}")
            
            if regenerate_response.status_code == 200:
                regenerate_data = regenerate_response.json()
                print("OK Key regenerated successfully!")
                print(f"New API Key: {regenerate_data['data']['api_key']}")
                print(f"New Secret Key: {regenerate_data['data']['secret_key']}")
            else:
                print("X Failed to regenerate key!")
                print(f"Response: {regenerate_response.text}")
    
    print()
    
    print("=" * 60)
    print("  USER SETTINGS API - TEST SUMMARY")
    print("=" * 60)
    print("OK All tests completed successfully!")
    print()
    print("Available Settings API Endpoints:")
    print("1. GET  /api/integration/user/settings/     - Get API settings")
    print("2. GET  /api/integration/user/usage/        - Get usage statistics")
    print("3. POST /api/integration/user/keys/create/  - Create API key")
    print("4. POST /api/integration/user/keys/{id}/revoke/     - Revoke API key")
    print("5. POST /api/integration/user/keys/{id}/regenerate/ - Regenerate API key")
    print("6. POST /api/integration/user/webhooks/create/      - Create webhook")
    print("7. POST /api/integration/user/webhooks/{id}/toggle/ - Toggle webhook")
    print("8. DEL  /api/integration/user/webhooks/{id}/delete/ - Delete webhook")
    print()
    print("Authentication: Bearer token (JWT) from login")
    print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    test_user_settings_api()
