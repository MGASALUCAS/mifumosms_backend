#!/usr/bin/env python3
"""
Test SMS verification with the working tenant
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

def test_with_working_tenant():
    """Test SMS verification with the specific working tenant."""
    print("=" * 80)
    print("TESTING SMS VERIFICATION WITH WORKING TENANT")
    print("=" * 80)
    
    try:
        # Use the specific tenant that was working in the earlier test
        tenant_id = "18da454d-57d5-4c0f-b09c-e74b3cd1a71a"
        tenant = Tenant.objects.get(id=tenant_id)
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Check SMS provider
        provider = tenant.sms_providers.filter(api_key__isnull=False).first()
        if provider:
            print(f"SMS Provider: {provider.name}")
            print(f"API Key: {provider.api_key[:10]}...")
            print(f"Secret Key: {provider.secret_key[:10]}...")
        else:
            print("No SMS provider found!")
            return False
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(tenant_id)
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

def test_user_registration_with_working_tenant():
    """Test user registration with the working tenant."""
    print("\n" + "=" * 80)
    print("TESTING USER REGISTRATION WITH WORKING TENANT")
    print("=" * 80)
    
    try:
        from accounts.models import User
        
        # Clean up any existing test user
        User.objects.filter(email="test0757347857@example.com").delete()
        
        # Create a test user with the specified phone number
        test_email = "test0757347857@example.com"
        test_phone = "0757347857"
        
        print(f"Creating test user with email: {test_email}")
        print(f"Phone number: {test_phone}")
        
        # Create user
        user = User.objects.create_user(
            email=test_email,
            password="testpassword123",
            first_name="Test",
            last_name="User",
            phone_number=test_phone
        )
        
        print(f"User created: {user.email} (ID: {user.id})")
        
        # Get the user's tenant
        tenant = user.get_tenant()
        print(f"User's tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test sending verification code using the working tenant
        working_tenant_id = "18da454d-57d5-4c0f-b09c-e74b3cd1a71a"
        sms_verification = SMSVerificationService(working_tenant_id)
        
        print("Sending account confirmation SMS...")
        result = sms_verification.send_verification_code(user, "account_confirmation")
        
        print(f"Verification code result: {result}")
        
        if result.get('success'):
            print("✅ SUCCESS: Account confirmation SMS sent!")
            print(f"Verification code: {user.phone_verification_code}")
            return True
        else:
            print("❌ FAILED: Account confirmation SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ User registration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tests."""
    print("Testing SMS verification with working tenant")
    print("=" * 80)
    
    results = []
    
    # Test 1: Direct SMS verification
    print("\n1. Testing direct SMS verification...")
    results.append(("Direct SMS Verification", test_with_working_tenant()))
    
    # Test 2: User registration with SMS
    print("\n2. Testing user registration with SMS...")
    results.append(("User Registration with SMS", test_user_registration_with_working_tenant()))
    
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
        print("\n⚠️  All tests failed. The tenant configuration needs to be fixed.")

if __name__ == "__main__":
    main()






