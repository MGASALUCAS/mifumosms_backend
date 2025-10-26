#!/usr/bin/env python3
"""
Test SMS for the specific user from the UI.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from accounts.services.sms_verification import SMSVerificationService

def test_ivan_user_sms():
    """Test SMS for ivan123@gmail.com user."""
    print("Testing SMS for ivan123@gmail.com user...")
    
    # Get the user
    user = User.objects.filter(phone_number='255614853618').first()
    if not user:
        print("ERROR: User not found!")
        return False
    
    print(f"User: {user.email}")
    print(f"Phone: {user.phone_number}")
    print(f"is_superuser: {user.is_superuser}")
    print(f"phone_verified: {user.phone_verified}")
    
    # Test SMS verification service directly
    print("\n" + "="*50)
    print("TESTING SMS VERIFICATION SERVICE")
    print("="*50)
    
    try:
        sms_service = SMSVerificationService(str(user.get_tenant().id))
        
        # Test send verification code
        result = sms_service.send_verification_code(user, "password_reset")
        print(f"SMS Service Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            if result.get('bypassed'):
                print("SUCCESS: SMS was bypassed (unexpected for regular user)")
            else:
                print("SUCCESS: SMS was sent successfully")
            return True
        else:
            print(f"ERROR: SMS failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"ERROR: SMS service error: {e}")
        return False

def test_api_endpoint():
    """Test the API endpoint."""
    print("\n" + "="*50)
    print("TESTING API ENDPOINT")
    print("="*50)
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with different phone formats
    phone_formats = [
        "255614853618",  # International format
        "+255614853618",  # With + prefix
        "0614853618",    # Local format
    ]
    
    headers = {'Content-Type': 'application/json'}
    
    for phone in phone_formats:
        print(f"\n--- Testing with phone: {phone} ---")
        
        test_data = {"phone_number": phone}
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('success'):
                    print("SUCCESS!")
                    if response_json.get('bypassed'):
                        print("  - SMS was bypassed")
                    else:
                        print("  - SMS was sent")
                    return True
                else:
                    print(f"  - Error: {response_json.get('error')}")
            else:
                print(f"  - HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"  - Request Error: {e}")
    
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST FOR IVAN USER (255614853618)")
    print("=" * 60)
    
    # Test 1: SMS service directly
    test_ivan_user_sms()
    
    # Test 2: API endpoint
    test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

