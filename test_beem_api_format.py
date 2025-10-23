#!/usr/bin/env python3
"""
Test different Beem API formats to find the working one
"""

import os
import sys
import django
import requests
import base64

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def test_different_api_formats():
    """Test different Beem API formats."""
    print("=" * 80)
    print("TESTING DIFFERENT BEEM API FORMATS")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Test different API endpoints and formats
    test_cases = [
        {
            "name": "Standard Format",
            "url": "https://apisms.beem.africa/v1/send",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "Alternative Format",
            "url": "https://apisms.beem.africa/v1/send",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "dest_addr": "255700000001",
                    "recipient_id": "test_1"
                }]
            }
        },
        {
            "name": "With Schedule Time",
            "url": "https://apisms.beem.africa/v1/send",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message",
                "encoding": 0,
                "schedule_time": "2025-10-23 12:00",
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "With Unicode Support",
            "url": "https://apisms.beem.africa/v1/send",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message",
                "encoding": 1,
                "allow_unicode": True,
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"URL: {test_case['url']}")
        print(f"Data: {test_case['data']}")
        
        try:
            response = requests.post(
                test_case['url'],
                json=test_case['data'],
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("SUCCESS!")
                break
            else:
                print("FAILED")
                
        except Exception as e:
            print(f"ERROR: {e}")

def test_sender_id_registration():
    """Test if sender ID needs to be registered first."""
    print("\n" + "=" * 80)
    print("TESTING SENDER ID REGISTRATION")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Check if we need to register the sender ID first
    try:
        response = requests.post(
            "https://apisms.beem.africa/public/v1/sender-names",
            json={
                "senderid": "Quantum",
                "sample_content": "Test verification messages for Mifumo WMS"
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
                'User-Agent': 'MifumoWMS/1.0'
            },
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Run all tests."""
    print("Testing Beem API Formats")
    print("=" * 80)
    
    test_different_api_formats()
    test_sender_id_registration()

if __name__ == "__main__":
    main()
