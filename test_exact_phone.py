#!/usr/bin/env python3
"""
Test with exact phone numbers from database.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User

def test_with_exact_phone():
    """Test with exact phone numbers from database."""
    print("Testing with exact phone numbers from database...")
    
    # Get all superadmin users
    superadmins = User.objects.filter(is_superuser=True)
    
    if not superadmins.exists():
        print("ERROR: No superadmin users found!")
        return False
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    headers = {'Content-Type': 'application/json'}
    
    for superadmin in superadmins:
        print(f"\n--- Testing with superadmin: {superadmin.email} ---")
        print(f"Phone: {superadmin.phone_number}")
        
        test_data = {"phone_number": superadmin.phone_number}
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
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

def test_regular_user():
    """Test with regular user."""
    print("\n" + "="*60)
    print("TESTING WITH REGULAR USER")
    print("="*60)
    
    # Get a regular user
    regular_user = User.objects.filter(is_superuser=False).exclude(phone_number='').first()
    if not regular_user:
        print("ERROR: No regular user found!")
        return False
    
    print(f"Regular user: {regular_user.email}")
    print(f"Phone: {regular_user.phone_number}")
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    headers = {'Content-Type': 'application/json'}
    
    test_data = {"phone_number": regular_user.phone_number}
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get('success'):
                print("SUCCESS!")
                if response_json.get('bypassed'):
                    print("  - SMS was bypassed (unexpected for regular user)")
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
    print("TEST WITH EXACT PHONE NUMBERS")
    print("=" * 60)
    
    # Test 1: Superadmin users with exact phone numbers
    test_with_exact_phone()
    
    # Test 2: Regular user
    test_regular_user()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

