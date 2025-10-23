#!/usr/bin/env python3
"""
Debug verification code issue
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

def debug_verification_code():
    """Debug verification code issue."""
    print("=" * 80)
    print("DEBUGGING VERIFICATION CODE ISSUE")
    print("=" * 80)
    
    try:
        # Get the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Phone Verified: {user.phone_verified}")
        print(f"Verification Code: {user.phone_verification_code}")
        print(f"Code Sent At: {user.phone_verification_sent_at}")
        print(f"Verification Attempts: {user.phone_verification_attempts}")
        print(f"Locked Until: {user.phone_verification_locked_until}")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        
        # Test sending verification code
        print("\n" + "=" * 80)
        print("SENDING VERIFICATION CODE")
        print("=" * 80)
        
        result = sms_verification.send_verification_code(user, "password_reset")
        print(f"Send result: {result}")
        
        if result.get('success'):
            # Refresh user from database
            user.refresh_from_db()
            print(f"After sending - Verification Code: {user.phone_verification_code}")
            print(f"After sending - Code Sent At: {user.phone_verification_sent_at}")
            
            # Test verifying the code
            print("\n" + "=" * 80)
            print("VERIFYING CODE")
            print("=" * 80)
            
            verify_result = sms_verification.verify_code(user, user.phone_verification_code)
            print(f"Verify result: {verify_result}")
            
            if verify_result.get('success'):
                print("SUCCESS: Code verification worked!")
            else:
                print("FAILED: Code verification failed")
                print(f"Error: {verify_result.get('error')}")
        else:
            print("FAILED: Could not send verification code")
            print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"Error debugging verification code: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging Verification Code Issue")
    print("=" * 80)
    
    debug_verification_code()

if __name__ == "__main__":
    main()
