#!/usr/bin/env python3
"""
Debug frontend password reset issue
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

def debug_frontend_password_reset():
    """Debug frontend password reset issue."""
    print("=" * 80)
    print("DEBUGGING FRONTEND PASSWORD RESET ISSUE")
    print("=" * 80)
    
    try:
        # Get the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Current verification code: {user.phone_verification_code}")
        print(f"Code sent at: {user.phone_verification_sent_at}")
        
        # Step 1: Send a fresh verification code
        print("\n" + "=" * 80)
        print("STEP 1: SENDING FRESH VERIFICATION CODE")
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
        print(f"Fresh verification code: {verification_code}")
        
        # Step 2: Test the exact API call that frontend would make
        print("\n" + "=" * 80)
        print("STEP 2: TESTING FRONTEND API CALL")
        print("=" * 80)
        
        # Test with the exact data format the frontend would send
        reset_data = {
            'phone_number': user.phone_number,  # This might be the issue - format
            'verification_code': verification_code,
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        print(f"Sending data: {reset_data}")
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/reset-password/',
            json=reset_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Password reset worked!")
        else:
            print("FAILED: Password reset failed")
            
            # Let's check what the user looks like in the database
            print("\n" + "=" * 80)
            print("CHECKING USER STATE IN DATABASE")
            print("=" * 80)
            
            user.refresh_from_db()
            print(f"User phone: {user.phone_number}")
            print(f"User verification code: {user.phone_verification_code}")
            print(f"User code sent at: {user.phone_verification_sent_at}")
            
            # Test verification code lookup
            print("\n" + "=" * 80)
            print("TESTING VERIFICATION CODE LOOKUP")
            print("=" * 80)
            
            # Try to find user by phone number
            found_user = User.objects.filter(phone_number=user.phone_number).first()
            if found_user:
                print(f"Found user by phone: {found_user.email}")
                print(f"Found user verification code: {found_user.phone_verification_code}")
                print(f"Found user code sent at: {found_user.phone_verification_sent_at}")
            else:
                print("No user found by phone number!")
        
    except Exception as e:
        print(f"Error debugging frontend password reset: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging Frontend Password Reset Issue")
    print("=" * 80)
    
    debug_frontend_password_reset()

if __name__ == "__main__":
    main()
