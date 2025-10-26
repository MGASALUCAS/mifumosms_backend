#!/usr/bin/env python3
"""
Test verification code functionality after fix.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User

def test_verification_code_flow():
    """Test the complete verification code flow."""
    print("Testing verification code flow...")
    
    # Get the user from the UI
    user = User.objects.filter(phone_number='255614853618').first()
    if not user:
        print("ERROR: User not found!")
        return False
    
    print(f"User: {user.email}")
    print(f"Phone: {user.phone_number}")
    print(f"Current verification code: {user.phone_verification_code}")
    print(f"Code sent at: {user.phone_verification_sent_at}")
    
    # Step 1: Send verification code
    print("\n" + "="*50)
    print("STEP 1: SENDING VERIFICATION CODE")
    print("="*50)
    
    url = "http://127.0.0.1:8001/api/auth/sms/send-code/"
    headers = {'Content-Type': 'application/json'}
    
    # Test with different phone formats
    phone_formats = [
        "255614853618",    # International format
        "+255614853618",   # With + prefix
        "0614853618",      # Local format
    ]
    
    for phone in phone_formats:
        print(f"\n--- Testing send code with phone: {phone} ---")
        
        test_data = {
            "phone_number": phone,
            "message_type": "password_reset"
        }
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('success'):
                    print("✅ Code sent successfully!")
                    
                    # Refresh user to get the new code
                    user.refresh_from_db()
                    print(f"New verification code: {user.phone_verification_code}")
                    print(f"Code sent at: {user.phone_verification_sent_at}")
                    
                    # Step 2: Verify the code
                    print(f"\n--- Testing verify code with phone: {phone} ---")
                    test_verify_code(phone, user.phone_verification_code)
                    return True
                else:
                    print(f"❌ Send code failed: {response_json.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    return False

def test_verify_code(phone, correct_code):
    """Test verifying the code."""
    print(f"\n--- Verifying code: {correct_code} ---")
    
    url = "http://127.0.0.1:8001/api/auth/sms/verify-code/"
    headers = {'Content-Type': 'application/json'}
    
    # Test with correct code
    test_data = {
        "phone_number": phone,
        "verification_code": correct_code
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('success'):
                print("✅ Code verified successfully!")
                return True
            else:
                print(f"❌ Verification failed: {response_json.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    # Test with wrong code
    print(f"\n--- Testing with wrong code: 999999 ---")
    test_data_wrong = {
        "phone_number": phone,
        "verification_code": "999999"
    }
    
    try:
        response = requests.post(url, json=test_data_wrong, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            response_json = response.json()
            if not response_json.get('success'):
                print("✅ Wrong code correctly rejected!")
                return True
            else:
                print("❌ Wrong code was accepted (this is a bug!)")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    return False

def test_forgot_password_flow():
    """Test the complete forgot password flow."""
    print("\n" + "="*60)
    print("TESTING COMPLETE FORGOT PASSWORD FLOW")
    print("="*60)
    
    # Step 1: Send forgot password SMS
    print("\n1. Sending forgot password SMS...")
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    headers = {'Content-Type': 'application/json'}
    
    test_data = {
        "phone_number": "255614853618"
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('success'):
                print("✅ Forgot password SMS sent!")
                
                # Get the user and verification code
                user = User.objects.filter(phone_number='255614853618').first()
                if user and user.phone_verification_code:
                    print(f"Verification code: {user.phone_verification_code}")
                    
                    # Step 2: Verify the code
                    print("\n2. Verifying code...")
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
                            print("✅ Code verified successfully!")
                            print("✅ Complete forgot password flow working!")
                            return True
                        else:
                            print(f"❌ Verification failed: {verify_json.get('error')}")
                    else:
                        print(f"❌ Verify HTTP Error: {verify_response.status_code}")
                else:
                    print("❌ No verification code found")
            else:
                print(f"❌ Forgot password failed: {response_json.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST VERIFICATION CODE FIX")
    print("=" * 60)
    
    # Test 1: Verification code flow
    test_verification_code_flow()
    
    # Test 2: Complete forgot password flow
    test_forgot_password_flow()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

