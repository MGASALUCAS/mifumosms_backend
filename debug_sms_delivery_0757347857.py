#!/usr/bin/env python3
"""
Debug SMS delivery issues for phone number 0757347857
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.services.sms_verification import SMSVerificationService
from tenants.models import Tenant
from messaging.services.sms_service import SMSService
from messaging.services.beem_sms import BeemSMSService
import requests
import base64
from django.conf import settings

def check_beem_api_directly():
    """Check Beem API directly with detailed logging."""
    print("=" * 80)
    print("CHECKING BEEM API DIRECTLY")
    print("=" * 80)
    
    try:
        # Get API credentials
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        print(f"API Key: {api_key[:10]}..." if api_key else "API Key: None")
        print(f"Secret Key: {secret_key[:10]}..." if secret_key else "Secret Key: None")
        
        if not api_key or not secret_key:
            print("❌ API credentials not found!")
            return False
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        # Prepare request data
        data = {
            "source_addr": "Taarifa-SMS",
            "message": "Test message from Mifumo WMS to 0757347857 - Direct API test",
            "encoding": 0,  # GSM7 encoding
            "recipients": [{
                "recipient_id": "test_direct_0757347857",
                "dest_addr": "255757347857"
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
                print("✅ SUCCESS: SMS sent via direct API call!")
                return True
            else:
                print("❌ FAILED: API returned unsuccessful")
                return False
        else:
            print(f"❌ FAILED: API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct API call error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_phone_formats():
    """Test different phone number formats."""
    print("\n" + "=" * 80)
    print("TESTING DIFFERENT PHONE NUMBER FORMATS")
    print("=" * 80)
    
    formats_to_test = [
        "255757347857",      # International without +
        "+255757347857",     # International with +
        "0757347857",        # Local format
        "757347857",         # Local without 0
    ]
    
    for phone_format in formats_to_test:
        print(f"\nTesting format: {phone_format}")
        
        try:
            # Use working tenant
            tenant_id = "18da454d-57d5-4c0f-b09c-e74b3cd1a71a"
            sms_verification = SMSVerificationService(tenant_id)
            
            # Format phone number for API
            if phone_format.startswith('+'):
                api_phone = phone_format[1:]
            elif phone_format.startswith('0') and len(phone_format) == 10:
                api_phone = '255' + phone_format[1:]
            elif len(phone_format) == 9 and phone_format.startswith('7'):
                api_phone = '255' + phone_format
            else:
                api_phone = phone_format
            
            print(f"API phone format: {api_phone}")
            
            result = sms_verification.send_verification_sms(
                phone_number=f"+{api_phone}",
                code="TEST123",
                message_type="verification"
            )
            
            print(f"Result: {result}")
            
            if result.get('success'):
                print("✅ SUCCESS with this format!")
            else:
                print("❌ FAILED with this format")
                
        except Exception as e:
            print(f"❌ Error with format {phone_format}: {e}")

def test_different_sender_ids():
    """Test different sender IDs."""
    print("\n" + "=" * 80)
    print("TESTING DIFFERENT SENDER IDs")
    print("=" * 80)
    
    sender_ids_to_test = [
        "Taarifa-SMS",
        "MIFUMO",
        "INFO",
        "TEST",
        "SMS"
    ]
    
    for sender_id in sender_ids_to_test:
        print(f"\nTesting sender ID: {sender_id}")
        
        try:
            # Get API credentials
            api_key = getattr(settings, 'BEEM_API_KEY', None)
            secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
            
            if not api_key or not secret_key:
                print("❌ API credentials not found!")
                continue
            
            # Create Basic Auth header
            credentials = f"{api_key}:{secret_key}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            auth_header = f"Basic {encoded_credentials}"
            
            # Prepare request data
            data = {
                "source_addr": sender_id,
                "message": f"Test message from {sender_id} to 0757347857",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": f"test_{sender_id.lower()}",
                    "dest_addr": "255757347857"
                }]
            }
            
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
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('successful'):
                    print(f"✅ SUCCESS with sender ID: {sender_id}")
                else:
                    print(f"❌ FAILED with sender ID: {sender_id}")
            else:
                print(f"❌ API error with sender ID: {sender_id}")
                
        except Exception as e:
            print(f"❌ Error with sender ID {sender_id}: {e}")

def check_sms_balance():
    """Check SMS account balance."""
    print("\n" + "=" * 80)
    print("CHECKING SMS ACCOUNT BALANCE")
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
        
        # Check balance
        response = requests.get(
            'https://apisms.beem.africa/public/v1/vendors/balance',
            headers={
                'Authorization': auth_header,
                'User-Agent': 'MifumoWMS/1.0'
            },
            timeout=30
        )
        
        print(f"Balance check status: {response.status_code}")
        print(f"Balance response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            balance = response_data.get('data', {}).get('credit_balance', 0)
            print(f"✅ Account balance: {balance} credits")
            if balance <= 0:
                print("⚠️  WARNING: No credits available! This might be why SMS is not being delivered.")
            return True
        else:
            print(f"❌ Balance check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Balance check error: {e}")
        return False

def main():
    """Run all debugging tests."""
    print("Debugging SMS delivery issues for 0757347857")
    print("=" * 80)
    
    # Test 1: Check account balance
    print("\n1. Checking SMS account balance...")
    check_sms_balance()
    
    # Test 2: Direct API call
    print("\n2. Testing direct Beem API call...")
    check_beem_api_directly()
    
    # Test 3: Different phone formats
    print("\n3. Testing different phone number formats...")
    test_different_phone_formats()
    
    # Test 4: Different sender IDs
    print("\n4. Testing different sender IDs...")
    test_different_sender_ids()
    
    print("\n" + "=" * 80)
    print("DEBUGGING COMPLETE")
    print("=" * 80)
    print("Check the results above to identify the issue.")
    print("Common issues:")
    print("- No SMS credits/balance")
    print("- Invalid sender ID")
    print("- Wrong phone number format")
    print("- Network/carrier issues")
    print("- API rate limiting")

if __name__ == "__main__":
    main()




