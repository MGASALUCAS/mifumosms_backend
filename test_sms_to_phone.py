#!/usr/bin/env python3
"""
Test sending SMS to the specific phone number 0614853618
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.beem_sms import BeemSMSService

def test_sms_to_phone():
    """Test sending SMS to 0614853618 using Taarifa-SMS."""
    print("=" * 80)
    print("TESTING SMS TO 0614853618 WITH TAARIFA-SMS")
    print("=" * 80)
    
    try:
        # Initialize BeemSMS service
        beem_service = BeemSMSService()
        print("BeemSMS service initialized successfully")
        
        # Test sending SMS to the specific phone number
        phone_number = "+255614853618"  # Tanzanian number format
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Using sender ID: Taarifa-SMS")
        
        result = beem_service.send_sms(
            message="Test message from SMS verification system to 0614853618",
            recipients=[phone_number],
            source_addr="Taarifa-SMS",
            recipient_ids=["test_0614853618"]
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS sent to 0614853618!")
        else:
            print("FAILED: SMS not sent to 0614853618")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"BeemSMS service error: {e}")
        import traceback
        traceback.print_exc()

def test_sms_verification_to_phone():
    """Test SMS verification service with the specific phone number."""
    print("\n" + "=" * 80)
    print("TESTING SMS VERIFICATION TO 0614853618")
    print("=" * 80)
    
    try:
        from accounts.services.sms_verification import SMSVerificationService
        from tenants.models import Tenant
        
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found!")
            return
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(tenant.id)
        print(f"SMS Verification Service initialized with sender ID: {sms_verification.sender_id}")
        
        # Test sending verification code to the specific phone number
        phone_number = "+255614853618"
        code = "123456"
        
        print(f"Sending verification SMS to: {phone_number}")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=code,
            message_type="verification"
        )
        
        print(f"SMS verification result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Verification SMS sent to 0614853618!")
        else:
            print("FAILED: Verification SMS not sent to 0614853618")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"SMS verification error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("Testing SMS to 0614853618")
    print("=" * 80)
    
    test_sms_to_phone()
    test_sms_verification_to_phone()

if __name__ == "__main__":
    main()
