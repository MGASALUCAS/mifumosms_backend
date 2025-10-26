#!/usr/bin/env python3
"""
Test forgot password with superadmin user to verify bypass works.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User

def test_forgot_password_with_superadmin():
    """Test forgot password with superadmin user."""
    print("Testing forgot password with superadmin user...")
    
    # Get a superadmin user
    superadmin = User.objects.filter(is_superuser=True).first()
    if not superadmin:
        print("ERROR: No superadmin user found!")
        return False
    
    print(f"Testing with superadmin: {superadmin.email}")
    print(f"Phone: {superadmin.phone_number}")
    print(f"is_superuser: {superadmin.is_superuser}")
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with superadmin's phone number
    test_data = {
        "phone_number": superadmin.phone_number
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Making POST request to: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            
            if response_json.get('success'):
                if response_json.get('bypassed'):
                    print("SUCCESS: Password reset bypassed for superadmin user!")
                    return True
                else:
                    print("WARNING: Password reset not bypassed for superadmin user!")
                    return False
            else:
                print(f"ERROR: API Error: {response_json.get('error')}")
                return False
        else:
            print(f"ERROR: HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Request Error: {e}")
        return False

def test_forgot_password_with_regular_user():
    """Test forgot password with regular user (should fail due to invalid credentials)."""
    print("\n" + "="*60)
    print("TESTING FORGOT PASSWORD WITH REGULAR USER")
    print("="*60)
    
    # Get a regular user
    regular_user = User.objects.filter(is_superuser=False).exclude(phone_number='').first()
    if not regular_user:
        print("ERROR: No regular user found!")
        return False
    
    print(f"Testing with regular user: {regular_user.email}")
    print(f"Phone: {regular_user.phone_number}")
    print(f"is_superuser: {regular_user.is_superuser}")
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with regular user's phone number
    test_data = {
        "phone_number": regular_user.phone_number
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Making POST request to: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            
            if response_json.get('success'):
                print("SUCCESS: Password reset sent for regular user!")
                return True
            else:
                print(f"ERROR: API Error: {response_json.get('error')}")
                return False
        else:
            print(f"ERROR: HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Request Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FORGOT PASSWORD TEST WITH SUPERADMIN BYPASS")
    print("=" * 60)
    
    # Test 1: Superadmin user (should bypass)
    test_forgot_password_with_superadmin()
    
    # Test 2: Regular user (should fail due to invalid credentials)
    test_forgot_password_with_regular_user()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

