#!/usr/bin/env python3
"""
Test SMS Verification Fix
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
from messaging.models import Tenant

def test_sms_verification_service():
    """Test SMS verification service with new sender ID."""
    print("=" * 80)
    print("TESTING SMS VERIFICATION SERVICE WITH QUANTUM SENDER ID")
    print("=" * 80)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenant found!")
        return
    
    print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
    
    # Test SMS verification service
    try:
        sms_verification = SMSVerificationService(tenant.id)
        print(f"SMS Verification Service initialized with sender ID: {sms_verification.sender_id}")
        
        # Test sending verification code
        result = sms_verification.send_verification_sms(
            phone_number="+255700000001",
            code="123456",
            message_type="verification"
        )
        
        print(f"SMS verification result: {result}")
        
    except Exception as e:
        print(f"SMS Verification Service error: {e}")
        import traceback
        traceback.print_exc()

def test_direct_sms_sending():
    """Test direct SMS sending with Quantum sender ID."""
    print("\n" + "=" * 80)
    print("TESTING DIRECT SMS SENDING WITH QUANTUM SENDER ID")
    print("=" * 80)
    
    import requests
    from requests.auth import HTTPBasicAuth
    from django.conf import settings
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Test direct SMS sending with Quantum sender ID
    send_url = "https://apisms.beem.africa/v1/send"
    
    payload = {
        "source_addr": "Quantum",
        "encoding": 0,
        "message": "Test message from SMS verification fix",
        "recipients": [
            {
                "dest_addr": "255700000001",
                "recipient_id": "test_verification"
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
            print("SUCCESS: SMS sent successfully with Quantum sender ID!")
        else:
            print("ERROR: Failed to send SMS with Quantum sender ID!")
            
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Run all tests."""
    print("Testing SMS Verification Fix")
    print("=" * 80)
    
    test_sms_verification_service()
    test_direct_sms_sending()

if __name__ == "__main__":
    main()
