#!/usr/bin/env python3
"""
Debug Beem API to understand the Reference Id issue
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

def test_beem_api_debug():
    """Debug Beem API to understand the Reference Id issue."""
    print("=" * 80)
    print("DEBUGGING BEEM API REFERENCE ID ISSUE")
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
    
    # Test with different parameter names that might be the "Reference Id"
    test_cases = [
        {
            "name": "With reference_id parameter",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message with reference_id",
                "encoding": 0,
                "reference_id": "test_ref_123",
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255614853618"
                }]
            }
        },
        {
            "name": "With request_id parameter",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message with request_id",
                "encoding": 0,
                "request_id": "test_req_123",
                "recipients": [{
                    "recipient_id": "test_2",
                    "dest_addr": "255614853618"
                }]
            }
        },
        {
            "name": "With id parameter",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message with id",
                "encoding": 0,
                "id": "test_id_123",
                "recipients": [{
                    "recipient_id": "test_3",
                    "dest_addr": "255614853618"
                }]
            }
        },
        {
            "name": "With reference parameter",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message with reference",
                "encoding": 0,
                "reference": "test_ref_456",
                "recipients": [{
                    "recipient_id": "test_4",
                    "dest_addr": "255614853618"
                }]
            }
        },
        {
            "name": "With ref parameter",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message with ref",
                "encoding": 0,
                "ref": "test_ref_789",
                "recipients": [{
                    "recipient_id": "test_5",
                    "dest_addr": "255614853618"
                }]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        
        try:
            response = requests.post(
                "https://apisms.beem.africa/v1/send",
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

def test_different_api_formats():
    """Test different API formats that might work."""
    print("\n" + "=" * 80)
    print("TESTING DIFFERENT API FORMATS")
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
    
    # Test different API formats
    test_cases = [
        {
            "name": "Standard format with recipient_id",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255614853618"
                }]
            }
        },
        {
            "name": "Format with dest_addr first",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "dest_addr": "255614853618",
                    "recipient_id": "test_2"
                }]
            }
        },
        {
            "name": "Format with different recipient structure",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "phone": "255614853618",
                    "id": "test_3"
                }]
            }
        },
        {
            "name": "Format with different recipient structure 2",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "number": "255614853618",
                    "recipient_id": "test_4"
                }]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        
        try:
            response = requests.post(
                "https://apisms.beem.africa/v1/send",
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

def main():
    """Run all tests."""
    print("Debugging Beem API Reference Id Issue")
    print("=" * 80)
    
    test_beem_api_debug()
    test_different_api_formats()

if __name__ == "__main__":
    main()
