#!/usr/bin/env python3
"""
Test Beem API with different endpoints and formats
"""

import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def test_balance_endpoint():
    """Test balance endpoint to verify API access."""
    print("=" * 80)
    print("TESTING BALANCE ENDPOINT")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    balance_url = "https://apisms.beem.africa/public/v1/vendors/balance"
    
    try:
        response = requests.get(
            balance_url,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_send_with_different_format():
    """Test sending SMS with different request format."""
    print("\n" + "=" * 80)
    print("TESTING SEND WITH DIFFERENT FORMAT")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    # Try with different endpoint
    send_url = "https://apisms.beem.africa/v1/send"
    
    # Try with different payload format
    payload = {
        "source_addr": "Taarifa-SMS",
        "message": "Test message from API test",
        "recipients": [
            {
                "dest_addr": "255700000001",
                "recipient_id": "test_1"
            }
        ]
    }
    
    try:
        response = requests.post(
            send_url,
            json=payload,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MifumoWMS/1.0'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_with_encoding():
    """Test with explicit encoding."""
    print("\n" + "=" * 80)
    print("TESTING WITH ENCODING")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    send_url = "https://apisms.beem.africa/v1/send"
    
    payload = {
        "source_addr": "Taarifa-SMS",
        "encoding": 0,
        "message": "Test message from API test",
        "recipients": [
            {
                "dest_addr": "255700000001",
                "recipient_id": "test_1"
            }
        ]
    }
    
    try:
        response = requests.post(
            send_url,
            json=payload,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MifumoWMS/1.0'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_with_unicode():
    """Test with Unicode encoding."""
    print("\n" + "=" * 80)
    print("TESTING WITH UNICODE ENCODING")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    send_url = "https://apisms.beem.africa/v1/send"
    
    payload = {
        "source_addr": "Taarifa-SMS",
        "encoding": 1,
        "message": "Test message from API test",
        "recipients": [
            {
                "dest_addr": "255700000001",
                "recipient_id": "test_1"
            }
        ]
    }
    
    try:
        response = requests.post(
            send_url,
            json=payload,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MifumoWMS/1.0'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Run all tests."""
    print("Testing Beem API with Different Formats")
    print("=" * 80)
    
    test_balance_endpoint()
    test_send_with_different_format()
    test_with_encoding()
    test_with_unicode()

if __name__ == "__main__":
    main()
