#!/usr/bin/env python3
"""
Test SMS with Quantum sender ID to phone number 0757347857
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

import requests
import base64
import time
from django.conf import settings

def test_quantum_sender():
    """Test SMS with Quantum sender ID."""
    print("=" * 80)
    print("TESTING SMS WITH QUANTUM SENDER ID TO 0757347857")
    print("=" * 80)
    
    try:
        # Get API credentials
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not api_key or not secret_key:
            print("❌ API credentials not found!")
            return False
        
        print(f"API Key: {api_key[:10]}...")
        print(f"Secret Key: {secret_key[:10]}...")
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        # Test with Quantum sender ID (which is active)
        sender_id = "Quantum"
        phone_number = "255757347857"
        message = "Test message from Quantum to 0757347857 - Real SMS test"
        
        # Generate unique recipient ID
        recipient_id = f"quantum_test_{int(time.time())}"
        
        print(f"Sender ID: {sender_id}")
        print(f"Phone: {phone_number}")
        print(f"Message: {message}")
        print(f"Recipient ID: {recipient_id}")
        
        # Prepare request data
        data = {
            "source_addr": sender_id,
            "message": message,
            "encoding": 0,  # GSM7 encoding
            "recipients": [{
                "recipient_id": recipient_id,
                "dest_addr": phone_number
            }]
        }
        
        print(f"Request data: {data}")
        
        # Make API request
        response = requests.post(
            'https://apisms.beem.africa/v1/send',
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
                'User-Agent': 'MifumoWMS/1.0'
            },
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('successful'):
                print("✅ SUCCESS: SMS sent with Quantum sender ID!")
                print("📱 Check your phone number 0757347857 for the SMS message!")
                print(f"Request ID: {response_data.get('request_id', 'N/A')}")
                return True
            else:
                print("❌ API returned unsuccessful")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_taarifa_sender_fixed():
    """Test SMS with Taarifa-SMS sender ID with fixed reference ID."""
    print("\n" + "=" * 80)
    print("TESTING SMS WITH TAARIFA-SMS SENDER ID (FIXED)")
    print("=" * 80)
    
    try:
        # Get API credentials
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not api_key or not secret_key:
            print("❌ API credentials not found!")
            return False
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        # Test with Taarifa-SMS sender ID
        sender_id = "Taarifa-SMS"
        phone_number = "255757347857"
        message = "Test message from Taarifa-SMS to 0757347857 - Account confirmation test"
        
        # Generate unique recipient ID
        recipient_id = f"taarifa_test_{int(time.time())}"
        
        print(f"Sender ID: {sender_id}")
        print(f"Phone: {phone_number}")
        print(f"Message: {message}")
        print(f"Recipient ID: {recipient_id}")
        
        # Prepare request data
        data = {
            "source_addr": sender_id,
            "message": message,
            "encoding": 0,  # GSM7 encoding
            "recipients": [{
                "recipient_id": recipient_id,
                "dest_addr": phone_number
            }]
        }
        
        print(f"Request data: {data}")
        
        # Make API request
        response = requests.post(
            'https://apisms.beem.africa/v1/send',
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
                'User-Agent': 'MifumoWMS/1.0'
            },
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('successful'):
                print("✅ SUCCESS: SMS sent with Taarifa-SMS sender ID!")
                print("📱 Check your phone number 0757347857 for the SMS message!")
                print(f"Request ID: {response_data.get('request_id', 'N/A')}")
                return True
            else:
                print("❌ API returned unsuccessful")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_message():
    """Test with a very simple message."""
    print("\n" + "=" * 80)
    print("TESTING SIMPLE MESSAGE")
    print("=" * 80)
    
    try:
        # Get API credentials
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not api_key or not secret_key:
            print("❌ API credentials not found!")
            return False
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        # Test with very simple data
        data = {
            "source_addr": "Quantum",
            "message": "Hello from Mifumo!",
            "encoding": 0,
            "recipients": [{
                "recipient_id": "1",
                "dest_addr": "255757347857"
            }]
        }
        
        print(f"Simple request data: {data}")
        
        # Make API request
        response = requests.post(
            'https://apisms.beem.africa/v1/send',
            json=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': auth_header,
                'User-Agent': 'MifumoWMS/1.0'
            },
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('successful'):
                print("✅ SUCCESS: Simple SMS sent!")
                print("📱 Check your phone number 0757347857 for the SMS message!")
                return True
            else:
                print("❌ API returned unsuccessful")
                return False
        else:
            print(f"❌ API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing SMS delivery with Quantum sender ID to 0757347857")
    print("=" * 80)
    
    results = []
    
    # Test 1: Simple message
    print("\n1. Testing simple message...")
    results.append(("Simple Message", test_simple_message()))
    
    # Test 2: Quantum sender
    print("\n2. Testing Quantum sender...")
    results.append(("Quantum Sender", test_quantum_sender()))
    
    # Test 3: Taarifa-SMS sender (fixed)
    print("\n3. Testing Taarifa-SMS sender (fixed)...")
    results.append(("Taarifa-SMS Sender", test_taarifa_sender_fixed()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\nTotal tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests > 0:
        print("\n🎉 SMS DELIVERY IS WORKING!")
        print("📱 Check your phone number 0757347857 for the SMS messages!")
    else:
        print("\n⚠️  All tests failed. The issue might be:")
        print("- Phone number not reachable")
        print("- Carrier blocking SMS")
        print("- Network issues")
        print("- API account restrictions")

if __name__ == "__main__":
    main()




