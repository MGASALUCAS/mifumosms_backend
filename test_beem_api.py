#!/usr/bin/env python3
"""
Test Beem API credentials
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

def test_beem_api():
    """Test Beem API credentials directly."""
    print("=" * 80)
    print("TESTING BEEM API CREDENTIALS")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    print(f"API Key: {api_key}")
    print(f"Secret Key: {secret_key[:20]}..." if secret_key else "None")
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Test balance endpoint (simpler than sending SMS)
    balance_url = "https://apisms.beem.africa/public/v1/vendors/balance"
    
    try:
        response = requests.get(
            balance_url,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: API credentials are valid!")
        else:
            print("ERROR: API credentials are invalid!")
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_send_sms():
    """Test sending SMS with Beem API."""
    print("\n" + "=" * 80)
    print("TESTING SEND SMS")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Test send SMS endpoint
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
        
        if response.status_code == 200:
            print("SUCCESS: SMS sent successfully!")
        else:
            print("ERROR: Failed to send SMS!")
            
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Run all tests."""
    print("Testing Beem API Credentials")
    print("=" * 80)
    
    test_beem_api()
    test_send_sms()

if __name__ == "__main__":
    main()
