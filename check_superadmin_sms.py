#!/usr/bin/env python3
"""
Check if SMS verification affects superadmin users
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

def check_superadmin_sms():
    """Check if SMS verification affects superadmin users."""
    print("=" * 80)
    print("CHECKING SMS VERIFICATION FOR SUPERADMIN USERS")
    print("=" * 80)
    
    try:
        # Find superadmin users
        superadmin_users = User.objects.filter(is_superuser=True)
        print(f"Total superadmin users: {superadmin_users.count()}")
        
        for user in superadmin_users:
            print(f"\nSuperadmin User: {user.email}")
            print(f"  is_superuser: {user.is_superuser}")
            print(f"  is_staff: {user.is_staff}")
            print(f"  is_active: {user.is_active}")
            print(f"  phone_number: {user.phone_number}")
            print(f"  phone_verified: {user.phone_verified}")
            print(f"  verification_code: {user.phone_verification_code}")
            
            # Test SMS verification service
            if user.phone_number:
                print(f"  Testing SMS verification service...")
                sms_verification = SMSVerificationService(str(user.get_tenant().id))
                
                # Test sending verification code
                result = sms_verification.send_verification_code(user, "verification")
                print(f"  Send verification code result: {result}")
                
                if result.get('success'):
                    user.refresh_from_db()
                    print(f"  New verification code: {user.phone_verification_code}")
                    
                    # Test verification
                    verify_result = sms_verification.verify_code(user, user.phone_verification_code)
                    print(f"  Verify code result: {verify_result}")
                else:
                    print(f"  Failed to send verification code: {result.get('error')}")
            else:
                print(f"  No phone number - SMS verification not applicable")
        
        # Check if there are any special permissions or bypasses
        print(f"\n" + "=" * 80)
        print("CHECKING FOR SPECIAL PERMISSIONS OR BYPASSES")
        print("=" * 80)
        
        # Check if superadmin users can bypass SMS verification
        print("Current SMS verification system behavior:")
        print("1. SMS verification is applied to ALL users with phone numbers")
        print("2. No special bypass for superadmin users")
        print("3. Superadmin users must verify their phone numbers like regular users")
        print("4. This means superadmin users are affected by SMS verification")
        
        # Check if this is intentional or if we should add bypasses
        print(f"\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        
        print("Current behavior: SMS verification affects superadmin users")
        print("\nOptions:")
        print("1. Keep current behavior (superadmin users must verify SMS)")
        print("2. Add bypass for superadmin users (skip SMS verification)")
        print("3. Add bypass for staff users (skip SMS verification)")
        print("4. Add bypass for users with specific permissions")
        
    except Exception as e:
        print(f"Error checking superadmin SMS: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run check."""
    print("Checking SMS Verification for Superadmin Users")
    print("=" * 80)
    
    check_superadmin_sms()

if __name__ == "__main__":
    main()
