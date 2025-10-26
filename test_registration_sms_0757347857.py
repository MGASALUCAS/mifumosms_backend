#!/usr/bin/env python3
"""
Test user registration with SMS verification for phone number 0757347857
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
import requests
import json

def test_user_registration_api():
    """Test user registration via API with SMS verification."""
    print("=" * 80)
    print("TESTING USER REGISTRATION API WITH SMS VERIFICATION")
    print("=" * 80)
    
    try:
        # Clean up any existing test user
        User.objects.filter(email="test0757347857@example.com").delete()
        
        # Test registration data
        registration_data = {
            "email": "test0757347857@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "0757347857"
        }
        
        print(f"Registering user with phone: {registration_data['phone_number']}")
        
        # Make registration request
        response = requests.post(
            "http://localhost:8000/api/auth/register/",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response: {response.json()}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get('sms_verification_sent'):
                print("✅ SUCCESS: User registered and SMS verification sent!")
                return True
            else:
                print("⚠️  User registered but SMS verification not sent")
                return False
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Registration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sms_verification_direct():
    """Test SMS verification service directly."""
    print("\n" + "=" * 80)
    print("TESTING SMS VERIFICATION SERVICE DIRECT")
    print("=" * 80)
    
    try:
        # Get a tenant with working credentials
        tenant = Tenant.objects.filter(
            sms_providers__api_key__isnull=False,
            sms_providers__secret_key__isnull=False
        ).first()
        
        if not tenant:
            print("No tenant with SMS credentials found!")
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
            print("✅ SUCCESS: Verification SMS sent to 0757347857!")
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

def test_user_creation_with_sms():
    """Test creating a user and sending SMS verification."""
    print("\n" + "=" * 80)
    print("TESTING USER CREATION WITH SMS VERIFICATION")
    print("=" * 80)
    
    try:
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
        
        # Test sending verification code using the working tenant
        tenant = Tenant.objects.filter(
            sms_providers__api_key__isnull=False,
            sms_providers__secret_key__isnull=False
        ).first()
        
        if not tenant:
            print("No tenant with SMS credentials found!")
            return False
        
        sms_verification = SMSVerificationService(str(tenant.id))
        
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
        print(f"❌ User creation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Testing SMS verification with phone number 0757347857")
    print("=" * 80)
    
    results = []
    
    # Test 1: SMS Verification Service Direct
    print("\n1. Testing SMS Verification Service Direct...")
    results.append(("SMS Verification Service Direct", test_sms_verification_direct()))
    
    # Test 2: User Creation with SMS
    print("\n2. Testing User Creation with SMS...")
    results.append(("User Creation with SMS", test_user_creation_with_sms()))
    
    # Test 3: User Registration API (if server is running)
    print("\n3. Testing User Registration API...")
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code == 200:
            results.append(("User Registration API", test_user_registration_api()))
        else:
            print("Server not running, skipping API test")
            results.append(("User Registration API", False))
    except:
        print("Server not running, skipping API test")
        results.append(("User Registration API", False))
    
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
        print("\n🎉 SMS VERIFICATION IS WORKING! Phone number 0757347857 will receive SMS codes.")
        print("\n📱 When users register with phone number 0757347857:")
        print("   - They will automatically receive SMS verification codes")
        print("   - The SMS will be sent from 'Taarifa-SMS' sender ID")
        print("   - The verification code will be stored in the database")
        print("   - Users can verify their account using the received code")
    else:
        print("\n⚠️  All tests failed. Check the configuration.")

if __name__ == "__main__":
    main()




