#!/usr/bin/env python3
"""
Fixed test script for Beem API.
"""
import requests
import base64
import json
import os
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def test_beem_api_with_reference():
    """Test Beem API with proper reference ID."""
    print("Testing Beem API with reference ID...")
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: Beem API credentials not configured!")
        return False
    
    print(f"API Key: {api_key[:10]}...")
    print(f"Secret Key: {secret_key[:10]}...")
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # Generate reference ID
    reference_id = f"mifumo_test_{int(time.time())}"
    
    # Test data with reference ID
    data = {
        "source_addr": "Taarifa-SMS",
        "message": "Test message from Mifumo WMS - Password reset test",
        "encoding": 0,  # GSM7 encoding
        "recipients": [{
            "recipient_id": reference_id,
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
        print(f"Reference ID: {reference_id}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            'https://apisms.beem.africa/v1/send',
            json=data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
            
            if response_data.get('successful'):
                print("SUCCESS: Beem API is working!")
                return True
            else:
                print(f"ERROR: Beem API error: {response_data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"ERROR: HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: Request Error: {e}")
        return False

def test_sms_service_directly():
    """Test SMS service directly."""
    print("\n" + "="*60)
    print("TESTING SMS SERVICE DIRECTLY")
    print("="*60)
    
    try:
        from messaging.services.sms_service import SMSService
        from tenants.models import Tenant
        
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("ERROR: No tenant found")
            return False
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Create SMS service
        sms_service = SMSService(str(tenant.id))
        
        # Test sending SMS
        result = sms_service.send_sms(
            to="255700000001",
            message="Test message from Mifumo WMS - Password reset test",
            sender_id="Taarifa-SMS",
            recipient_id=f"test_{int(time.time())}"
        )
        
        print(f"SMS Service Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("SUCCESS: SMS service is working!")
            return True
        else:
            print(f"ERROR: SMS service failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"ERROR: SMS service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_forgot_password_endpoint():
    """Test the forgot password endpoint."""
    print("\n" + "="*60)
    print("TESTING FORGOT PASSWORD ENDPOINT")
    print("="*60)
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with a valid phone number from database
    test_data = {
        "phone_number": "0757347857"  # This should exist in database
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
                print("SUCCESS: Password reset code sent!")
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

if __name__ == "__main__":
    print("=" * 60)
    print("BEEM API AND SMS COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: Beem API with reference ID
    test_beem_api_with_reference()
    
    # Test 2: SMS service directly
    test_sms_service_directly()
    
    # Test 3: Forgot password endpoint
    test_forgot_password_endpoint()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

