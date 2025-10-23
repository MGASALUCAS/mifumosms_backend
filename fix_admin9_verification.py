#!/usr/bin/env python3
"""
Fix admin9@mifumo.com verification code
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

def fix_admin9_verification():
    """Fix admin9@mifumo.com verification code."""
    print("=" * 80)
    print("FIXING ADMIN9@MIFUMO.COM VERIFICATION CODE")
    print("=" * 80)
    
    try:
        # Get the user
        user = User.objects.filter(email='admin9@mifumo.com').first()
        if not user:
            print("User admin9@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Phone Verified: {user.phone_verified}")
        print(f"Current Verification Code: {user.phone_verification_code}")
        
        # Send a fresh verification code
        print("\nSending fresh verification code...")
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        result = sms_verification.send_verification_code(user, "account_confirmation")
        print(f"Send result: {result}")
        
        if result.get('success'):
            # Refresh user to get the new code
            user.refresh_from_db()
            verification_code = user.phone_verification_code
            print(f"New verification code: {verification_code}")
            
            # Test verification
            print("\nTesting verification...")
            verification_data = {
                'phone_number': user.phone_number,
                'verification_code': verification_code
            }
            
            response = requests.post(
                'http://127.0.0.1:8001/api/auth/sms/verify-code/',
                json=verification_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Verification response status: {response.status_code}")
            print(f"Verification response: {response.text}")
            
            if response.status_code == 200:
                print("SUCCESS: Verification worked!")
                print("The user can now complete the verification process.")
            else:
                print("FAILED: Verification failed")
        else:
            print("FAILED: Could not send verification code")
            print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"Error fixing admin9 verification: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run fix."""
    print("Fixing admin9@mifumo.com Verification Code")
    print("=" * 80)
    
    fix_admin9_verification()

if __name__ == "__main__":
    main()
