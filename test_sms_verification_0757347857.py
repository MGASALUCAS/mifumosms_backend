#!/usr/bin/env python3
"""
Test SMS verification with the specified phone number 0757347857
This script tests the complete SMS verification flow for account confirmation.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from accounts.services.sms_verification import SMSVerificationService
from tenants.models import Tenant
from messaging.services.sms_service import SMSService
from messaging.services.beem_sms import BeemSMSService

def test_sms_to_specified_phone():
    """Test sending SMS to 0757347857 using Taarifa-SMS."""
    print("=" * 80)
    print("TESTING SMS TO 0757347857 WITH TAARIFA-SMS")
    print("=" * 80)
    
    try:
        # Initialize BeemSMS service
        beem_service = BeemSMSService()
        print("BeemSMS service initialized successfully")
        
        # Test sending SMS to the specified phone number
        phone_number = "+255757347857"  # Tanzanian number format
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Using sender ID: Taarifa-SMS")
        
        result = beem_service.send_sms(
            message="Test message from Mifumo WMS to 0757347857 - Account confirmation test",
            recipients=[phone_number],
            source_addr="Taarifa-SMS",
            recipient_ids=["test_0757347857"]
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS sent to 0757347857!")
            return True
        else:
            print("FAILED: SMS not sent to 0757347857")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"BeemSMS service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sms_verification_service():
    """Test SMS verification service with the specified phone number."""
    print("\n" + "=" * 80)
    print("TESTING SMS VERIFICATION SERVICE TO 0757347857")
    print("=" * 80)
    
    try:
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found!")
            return False
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(str(tenant.id))
        print(f"SMS Verification Service initialized with sender ID: {sms_verification.sender_id}")
        
        # Test sending verification code to the specified phone number
        phone_number = "+255757347857"
        code = "123456"
        
        print(f"Sending verification SMS to: {phone_number}")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=code,
            message_type="account_confirmation"
        )
        
        print(f"SMS verification result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Verification SMS sent to 0757347857!")
            return True
        else:
            print("FAILED: Verification SMS not sent to 0757347857")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"SMS verification error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_registration_with_sms():
    """Test user registration with SMS verification."""
    print("\n" + "=" * 80)
    print("TESTING USER REGISTRATION WITH SMS VERIFICATION")
    print("=" * 80)
    
    try:
        # Create a test user with the specified phone number
        test_email = "test0757347857@example.com"
        test_phone = "0757347857"
        
        # Clean up any existing test user
        User.objects.filter(email=test_email).delete()
        
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
        
        # Test sending verification code
        tenant = user.get_tenant()
        sms_verification = SMSVerificationService(str(tenant.id))
        
        print("Sending account confirmation SMS...")
        result = sms_verification.send_verification_code(user, "account_confirmation")
        
        print(f"Verification code result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Account confirmation SMS sent!")
            print(f"Verification code: {user.phone_verification_code}")
            return True
        else:
            print("FAILED: Account confirmation SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"User registration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sms_service_direct():
    """Test SMS service directly with the specified phone number."""
    print("\n" + "=" * 80)
    print("TESTING SMS SERVICE DIRECT TO 0757347857")
    print("=" * 80)
    
    try:
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found!")
            return False
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test SMS service
        sms_service = SMSService(str(tenant.id))
        print("SMS Service initialized successfully")
        
        # Test sending SMS to the specified phone number
        phone_number = "255757347857"  # International format without +
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Using sender ID: Taarifa-SMS")
        
        result = sms_service.send_sms(
            to=phone_number,
            message="Test message from SMS Service to 0757347857 - Direct service test",
            sender_id="Taarifa-SMS",
            recipient_id="test_direct_0757347857"
        )
        
        print(f"SMS service result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS sent via SMS Service to 0757347857!")
            return True
        else:
            print("FAILED: SMS not sent via SMS Service to 0757347857")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"SMS service error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing SMS verification with phone number 0757347857")
    print("=" * 80)
    
    results = []
    
    # Test 1: Direct Beem SMS
    print("\n1. Testing direct Beem SMS...")
    results.append(("Direct Beem SMS", test_sms_to_specified_phone()))
    
    # Test 2: SMS Verification Service
    print("\n2. Testing SMS Verification Service...")
    results.append(("SMS Verification Service", test_sms_verification_service()))
    
    # Test 3: SMS Service
    print("\n3. Testing SMS Service...")
    results.append(("SMS Service", test_sms_service_direct()))
    
    # Test 4: User Registration with SMS
    print("\n4. Testing User Registration with SMS...")
    results.append(("User Registration with SMS", test_user_registration_with_sms()))
    
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
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! SMS verification is working with 0757347857")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()







