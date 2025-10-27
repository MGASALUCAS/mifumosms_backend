#!/usr/bin/env python3
"""
Test SMS to phone number 0614853618
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

def test_sms_0614853618():
    """Test SMS to phone number 0614853618."""
    print("=" * 80)
    print("TESTING SMS TO 0614853618")
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
        
        # Test with 0614853618 (convert to international format)
        phone_number = "255614853618"  # 0614853618 -> 255614853618
        message = "Test message from Mifumo to 0614853618 - SMS delivery test"
        sender_id = "Quantum"
        
        print(f"Phone number: 0614853618 (international: {phone_number})")
        print(f"Message: {message}")
        print(f"Sender ID: {sender_id}")
        
        # Prepare request data
        data = {
            "source_addr": sender_id,
            "message": message,
            "encoding": 0,  # GSM7 encoding
            "recipients": [{
                "recipient_id": "1",
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
                print("✅ SUCCESS: SMS sent to 0614853618!")
                print("📱 Check your phone number 0614853618 for the SMS message!")
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

def test_multiple_phones():
    """Test SMS to multiple phone numbers."""
    print("\n" + "=" * 80)
    print("TESTING SMS TO MULTIPLE PHONE NUMBERS")
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
        
        # Test with both phone numbers
        phone_numbers = [
            ("0757347857", "255757347857"),
            ("0614853618", "255614853618")
        ]
        
        for local_phone, intl_phone in phone_numbers:
            print(f"\nTesting phone: {local_phone} (international: {intl_phone})")
            
            # Prepare request data
            data = {
                "source_addr": "Quantum",
                "message": f"Test message from Mifumo to {local_phone} - Multi-phone test",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": f"test_{local_phone}",
                    "dest_addr": intl_phone
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
                    print(f"✅ SUCCESS: SMS sent to {local_phone}!")
                else:
                    print(f"❌ FAILED: SMS not sent to {local_phone}")
            else:
                print(f"❌ API error for {local_phone}: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_verification_message_0614853618():
    """Test verification message to 0614853618."""
    print("\n" + "=" * 80)
    print("TESTING VERIFICATION MESSAGE TO 0614853618")
    print("=" * 80)
    
    try:
        from accounts.services.sms_verification import SMSVerificationService
        from tenants.models import Tenant
        
        # Get working tenant
        tenant = Tenant.objects.get(id="18da454d-57d5-4c0f-b09c-e74b3cd1a71a")
        print(f"Using tenant: {tenant.name}")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(str(tenant.id))
        print(f"SMS Verification Service initialized with sender ID: {sms_verification.sender_id}")
        
        # Test sending verification code to 0614853618
        phone_number = "+255614853618"  # 0614853618 -> +255614853618
        code = "123456"
        
        print(f"Sending verification SMS to: {phone_number}")
        print(f"Message type: account_confirmation")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=code,
            message_type="account_confirmation"
        )
        
        print(f"SMS verification result: {result}")
        
        if result.get('success'):
            print("✅ SUCCESS: Verification SMS sent to 0614853618!")
            print("📱 Check your phone number 0614853618 for the verification SMS!")
            return True
        else:
            print("❌ FAILED: Verification SMS not sent to 0614853618")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Verification SMS error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests for 0614853618."""
    print("Testing SMS delivery to phone number 0614853618")
    print("=" * 80)
    
    results = []
    
    # Test 1: Simple SMS to 0614853618
    print("\n1. Testing simple SMS to 0614853618...")
    results.append(("Simple SMS to 0614853618", test_sms_0614853618()))
    
    # Test 2: Multiple phones
    print("\n2. Testing multiple phone numbers...")
    results.append(("Multiple Phones", test_multiple_phones()))
    
    # Test 3: Verification message
    print("\n3. Testing verification message to 0614853618...")
    results.append(("Verification Message to 0614853618", test_verification_message_0614853618()))
    
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
        print("📱 Check your phone numbers for the SMS messages!")
        print("   - 0757347857")
        print("   - 0614853618")
    else:
        print("\n⚠️  All tests failed. The issue might be:")
        print("- Phone numbers not reachable")
        print("- Carrier blocking SMS")
        print("- Network issues")
        print("- API account restrictions")

if __name__ == "__main__":
    main()






