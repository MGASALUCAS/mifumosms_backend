#!/usr/bin/env python3
"""
Simple test for verification code functionality.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User

def test_verification_code():
    """Test verification code functionality."""
    print("Testing verification code functionality...")
    
    # Get the user
    user = User.objects.filter(phone_number='255614853618').first()
    if not user:
        print("ERROR: User not found!")
        return False
    
    print(f"User: {user.email}")
    print(f"Phone: {user.phone_number}")
    print(f"Current verification code: {user.phone_verification_code}")
    
    # Test 1: Send verification code
    print("\n1. Sending verification code...")
    url = "http://127.0.0.1:8001/api/auth/sms/send-code/"
    headers = {'Content-Type': 'application/json'}
    
    test_data = {
        "phone_number": "255614853618",
        "message_type": "password_reset"
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('success'):
                print("SUCCESS: Code sent!")
                
                # Refresh user to get new code
                user.refresh_from_db()
                print(f"New verification code: {user.phone_verification_code}")
                
                # Test 2: Verify with correct code
                print("\n2. Verifying with correct code...")
                verify_url = "http://127.0.0.1:8001/api/auth/sms/verify-code/"
                
                verify_data = {
                    "phone_number": "255614853618",
                    "verification_code": user.phone_verification_code
                }
                
                verify_response = requests.post(verify_url, json=verify_data, headers=headers, timeout=30)
                print(f"Verify Status: {verify_response.status_code}")
                print(f"Verify Response: {verify_response.text}")
                
                if verify_response.status_code == 200:
                    verify_json = verify_response.json()
                    if verify_json.get('success'):
                        print("SUCCESS: Correct code verified!")
                    else:
                        print(f"ERROR: Verification failed: {verify_json.get('error')}")
                else:
                    print(f"ERROR: Verify HTTP Error: {verify_response.status_code}")
                
                # Test 3: Verify with wrong code
                print("\n3. Verifying with wrong code...")
                wrong_verify_data = {
                    "phone_number": "255614853618",
                    "verification_code": "999999"
                }
                
                wrong_response = requests.post(verify_url, json=wrong_verify_data, headers=headers, timeout=30)
                print(f"Wrong Code Status: {wrong_response.status_code}")
                print(f"Wrong Code Response: {wrong_response.text}")
                
                if wrong_response.status_code == 400:
                    wrong_json = wrong_response.json()
                    if not wrong_json.get('success'):
                        print("SUCCESS: Wrong code correctly rejected!")
                    else:
                        print("ERROR: Wrong code was accepted!")
                else:
                    print(f"ERROR: Wrong code HTTP Error: {wrong_response.status_code}")
                
                return True
            else:
                print(f"ERROR: Send code failed: {response_json.get('error')}")
        else:
            print(f"ERROR: HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Request Error: {e}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST VERIFICATION CODE")
    print("=" * 60)
    
    test_verification_code()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

