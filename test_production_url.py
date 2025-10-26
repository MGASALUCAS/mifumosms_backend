#!/usr/bin/env python3
"""
Test with production URL from frontend.
"""
import requests
import json

def test_production_url():
    """Test with production URL from frontend."""
    print("Testing with production URL from frontend...")
    
    # The URL from the frontend error
    url = "https://mifumosms.servehttp.com/api/auth/sms/forgot-password/"
    
    # Test with a superadmin phone number
    test_data = {
        "phone_number": "255623118170"  # Superadmin phone from database
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
                    print("SUCCESS: Password reset sent!")
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

def test_with_different_phones():
    """Test with different phone numbers."""
    print("\n" + "="*60)
    print("TESTING WITH DIFFERENT PHONE NUMBERS")
    print("="*60)
    
    url = "https://mifumosms.servehttp.com/api/auth/sms/forgot-password/"
    headers = {'Content-Type': 'application/json'}
    
    # Test different phone numbers
    test_phones = [
        "255623118170",  # Superadmin
        "255689726060",  # Another superadmin
        "0757347857",    # Regular user
        "255700000001",  # Test user
    ]
    
    for phone in test_phones:
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
                else:
                    print(f"  - Error: {response_json.get('error')}")
            else:
                print(f"  - HTTP Error: {response.status_code}")
                print(f"  - Response: {response.text}")
                
        except Exception as e:
            print(f"  - Request Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("TEST WITH PRODUCTION URL")
    print("=" * 60)
    
    # Test 1: With superadmin phone
    test_production_url()
    
    # Test 2: With different phones
    test_with_different_phones()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

