#!/usr/bin/env python3
"""
Test different Beem API endpoints and formats
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

def test_different_endpoints():
    """Test different Beem API endpoints."""
    print("=" * 80)
    print("TESTING DIFFERENT BEEM API ENDPOINTS")
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
    endpoints_to_test = [
        "https://apisms.beem.africa/v1/send",
        "https://apisms.beem.africa/public/v1/send",
        "https://apisms.beem.africa/send",
        "https://apisms.beem.africa/v1/sms/send"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting endpoint: {endpoint}")
        
        # Test with simple data
        data = {
            "source_addr": "Taarifa-SMS",
            "message": "Test message",
            "encoding": 0,
            "recipients": [{
                "recipient_id": "test_1",
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
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("SUCCESS!")
                break
            else:
                print("FAILED")
                
        except Exception as e:
            print(f"ERROR: {e}")

def test_different_data_formats():
    """Test different data formats."""
    print("\n" + "=" * 80)
    print("TESTING DIFFERENT DATA FORMATS")
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
    
    # Test different data formats
    data_formats = [
        {
            "name": "Standard Format",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "Without Encoding",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "With Reference ID",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "reference_id": "test_ref_1",
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        },
        {
            "name": "With Request ID",
            "data": {
                "source_addr": "Taarifa-SMS",
                "message": "Test message",
                "encoding": 0,
                "request_id": "test_req_1",
                "recipients": [{
                    "recipient_id": "test_1",
                    "dest_addr": "255700000001"
                }]
            }
        }
    ]
    
    for format_test in data_formats:
        print(f"\nTesting: {format_test['name']}")
        print(f"Data: {format_test['data']}")
        
        try:
            response = requests.post(
                "https://apisms.beem.africa/v1/send",
                json=format_test['data'],
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
    print("Testing Different Beem API Endpoints and Formats")
    print("=" * 80)
    
    test_different_endpoints()
    test_different_data_formats()

if __name__ == "__main__":
    main()
