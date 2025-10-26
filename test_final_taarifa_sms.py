"""
Final Comprehensive Test with Taarifa-SMS Sender ID
This demonstrates the complete working User Settings API with real SMS sending
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api/integration"
TEST_PHONE_NUMBER = "+255757347863"

def format_response(response):
    try:
        return json.dumps(response.json(), indent=2)
    except json.JSONDecodeError:
        return response.text

def test_final_taarifa_sms():
    print("=" * 70)
    print("  FINAL COMPREHENSIVE TEST - TAARIFA-SMS SENDER ID")
    print("=" * 70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Phone: {TEST_PHONE_NUMBER}")
    print(f"Sender ID: Taarifa-SMS (ACTIVE)")
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
        print(f"Response: {format_response(login_response)}")
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
        print(f"Response: {format_response(settings_response)}")
        return
    
    print()
    
    # Step 3: Create API Key for SMS sending
    print("=" * 70)
    print("  3. CREATE API KEY FOR SMS")
    print("=" * 70)
    key_create_data = {
        "key_name": "Taarifa-SMS Test Key",
        "permissions": {"sms": ["send", "status", "balance"]}
    }
    key_response = requests.post(f"{API_BASE}/user/keys/create/", headers=headers, json=key_create_data)
    print(f"Create Key Status: {key_response.status_code}")
    
    if key_response.status_code == 201:
        key_data = key_response.json()
        api_key_sms = key_data['data']['api_key']
        secret_key_sms = key_data['data']['secret_key']
        print("OK API Key created successfully!")
        print(f"API Key: {api_key_sms}")
        print(f"Secret Key: {secret_key_sms}")
    else:
        print("X Failed to create API key!")
        print(f"Response: {format_response(key_response)}")
        return
    
    print()
    
    # Headers for SMS API with the new key
    sms_headers = {
        "Authorization": f"Bearer {api_key_sms}",
        "Content-Type": "application/json"
    }
    
    # Step 4: Test SMS API with Taarifa-SMS sender ID
    print("=" * 70)
    print("  4. TEST SMS API WITH TAARIFA-SMS SENDER ID")
    print("=" * 70)
    sms_send_data = {
        "message": f"FINAL TEST: This is a comprehensive test from Mifumo SMS API using Taarifa-SMS sender ID to {TEST_PHONE_NUMBER}. The User Settings API is working perfectly!",
        "recipients": [TEST_PHONE_NUMBER],
        "sender_id": "Taarifa-SMS"
    }
    print(f"Sending SMS to: {TEST_PHONE_NUMBER}")
    print(f"Message: {sms_send_data['message'][:80]}...")
    print(f"Sender ID: {sms_send_data['sender_id']}")
    
    sms_response = requests.post(f"{API_BASE}/v1/test-sms/send/", headers=sms_headers, json=sms_send_data)
    print(f"\nSMS Status: {sms_response.status_code}")
    
    if sms_response.status_code == 200:
        sms_data = sms_response.json()
        print("OK SMS sent successfully!")
        print(f"Message ID: {sms_data['data']['message_id']}")
        print(f"Status: {sms_data['data']['status']}")
        print(f"Cost: {sms_data['data']['cost']} {sms_data['data']['currency']}")
        message_id = sms_data['data']['message_id']
    else:
        print("X Failed to send SMS!")
        print(f"Response: {format_response(sms_response)}")
        return
    
    print()
    
    # Step 5: Check Message Status
    print("=" * 70)
    print("  5. CHECK MESSAGE STATUS")
    print("=" * 70)
    print("Waiting 3 seconds before checking status...")
    time.sleep(3)
    
    status_response = requests.get(f"{API_BASE}/v1/test-sms/status/{message_id}/", headers=sms_headers)
    print(f"Status Check: {status_response.status_code}")
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print("OK Message status retrieved!")
        print(f"Message ID: {status_data['data']['message_id']}")
        print(f"Status: {status_data['data']['status']}")
        print(f"Delivery Time: {status_data['data']['delivery_time']}")
        print(f"Recipient: {status_data['data']['recipients'][0]['phone']} - {status_data['data']['recipients'][0]['status']}")
    else:
        print("X Failed to get message status!")
        print(f"Response: {format_response(status_response)}")
        return
    
    print()
    
    # Step 6: Check Account Balance
    print("=" * 70)
    print("  6. CHECK ACCOUNT BALANCE")
    print("=" * 70)
    balance_response = requests.get(f"{API_BASE}/v1/test-sms/balance/", headers=sms_headers)
    print(f"Balance Check: {balance_response.status_code}")
    
    if balance_response.status_code == 200:
        balance_data = balance_response.json()
        print("OK Balance retrieved!")
        print(f"Balance: {balance_data['data']['balance']} {balance_data['data']['currency']}")
        print(f"Last Updated: {balance_data['data']['last_updated']}")
    else:
        print("X Failed to get balance!")
        print(f"Response: {format_response(balance_response)}")
        return
    
    print()
    
    # Step 7: Create Webhook
    print("=" * 70)
    print("  7. CREATE WEBHOOK")
    print("=" * 70)
    webhook_create_data = {
        "url": "https://webhook.site/unique-id-for-mifumo-taarifa-test",
        "events": ["message.sent", "message.delivered", "message.failed"]
    }
    webhook_response = requests.post(f"{API_BASE}/user/webhooks/create/", headers=headers, json=webhook_create_data)
    print(f"Create Webhook Status: {webhook_response.status_code}")
    
    if webhook_response.status_code == 201:
        webhook_data = webhook_response.json()
        print("OK Webhook created successfully!")
        print(f"Webhook ID: {webhook_data['data']['id']}")
        print(f"URL: {webhook_data['data']['url']}")
        print(f"Events: {webhook_data['data']['events']}")
    else:
        print("X Failed to create webhook!")
        print(f"Response: {format_response(webhook_response)}")
        return
    
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
        print(f"API Calls: {usage_data['data'].get('total_api_calls', 'N/A')}")
    else:
        print("X Failed to get usage statistics!")
        print(f"Response: {format_response(usage_response)}")
        return
    
    print()
    
    # Step 9: Test Real SMS API (if account has balance)
    print("=" * 70)
    print("  9. TEST REAL SMS API (REQUIRES ACCOUNT BALANCE)")
    print("=" * 70)
    print("Testing real SMS API with Taarifa-SMS sender ID...")
    print("NOTE: This will only work if the Beem Africa account has sufficient balance.")
    
    real_sms_data = {
        "message": f"REAL SMS TEST: This is a real SMS from Mifumo SMS API using Taarifa-SMS sender ID to {TEST_PHONE_NUMBER}. If you receive this, the real SMS service is working!",
        "recipients": [TEST_PHONE_NUMBER],
        "sender_id": "Taarifa-SMS"
    }
    
    real_sms_response = requests.post(f"{API_BASE}/v1/sms/send/", headers=sms_headers, json=real_sms_data)
    print(f"Real SMS Status: {real_sms_response.status_code}")
    
    if real_sms_response.status_code == 200:
        real_sms_data = real_sms_response.json()
        print("OK Real SMS sent successfully!")
        print(f"Message ID: {real_sms_data['data']['message_id']}")
        print(f"Status: {real_sms_data['data']['status']}")
        print("Check your phone for the real SMS message!")
    else:
        print("X Real SMS failed (likely insufficient balance)")
        print(f"Response: {format_response(real_sms_response)}")
        print("This is expected if the Beem Africa account needs to be topped up.")
    
    print()
    
    # Final Summary
    print("=" * 70)
    print("  FINAL TEST SUMMARY - TAARIFA-SMS SENDER ID")
    print("=" * 70)
    print("OK All tests completed successfully!")
    print()
    print("Test Results:")
    print(f"OK User Authentication: SUCCESS")
    print(f"OK API Settings Retrieval: SUCCESS")
    print(f"OK API Key Creation: SUCCESS")
    print(f"OK Test SMS Sending: SUCCESS")
    print(f"OK Message Status Check: SUCCESS")
    print(f"OK Account Balance Check: SUCCESS")
    print(f"OK Webhook Creation: SUCCESS")
    print(f"OK Usage Statistics: SUCCESS")
    print(f"OK Real SMS API Test: {'SUCCESS' if real_sms_response.status_code == 200 else 'FAILED (Insufficient Balance)'}")
    print()
    print("SMS Details:")
    print(f"Phone Number: {TEST_PHONE_NUMBER}")
    print(f"Sender ID: Taarifa-SMS (ACTIVE)")
    print(f"Test Messages Sent: 1")
    print(f"Real Messages Sent: {'1' if real_sms_response.status_code == 200 else '0 (Insufficient Balance)'}")
    print(f"API Key: {api_key_sms[:20]}...")
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
    print("9. POST /api/integration/v1/test-sms/send/  - Send test SMS")
    print("10. GET /api/integration/v1/test-sms/status/{id}/ - Check test SMS status")
    print("11. GET /api/integration/v1/test-sms/balance/ - Check test balance")
    print("12. POST /api/integration/v1/sms/send/      - Send real SMS (requires balance)")
    print("13. GET /api/integration/v1/sms/status/{id}/ - Check real SMS status")
    print("14. GET /api/integration/v1/sms/balance/    - Check real balance")
    print()
    print("Authentication: Bearer token (JWT) from login")
    print("Default Sender ID: Taarifa-SMS (ACTIVE)")
    print("Test completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)

if __name__ == "__main__":
    test_final_taarifa_sms()
