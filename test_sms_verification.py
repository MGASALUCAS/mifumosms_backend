#!/usr/bin/env python3
"""
Test SMS Verification Endpoints
Tests forgot password, reset password, and account confirmation via SMS
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

def get_admin_user_and_token():
    """Get admin user and generate JWT token."""
    try:
        user = User.objects.get(email='admin@mifumo.com')
        refresh = RefreshToken.for_user(user)
        return user, str(refresh.access_token)
    except User.DoesNotExist:
        print("Admin user not found. Please create admin@mifumo.com user first.")
        return None, None

def test_send_verification_code():
    """Test sending verification code via SMS."""
    print("=" * 80)
    print("TESTING SEND VERIFICATION CODE")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/auth/sms/send-code/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "message_type": "verification"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_verify_phone_code():
    """Test verifying phone code."""
    print("\n" + "=" * 80)
    print("TESTING VERIFY PHONE CODE")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/auth/sms/verify-code/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Use the actual verification code from the user
    payload = {
        "verification_code": user.phone_verification_code or "123456"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_forgot_password_sms():
    """Test forgot password via SMS."""
    print("\n" + "=" * 80)
    print("TESTING FORGOT PASSWORD SMS")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "phone_number": user.phone_number or "+255689726060"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_reset_password_sms():
    """Test reset password via SMS."""
    print("\n" + "=" * 80)
    print("TESTING RESET PASSWORD SMS")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/auth/sms/reset-password/"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "phone_number": user.phone_number or "+255689726060",
        "verification_code": user.phone_verification_code or "123456",
        "new_password": "newpassword123",
        "new_password_confirm": "newpassword123"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_confirm_account_sms():
    """Test account confirmation via SMS."""
    print("\n" + "=" * 80)
    print("TESTING CONFIRM ACCOUNT SMS")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/auth/sms/confirm-account/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "verification_code": user.phone_verification_code or "123456"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_user_registration_with_sms():
    """Test user registration with SMS verification."""
    print("\n" + "=" * 80)
    print("TESTING USER REGISTRATION WITH SMS")
    print("=" * 80)
    
    url = "http://127.0.0.1:8001/api/auth/register/"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+255700000001",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Run all SMS verification tests."""
    print("Testing SMS Verification Endpoints")
    print("=" * 80)
    
    # Test user registration with SMS
    registration_result = test_user_registration_with_sms()
    
    # Test sending verification code
    send_code_result = test_send_verification_code()
    
    # Test verifying phone code
    verify_code_result = test_verify_phone_code()
    
    # Test forgot password SMS
    forgot_password_result = test_forgot_password_sms()
    
    # Test reset password SMS
    reset_password_result = test_reset_password_sms()
    
    # Test account confirmation SMS
    confirm_account_result = test_confirm_account_sms()
    
    # Save results
    results = {
        "user_registration": registration_result,
        "send_verification_code": send_code_result,
        "verify_phone_code": verify_code_result,
        "forgot_password_sms": forgot_password_result,
        "reset_password_sms": reset_password_result,
        "confirm_account_sms": confirm_account_result
    }
    
    with open("sms_verification_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("All test results saved to: sms_verification_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
