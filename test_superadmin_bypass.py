#!/usr/bin/env python3
"""
Test superadmin SMS verification bypass
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from accounts.services.sms_verification import SMSVerificationService

def test_superadmin_bypass():
    """Test superadmin SMS verification bypass."""
    print("=" * 80)
    print("TESTING SUPERADMIN SMS VERIFICATION BYPASS")
    print("=" * 80)
    
    try:
        # Test with superadmin user
        superadmin_user = User.objects.filter(is_superuser=True).first()
        if not superadmin_user:
            print("No superadmin user found!")
            return
        
        print(f"Testing with superadmin user: {superadmin_user.email}")
        print(f"  is_superuser: {superadmin_user.is_superuser}")
        print(f"  phone_number: {superadmin_user.phone_number}")
        print(f"  phone_verified: {superadmin_user.phone_verified}")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(str(superadmin_user.get_tenant().id))
        
        # Test 1: Send verification code (should be bypassed)
        print(f"\n" + "=" * 50)
        print("TEST 1: SEND VERIFICATION CODE (should be bypassed)")
        print("=" * 50)
        
        result = sms_verification.send_verification_code(superadmin_user, "verification")
        print(f"Send verification code result: {result}")
        
        if result.get('success') and result.get('bypassed'):
            print("SUCCESS: SMS verification bypassed for superadmin user!")
        else:
            print("FAILED: SMS verification not bypassed for superadmin user!")
        
        # Check if phone is now verified
        superadmin_user.refresh_from_db()
        print(f"Phone verified after bypass: {superadmin_user.phone_verified}")
        
        # Test 2: Verify code (should be bypassed)
        print(f"\n" + "=" * 50)
        print("TEST 2: VERIFY CODE (should be bypassed)")
        print("=" * 50)
        
        verify_result = sms_verification.verify_code(superadmin_user, "any_code")
        print(f"Verify code result: {verify_result}")
        
        if verify_result.get('success') and verify_result.get('bypassed'):
            print("SUCCESS: Code verification bypassed for superadmin user!")
        else:
            print("FAILED: Code verification not bypassed for superadmin user!")
        
        # Test 3: Test with regular user (should not be bypassed)
        print(f"\n" + "=" * 50)
        print("TEST 3: REGULAR USER (should NOT be bypassed)")
        print("=" * 50)
        
        regular_user = User.objects.filter(is_superuser=False).first()
        if regular_user:
            print(f"Testing with regular user: {regular_user.email}")
            print(f"  is_superuser: {regular_user.is_superuser}")
            print(f"  phone_number: {regular_user.phone_number}")
            
            regular_sms_verification = SMSVerificationService(str(regular_user.get_tenant().id))
            
            result = regular_sms_verification.send_verification_code(regular_user, "verification")
            print(f"Send verification code result: {result}")
            
            if result.get('success') and not result.get('bypassed'):
                print("SUCCESS: SMS verification NOT bypassed for regular user!")
            else:
                print("FAILED: SMS verification was bypassed for regular user!")
        else:
            print("No regular user found for testing")
        
        # Test 4: Test registration flow for superadmin
        print(f"\n" + "=" * 50)
        print("TEST 4: REGISTRATION FLOW FOR SUPERADMIN")
        print("=" * 50)
        
        # Create a test superadmin user
        test_superadmin_data = {
            'email': 'test_superadmin@example.com',
            'first_name': 'Test',
            'last_name': 'Superadmin',
            'password': 'TestPassword123#',
            'password_confirm': 'TestPassword123#',
            'phone_number': '0699999999',
            'timezone': 'UTC'
        }
        
        # First, create the user as superadmin
        test_user = User.objects.create(
            email=test_superadmin_data['email'],
            first_name=test_superadmin_data['first_name'],
            last_name=test_superadmin_data['last_name'],
            phone_number=test_superadmin_data['phone_number'],
            timezone=test_superadmin_data['timezone'],
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        
        # Set tenant
        tenant = superadmin_user.get_tenant()
        test_user.tenant_id = tenant.id
        test_user.save()
        
        print(f"Created test superadmin user: {test_user.email}")
        print(f"  is_superuser: {test_user.is_superuser}")
        print(f"  phone_number: {test_user.phone_number}")
        print(f"  phone_verified: {test_user.phone_verified}")
        
        # Test SMS verification service
        test_sms_verification = SMSVerificationService(str(test_user.get_tenant().id))
        
        result = test_sms_verification.send_verification_code(test_user, "account_confirmation")
        print(f"Send verification code result: {result}")
        
        if result.get('success') and result.get('bypassed'):
            print("SUCCESS: SMS verification bypassed for new superadmin user!")
        else:
            print("FAILED: SMS verification not bypassed for new superadmin user!")
        
        # Check if phone is now verified
        test_user.refresh_from_db()
        print(f"Phone verified after bypass: {test_user.phone_verified}")
        
        # Clean up
        test_user.delete()
        print("Cleaned up test user")
        
    except Exception as e:
        print(f"Error testing superadmin bypass: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Superadmin SMS Verification Bypass")
    print("=" * 80)
    
    test_superadmin_bypass()

if __name__ == "__main__":
    main()
