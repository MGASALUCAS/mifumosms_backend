#!/usr/bin/env python3
"""
Test API endpoints with HTTP requests.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from api_integration.models import APIAccount, APIKey

def test_api_endpoints():
    """Test the API endpoints with HTTP requests."""
    print("=" * 60)
    print("TESTING API ENDPOINTS WITH HTTP REQUESTS")
    print("=" * 60)
    
    # Get a test user and API key
    user = User.objects.filter(email='ivan123@gmail.com').first()
    if not user:
        print("ERROR: Test user not found!")
        return False
    
    api_account = APIAccount.objects.filter(owner=user).first()
    if not api_account:
        print("ERROR: API account not found!")
        return False
    
    api_key = APIKey.objects.filter(api_account=api_account).first()
    if not api_key:
        print("ERROR: API key not found!")
        return False
    
    print(f"Using API Key: {api_key.api_key[:20]}...")
    
    # Test 1: Dashboard access
    print("\n1. Testing Dashboard Access...")
    try:
        response = requests.get("http://127.0.0.1:8001/api/integration/dashboard/", timeout=10)
        print(f"Dashboard Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Dashboard accessible")
        else:
            print(f"FAIL: Dashboard returned {response.status_code}")
    except Exception as e:
        print(f"ERROR: Dashboard test failed: {e}")
    
    # Test 2: API Documentation
    print("\n2. Testing API Documentation...")
    try:
        response = requests.get("http://127.0.0.1:8001/api/integration/documentation/", timeout=10)
        print(f"Documentation Status: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS: Documentation accessible")
        else:
            print(f"FAIL: Documentation returned {response.status_code}")
    except Exception as e:
        print(f"ERROR: Documentation test failed: {e}")
    
    # Test 3: SMS API - Send SMS
    print("\n3. Testing SMS API - Send SMS...")
    headers = {
        'Authorization': f'Bearer {api_key.api_key}',
        'Content-Type': 'application/json'
    }
    
    sms_data = {
        "message": "Hello from Mifumo SMS API! This is a test message.",
        "recipients": ["+255614853618"],
        "sender_id": "MIFUMO"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/integration/v1/sms/send/", 
            json=sms_data, 
            headers=headers, 
            timeout=30
        )
        print(f"SMS Send Status: {response.status_code}")
        print(f"SMS Send Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: SMS sent successfully")
                message_id = result['data']['message_id']
                
                # Test 4: Get Message Status
                print(f"\n4. Testing Message Status for ID: {message_id}")
                try:
                    status_response = requests.get(
                        f"http://127.0.0.1:8001/api/integration/v1/sms/status/{message_id}/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Status Response: {status_response.status_code}")
                    print(f"Status Data: {status_response.text}")
                    
                    if status_response.status_code == 200:
                        print("SUCCESS: Message status retrieved")
                    else:
                        print(f"FAIL: Status returned {status_response.status_code}")
                except Exception as e:
                    print(f"ERROR: Status test failed: {e}")
                
                # Test 5: Delivery Reports
                print(f"\n5. Testing Delivery Reports...")
                try:
                    reports_response = requests.get(
                        "http://127.0.0.1:8001/api/integration/v1/sms/delivery-reports/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Reports Response: {reports_response.status_code}")
                    print(f"Reports Data: {reports_response.text}")
                    
                    if reports_response.status_code == 200:
                        print("SUCCESS: Delivery reports retrieved")
                    else:
                        print(f"FAIL: Reports returned {reports_response.status_code}")
                except Exception as e:
                    print(f"ERROR: Reports test failed: {e}")
                
                # Test 6: Balance
                print(f"\n6. Testing Balance...")
                try:
                    balance_response = requests.get(
                        "http://127.0.0.1:8001/api/integration/v1/sms/balance/",
                        headers=headers,
                        timeout=10
                    )
                    print(f"Balance Response: {balance_response.status_code}")
                    print(f"Balance Data: {balance_response.text}")
                    
                    if balance_response.status_code == 200:
                        print("SUCCESS: Balance retrieved")
                    else:
                        print(f"FAIL: Balance returned {balance_response.status_code}")
                except Exception as e:
                    print(f"ERROR: Balance test failed: {e}")
                
            else:
                print(f"FAIL: SMS send failed: {result.get('message')}")
        else:
            print(f"FAIL: SMS send returned {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: SMS send test failed: {e}")
    
    # Test 7: Create API Key via AJAX
    print(f"\n7. Testing Create API Key via AJAX...")
    try:
        create_key_data = {
            "key_name": "Test Key via API",
            "permissions": ["read", "write"],
            "expires_at": None
        }
        
        response = requests.post(
            "http://127.0.0.1:8001/api/integration/keys/create/",
            json=create_key_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"Create Key Status: {response.status_code}")
        print(f"Create Key Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("SUCCESS: API key created via AJAX")
            else:
                print(f"FAIL: Create key failed: {result.get('error')}")
        else:
            print(f"FAIL: Create key returned {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Create key test failed: {e}")
    
    return True

if __name__ == "__main__":
    print("Starting API Endpoint Tests...")
    
    success = test_api_endpoints()
    
    print("\n" + "=" * 60)
    if success:
        print("API ENDPOINT TESTS COMPLETED")
        print("Check the results above for individual test status.")
    else:
        print("API ENDPOINT TESTS FAILED")
        print("Check the errors above for details.")

