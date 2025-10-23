#!/usr/bin/env python3
"""
Test complete password reset flow
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

def test_password_reset_flow():
    """Test complete password reset flow."""
    print("=" * 80)
    print("TESTING COMPLETE PASSWORD RESET FLOW")
    print("=" * 80)
    
    try:
        # Get the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Initial verification code: {user.phone_verification_code}")
        
        # Step 1: Send forgot password SMS
        print("\n" + "=" * 80)
        print("STEP 1: SENDING FORGOT PASSWORD SMS")
        print("=" * 80)
        
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        result = sms_verification.send_verification_code(user, "password_reset")
        print(f"Send result: {result}")
        
        if not result.get('success'):
            print("FAILED: Could not send verification code")
            return
        
        # Refresh user to get the new code
        user.refresh_from_db()
        verification_code = user.phone_verification_code
        print(f"Verification code sent: {verification_code}")
        
        # Step 2: Verify code (without clearing it)
        print("\n" + "=" * 80)
        print("STEP 2: VERIFYING CODE (without clearing)")
        print("=" * 80)
        
        verify_result = sms_verification.verify_code(user, verification_code, clear_code=False)
        print(f"Verify result: {verify_result}")
        
        if not verify_result.get('success'):
            print("FAILED: Code verification failed")
            return
        
        # Check that code is still there
        user.refresh_from_db()
        print(f"Code after verification: {user.phone_verification_code}")
        
        # Step 3: Reset password
        print("\n" + "=" * 80)
        print("STEP 3: RESETTING PASSWORD")
        print("=" * 80)
        
        # Simulate the password reset API call
        reset_data = {
            'phone_number': user.phone_number,
            'verification_code': verification_code,
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        # Test the reset password endpoint
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/reset-password/',
            json=reset_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Reset password response status: {response.status_code}")
        print(f"Reset password response: {response.json()}")
        
        if response.status_code == 200:
            print("SUCCESS: Password reset completed!")
            
            # Check that code is now cleared
            user.refresh_from_db()
            print(f"Code after password reset: {user.phone_verification_code}")
        else:
            print("FAILED: Password reset failed")
        
    except Exception as e:
        print(f"Error testing password reset flow: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Complete Password Reset Flow")
    print("=" * 80)
    
    test_password_reset_flow()

if __name__ == "__main__":
    main()
