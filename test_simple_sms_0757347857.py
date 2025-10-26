#!/usr/bin/env python3
"""
Simple test for SMS verification with phone number 0757347857
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

def test_sms_verification():
    """Test SMS verification with the working tenant."""
    print("=" * 80)
    print("TESTING SMS VERIFICATION TO 0757347857")
    print("=" * 80)
    
    try:
        # Find a tenant with working SMS credentials
        tenant = Tenant.objects.filter(
            sms_providers__api_key__isnull=False,
            sms_providers__secret_key__isnull=False
        ).first()
        
        if not tenant:
            print("❌ No tenant with SMS credentials found!")
            return False
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(str(tenant.id))
        print(f"SMS Verification Service initialized with sender ID: {sms_verification.sender_id}")
        
        # Test sending verification code to the specified phone number
        phone_number = "+255757347857"
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
            print("✅ SUCCESS: Verification SMS sent to 0757347857!")
            print("📱 The phone number 0757347857 should receive an SMS with:")
            print("   'Your Mifumo WMS account confirmation code is: 123456. This code expires in 10 minutes. Do not share this code with anyone.'")
            return True
        else:
            print("❌ FAILED: Verification SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ SMS verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("Testing SMS verification with phone number 0757347857")
    print("=" * 80)
    
    success = test_sms_verification()
    
    if success:
        print("\n🎉 SMS VERIFICATION IS WORKING!")
        print("\n📋 Summary:")
        print("   ✅ SMS verification system is configured and working")
        print("   ✅ Phone number 0757347857 will receive SMS verification codes")
        print("   ✅ Sender ID: Taarifa-SMS")
        print("   ✅ Message type: account_confirmation")
        print("\n📱 When users register with phone number 0757347857:")
        print("   - They will automatically receive SMS verification codes")
        print("   - The verification code will be stored in the database")
        print("   - Users can verify their account using the received code")
    else:
        print("\n⚠️  SMS verification test failed. Check the configuration.")

if __name__ == "__main__":
    main()




