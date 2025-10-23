#!/usr/bin/env python3
"""
Test the exact API call that was working yesterday
"""

import os
import sys
import django
import requests
import base64
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def test_exact_working_call():
    """Test the exact API call that was working yesterday."""
    print("=" * 80)
    print("TESTING EXACT WORKING API CALL")
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
    
    # Test with the exact format that was working yesterday
    # Based on the successful messages in the database
    test_cases = [
        {
            "name": "Quantum Sender ID (was working yesterday)",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message from exact working call",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "test_exact_1",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "Taarifa-SMS Sender ID (was working yesterday)",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message from exact working call",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "test_exact_2",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "With Reference ID parameter",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message with reference ID",
                "encoding": 0,
                "reference_id": "test_ref_123",
                "recipients": [{
                    "recipient_id": "test_exact_3",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "With Request ID parameter",
            "data": {
                "source_addr": "Quantum",
                "message": "Test message with request ID",
                "encoding": 0,
                "request_id": "test_req_123",
                "recipients": [{
                    "recipient_id": "test_exact_4",
                    "dest_addr": "255700000001"
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

def test_different_api_endpoints():
    """Test different API endpoints that might work."""
    print("\n" + "=" * 80)
    print("TESTING DIFFERENT API ENDPOINTS")
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
    
    # Test different endpoints
    endpoints = [
        "https://apisms.beem.africa/v1/send",
        "https://apisms.beem.africa/public/v1/send",
        "https://apisms.beem.africa/send",
        "https://apisms.beem.africa/v1/sms/send",
        "https://apisms.beem.africa/api/v1/send"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        
        data = {
            "source_addr": "Quantum",
            "message": "Test message",
            "encoding": 0,
            "recipients": [{
                "recipient_id": "test_endpoint",
                "dest_addr": "255700000001"
            }]
        }
        
        try:
            response = requests.post(
                endpoint,
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("SUCCESS!")
                break
            else:
                print("FAILED")
                
        except Exception as e:
            print(f"ERROR: {e}")

def main():
    """Run all tests."""
    print("Testing Exact Working API Call")
    print("=" * 80)
    
    test_exact_working_call()
    test_different_api_endpoints()

if __name__ == "__main__":
    main()
