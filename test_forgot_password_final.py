#!/usr/bin/env python3
"""
Final test for forgot password functionality.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from accounts.views import normalize_phone_number

def test_forgot_password_with_normalized_phone():
    """Test forgot password with normalized phone number."""
    print("Testing forgot password with normalized phone number...")
    
    # Get a superadmin user
    superadmin = User.objects.filter(is_superuser=True).first()
    if not superadmin:
        print("ERROR: No superadmin user found!")
        return False
    
    print(f"Superadmin: {superadmin.email}")
    print(f"Original phone: {superadmin.phone_number}")
    
    # Normalize the phone number
    normalized_phone = normalize_phone_number(superadmin.phone_number)
    print(f"Normalized phone: {normalized_phone}")
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with normalized phone number
    test_data = {
        "phone_number": normalized_phone
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

def test_with_different_phone_formats():
    """Test with different phone number formats."""
    print("\n" + "="*60)
    print("TESTING WITH DIFFERENT PHONE FORMATS")
    print("="*60)
    
    # Get a superadmin user
    superadmin = User.objects.filter(is_superuser=True).first()
    if not superadmin:
        print("ERROR: No superadmin user found!")
        return False
    
    print(f"Superadmin: {superadmin.email}")
    print(f"Original phone: {superadmin.phone_number}")
    
    # Test different formats
    phone_formats = [
        superadmin.phone_number,  # Original format
        normalize_phone_number(superadmin.phone_number),  # Normalized format
        f"+{superadmin.phone_number}",  # With + prefix
        f"0{superadmin.phone_number[3:]}" if superadmin.phone_number.startswith('255') else superadmin.phone_number,  # Local format
    ]
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    headers = {'Content-Type': 'application/json'}
    
    for phone in phone_formats:
        print(f"\n--- Testing with phone: {phone} ---")
        
        test_data = {"phone_number": phone}
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('success'):
                    print("SUCCESS!")
                    if response_json.get('bypassed'):
                        print("  - SMS was bypassed for superadmin")
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
    print("FINAL FORGOT PASSWORD TEST")
    print("=" * 60)
    
    # Test 1: With normalized phone
    test_forgot_password_with_normalized_phone()
    
    # Test 2: With different formats
    test_with_different_phone_formats()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

