#!/usr/bin/env python3
"""
Test SMS verification service directly with the phone number from the test
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
from accounts.models import User
from tenants.models import Tenant

def test_sms_verification_direct():
    """Test SMS verification service directly."""
    print("=" * 80)
    print("TESTING SMS VERIFICATION SERVICE DIRECTLY")
    print("=" * 80)
    
    try:
        # Get the user from the test (admin@mifumo.com)
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Tenant: {user.get_tenant().name if user.get_tenant() else 'None'}")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        print(f"SMS Verification Service initialized with tenant ID: {sms_verification.tenant_id}")
        
        # Test sending verification code
        phone_number = user.phone_number or "+255614853618"
        code = "123456"
        
        print(f"Sending verification SMS to: {phone_number}")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=code,
            message_type="verification"
        )
        
        print(f"SMS verification result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Verification SMS sent!")
        else:
            print("FAILED: Verification SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Details: {result.get('details', {})}")
        
    except Exception as e:
        print(f"Error testing SMS verification: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing SMS Verification Service Directly")
    print("=" * 80)
    
    test_sms_verification_direct()

if __name__ == "__main__":
    main()
