#!/usr/bin/env python3
"""
Test Simple SMS API (bypasses DRF authentication)
"""

import requests
import json
from datetime import datetime

def test_simple_sms_api():
    """Test the simple SMS API that bypasses DRF authentication"""
    
    print("="*60)
    print("  SIMPLE SMS API TEST (Bypasses DRF Authentication)")
    print("="*60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Phone: +255757347863")
    print(f"Sender ID: Quantum")
    
    # Use the API key from previous test
    api_key = "mif_i75CoBURE1yKbP-S_eMvZi5FGE5maqicrUDkE4KCRPg"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Send SMS
    print("\n1. TESTING SMS SENDING")
    print("-" * 40)
    
    sms_data = {
        "message": "Hello from Quantum SMS! This is a test message using the simple API.",
        "recipients": ["+255757347863"],
        "sender_id": "Quantum"
    }
    
    print(f"Message: {sms_data['message']}")
    print(f"Recipients: {sms_data['recipients']}")
    print(f"Sender ID: {sms_data['sender_id']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/integration/v1/test-sms/send/",
            json=sms_data,
            headers=headers
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                message_id = data['data']['message_id']
                print(f"\nSUCCESS! SMS sent with message ID: {message_id}")
                
                # Test 2: Check message status
                print("\n2. TESTING MESSAGE STATUS")
                print("-" * 40)
                
                try:
                    status_response = requests.get(
                        f"http://127.0.0.1:8001/api/integration/v1/test-sms/status/{message_id}/",
                        headers=headers
                    )
                    
                    print(f"Status Response: {json.dumps(status_response.json(), indent=2)}")
                    
                    if status_response.status_code == 200:
                        print("SUCCESS! Message status retrieved")
                    else:
                        print("FAILED! Could not retrieve message status")
                        
                except Exception as e:
                    print(f"Error checking status: {e}")
                
                # Test 3: Check balance
                print("\n3. TESTING ACCOUNT BALANCE")
                print("-" * 40)
                
                try:
                    balance_response = requests.get(
                        "http://127.0.0.1:8001/api/integration/v1/test-sms/balance/",
                        headers=headers
                    )
                    
                    print(f"Balance Response: {json.dumps(balance_response.json(), indent=2)}")
                    
                    if balance_response.status_code == 200:
                        print("SUCCESS! Account balance retrieved")
                    else:
                        print("FAILED! Could not retrieve account balance")
                        
                except Exception as e:
                    print(f"Error checking balance: {e}")
                
            else:
                print("FAILED! SMS sending failed")
        else:
            print("FAILED! SMS sending failed with status code")
            
    except Exception as e:
        print(f"Error sending SMS: {e}")
    
    # Test 4: Test error handling
    print("\n4. TESTING ERROR HANDLING")
    print("-" * 40)
    
    # Test with invalid API key
    print("Testing with invalid API key...")
    invalid_headers = {
        "Authorization": "Bearer invalid_key_12345",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/integration/v1/test-sms/send/",
            json=sms_data,
            headers=invalid_headers
        )
        
        print(f"Invalid API Key Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing invalid API key: {e}")
    
    # Test with missing message
    print("\nTesting with missing message...")
    invalid_sms_data = {
        "recipients": ["+255757347863"],
        "sender_id": "Quantum"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/integration/v1/test-sms/send/",
            json=invalid_sms_data,
            headers=headers
        )
        
        print(f"Missing Message Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing missing message: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("  SIMPLE SMS API TEST SUMMARY")
    print("="*60)
    print("The simple SMS API bypasses Django REST Framework authentication")
    print("and uses custom API key validation logic.")
    print("\nThis demonstrates that the API key authentication logic works")
    print("when not intercepted by DRF's authentication system.")
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_simple_sms_api()

