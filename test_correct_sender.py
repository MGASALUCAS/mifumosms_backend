#!/usr/bin/env python3
"""
Test SMS with correct sender ID format
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

def test_sms_with_correct_sender():
    """Test sending SMS with correct sender ID format."""
    print("=" * 80)
    print("TESTING SMS WITH CORRECT SENDER ID")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Try with the correct sender ID format
    send_url = "https://apisms.beem.africa/v1/send"
    
    # Use the sender ID from the API response
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

def test_sms_with_quantum_sender():
    """Test sending SMS with Quantum sender ID."""
    print("\n" + "=" * 80)
    print("TESTING SMS WITH QUANTUM SENDER ID")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Try with Quantum sender ID
    send_url = "https://apisms.beem.africa/v1/send"
    
    payload = {
        "source_addr": "Quantum",
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
    print("Testing SMS with Correct Sender IDs")
    print("=" * 80)
    
    test_sms_with_correct_sender()
    test_sms_with_quantum_sender()

if __name__ == "__main__":
    main()
