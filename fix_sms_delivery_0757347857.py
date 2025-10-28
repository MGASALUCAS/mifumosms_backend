#!/usr/bin/env python3
"""
Fix SMS delivery issues for phone number 0757347857
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.sms_service import SMSService
from messaging.services.beem_sms import BeemSMSService
from tenants.models import Tenant
import requests
import base64
from django.conf import settings

def test_sms_service_direct():
    """Test SMS service directly with proper error handling."""
    print("=" * 80)
    print("TESTING SMS SERVICE DIRECT WITH ERROR HANDLING")
    print("=" * 80)
    
    try:
        # Get working tenant
        tenant = Tenant.objects.get(id="18da454d-57d5-4c0f-b09c-e74b3cd1a71a")
        print(f"Using tenant: {tenant.name}")
        
        # Test SMS service
        sms_service = SMSService(str(tenant.id))
        print("SMS Service initialized")
        
        # Test sending SMS
        phone_number = "255757347857"  # International format without +
        message = "Test message from SMS Service to 0757347857 - Direct test"
        sender_id = "Taarifa-SMS"
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Message: {message}")
        print(f"Sender ID: {sender_id}")
        
        result = sms_service.send_sms(
            to=phone_number,
            message=message,
            sender_id=sender_id,
            recipient_id="test_direct_0757347857"
        )
        
        print(f"SMS service result: {result}")
        
        if result.get('success'):
            print("✅ SUCCESS: SMS sent via SMS service!")
            return True
        else:
            print("❌ FAILED: SMS not sent via SMS service")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ SMS service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_beem_service_direct():
    """Test Beem service directly."""
    print("\n" + "=" * 80)
    print("TESTING BEEM SERVICE DIRECT")
    print("=" * 80)
    
    try:
        # Test Beem service
        beem_service = BeemSMSService()
        print("Beem service initialized")
        
        # Test sending SMS
        phone_number = "+255757347857"
        message = "Test message from Beem Service to 0757347857 - Direct test"
        sender_id = "Taarifa-SMS"
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Message: {message}")
        print(f"Sender ID: {sender_id}")
        
        result = beem_service.send_sms(
            message=message,
            recipients=[phone_number],
            source_addr=sender_id,
            recipient_ids=["test_beem_0757347857"]
        )
        
        print(f"Beem service result: {result}")
        
        if result.get('success'):
            print("✅ SUCCESS: SMS sent via Beem service!")
            return True
        else:
            print("❌ FAILED: SMS not sent via Beem service")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Beem service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_working_sender_id():
    """Test with a known working sender ID."""
    print("\n" + "=" * 80)
    print("TESTING WITH KNOWN WORKING SENDER ID")
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
        
        # Test with different sender IDs that might work
        sender_ids_to_test = [
            "INFO",      # Common working sender ID
            "SMS",       # Simple sender ID
            "TEST",      # Test sender ID
            "MIFUMO",    # Company name
        ]
        
        for sender_id in sender_ids_to_test:
            print(f"\nTesting sender ID: {sender_id}")
            
            # Prepare request data
            data = {
                "source_addr": sender_id,
                "message": f"Test message from {sender_id} to 0757347857",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": f"test_{sender_id.lower()}_{int(__import__('time').time())}",
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
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('successful'):
                    print(f"✅ SUCCESS with sender ID: {sender_id}")
                    print("📱 Check your phone! You should receive the SMS now!")
                    return True
                else:
                    print(f"❌ API returned unsuccessful for sender ID: {sender_id}")
            else:
                print(f"❌ API error with sender ID: {sender_id}")
                
        return False
        
    except Exception as e:
        print(f"❌ Error testing sender IDs: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_sender_id_status():
    """Check the status of sender IDs."""
    print("\n" + "=" * 80)
    print("CHECKING SENDER ID STATUS")
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
        
        # Check sender IDs
        response = requests.get(
            'https://apisms.beem.africa/public/v1/sender-names',
            headers={
                'Authorization': auth_header,
                'User-Agent': 'MifumoWMS/1.0'
            },
            timeout=30
        )
        
        print(f"Sender IDs check status: {response.status_code}")
        print(f"Sender IDs response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            sender_ids = response_data.get('data', [])
            print(f"Available sender IDs: {len(sender_ids)}")
            for sid in sender_ids[:5]:  # Show first 5
                print(f"  - {sid.get('senderid', 'N/A')} (Status: {sid.get('status', 'N/A')})")
            return True
        else:
            print(f"❌ Sender IDs check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Sender IDs check error: {e}")
        return False

def main():
    """Run all tests to fix SMS delivery."""
    print("Fixing SMS delivery issues for 0757347857")
    print("=" * 80)
    
    # Test 1: Check sender ID status
    print("\n1. Checking sender ID status...")
    check_sender_id_status()
    
    # Test 2: Test with working sender IDs
    print("\n2. Testing with known working sender IDs...")
    success = test_with_working_sender_id()
    
    if success:
        print("\n🎉 SMS DELIVERY FIXED!")
        print("📱 Check your phone number 0757347857 for the SMS message!")
    else:
        # Test 3: SMS service direct
        print("\n3. Testing SMS service direct...")
        test_sms_service_direct()
        
        # Test 4: Beem service direct
        print("\n4. Testing Beem service direct...")
        test_beem_service_direct()
        
        print("\n⚠️  SMS delivery still not working. The issue might be:")
        print("- Sender ID not approved/registered")
        print("- Phone number format issues")
        print("- Carrier/network issues")
        print("- API rate limiting")

if __name__ == "__main__":
    main()







