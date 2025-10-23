#!/usr/bin/env python3
"""
Verify that all superadmin and staff users are phone verified
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
from django.db import models

def verify_superadmin_staff_status():
    """Verify that all superadmin and staff users are phone verified."""
    print("=" * 80)
    print("VERIFYING SUPERADMIN AND STAFF PHONE VERIFICATION STATUS")
    print("=" * 80)
    
    try:
        # Get all superadmin and staff users
        admin_staff_users = User.objects.filter(
            models.Q(is_superuser=True) | models.Q(is_staff=True)
        ).order_by('-is_superuser', 'email')
        
        print(f"Total admin/staff users: {admin_staff_users.count()}")
        
        # Check verification status
        verified_count = 0
        unverified_count = 0
        
        print(f"\n" + "=" * 50)
        print("VERIFICATION STATUS")
        print("=" * 50)
        
        for user in admin_staff_users:
            user_type = "SUPERADMIN" if user.is_superuser else "STAFF"
            verified_status = "VERIFIED" if user.phone_verified else "NOT VERIFIED"
            
            if user.phone_verified:
                verified_count += 1
            else:
                unverified_count += 1
            
            print(f"  {user_type}: {user.email} - {verified_status}")
        
        print(f"\nSummary:")
        print(f"  Verified: {verified_count}")
        print(f"  Not verified: {unverified_count}")
        
        if unverified_count == 0:
            print(f"\nSUCCESS: All superadmin and staff users are phone verified!")
            print(f"They will bypass SMS verification automatically.")
        else:
            print(f"\nWARNING: {unverified_count} users are still not verified!")
            print(f"Run the update script to fix this.")
        
        # Test SMS verification bypass
        print(f"\n" + "=" * 50)
        print("TESTING SMS VERIFICATION BYPASS")
        print("=" * 50)
        
        from accounts.services.sms_verification import SMSVerificationService
        
        # Test with a superadmin user
        superadmin_user = User.objects.filter(is_superuser=True).first()
        if superadmin_user:
            print(f"Testing with superadmin: {superadmin_user.email}")
            
            sms_verification = SMSVerificationService(str(superadmin_user.get_tenant().id))
            
            # Test send verification code
            result = sms_verification.send_verification_code(superadmin_user, "verification")
            print(f"Send verification code result: {result}")
            
            if result.get('success') and result.get('bypassed'):
                print("SUCCESS: SMS verification bypassed for superadmin!")
            else:
                print("FAILED: SMS verification not bypassed!")
            
            # Test verify code
            verify_result = sms_verification.verify_code(superadmin_user, "any_code")
            print(f"Verify code result: {verify_result}")
            
            if verify_result.get('success') and verify_result.get('bypassed'):
                print("SUCCESS: Code verification bypassed for superadmin!")
            else:
                print("FAILED: Code verification not bypassed!")
        
    except Exception as e:
        print(f"Error verifying status: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run verification."""
    print("Verifying Superadmin and Staff Phone Verification Status")
    print("=" * 80)
    
    verify_superadmin_staff_status()

if __name__ == "__main__":
    main()
