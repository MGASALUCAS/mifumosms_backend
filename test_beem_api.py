#!/usr/bin/env python3
"""
Test Beem API directly to check credentials.
"""
import requests
import base64
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def test_beem_api_directly():
    """Test Beem API directly with credentials."""
    print("Testing Beem API directly...")
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("❌ Beem API credentials not configured!")
        return False
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Secret Key: {secret_key[:10]}...")
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Test data
    data = {
        "source_addr": "Taarifa-SMS",
        "message": "Test message from Mifumo WMS - Password reset test",
        "encoding": 0,  # GSM7 encoding
        "recipients": [{
            "recipient_id": "test_001",
            "dest_addr": "255700000001"
        }]
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header,
        'User-Agent': 'MifumoWMS/1.0'
    }
    
    try:
        print("Making request to Beem API...")
        response = requests.post(
            'https://apisms.beem.africa/v1/send',
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
            
            if response_data.get('successful'):
                print("✅ Beem API is working!")
                return True
            else:
                print(f"❌ Beem API error: {response_data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

def test_beem_balance():
    """Test Beem account balance."""
    print("\nTesting Beem account balance...")
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("❌ Beem API credentials not configured!")
        return False
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    headers = {
        'Authorization': auth_header,
        'User-Agent': 'MifumoWMS/1.0'
    }
    
    try:
        response = requests.get(
            'https://apisms.beem.africa/v1/balance',
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Balance Response: {json.dumps(response_data, indent=2)}")
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("BEEM API DIRECT TEST")
    print("=" * 60)
    
    # Test 1: Send SMS
    test_beem_api_directly()
    
    # Test 2: Check balance
    test_beem_balance()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)