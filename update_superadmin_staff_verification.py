#!/usr/bin/env python3
"""
Update database to mark all superadmin and staff users as phone verified
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

def update_superadmin_staff_verification():
    """Update database to mark all superadmin and staff users as phone verified."""
    print("=" * 80)
    print("UPDATING DATABASE FOR SUPERADMIN AND STAFF PHONE VERIFICATION")
    print("=" * 80)
    
    try:
        # Find all superadmin users
        superadmin_users = User.objects.filter(is_superuser=True)
        print(f"Found {superadmin_users.count()} superadmin users")
        
        # Find all staff users (excluding superadmin to avoid duplicates)
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        print(f"Found {staff_users.count()} staff users (non-superadmin)")
        
        # Update superadmin users
        print(f"\n" + "=" * 50)
        print("UPDATING SUPERADMIN USERS")
        print("=" * 50)
        
        superadmin_updated = 0
        for user in superadmin_users:
            if not user.phone_verified:
                user.phone_verified = True
                user.save(update_fields=['phone_verified'])
                superadmin_updated += 1
                print(f"  Updated {user.email}: phone_verified = True")
            else:
                print(f"  Already verified {user.email}")
        
        print(f"Updated {superadmin_updated} superadmin users")
        
        # Update staff users
        print(f"\n" + "=" * 50)
        print("UPDATING STAFF USERS")
        print("=" * 50)
        
        staff_updated = 0
        for user in staff_users:
            if not user.phone_verified:
                user.phone_verified = True
                user.save(update_fields=['phone_verified'])
                staff_updated += 1
                print(f"  Updated {user.email}: phone_verified = True")
            else:
                print(f"  Already verified {user.email}")
        
        print(f"Updated {staff_updated} staff users")
        
        # Final verification
        print(f"\n" + "=" * 50)
        print("FINAL VERIFICATION")
        print("=" * 50)
        
        # Check superadmin users
        superadmin_unverified = User.objects.filter(is_superuser=True, phone_verified=False).count()
        print(f"Superadmin users not verified: {superadmin_unverified}")
        
        # Check staff users
        staff_unverified = User.objects.filter(is_staff=True, is_superuser=False, phone_verified=False).count()
        print(f"Staff users not verified: {staff_unverified}")
        
        # Show final statistics
        total_superadmin = User.objects.filter(is_superuser=True).count()
        total_staff = User.objects.filter(is_staff=True, is_superuser=False).count()
        verified_superadmin = User.objects.filter(is_superuser=True, phone_verified=True).count()
        verified_staff = User.objects.filter(is_staff=True, is_superuser=False, phone_verified=True).count()
        
        print(f"\nFinal Statistics:")
        print(f"  Total superadmin users: {total_superadmin}")
        print(f"  Verified superadmin users: {verified_superadmin}")
        print(f"  Total staff users: {total_staff}")
        print(f"  Verified staff users: {verified_staff}")
        
        if superadmin_unverified == 0 and staff_unverified == 0:
            print("\nSUCCESS: All superadmin and staff users are now phone verified!")
            print("They will bypass SMS verification automatically.")
        else:
            print(f"\nWARNING: Some users are still not verified!")
            print(f"  Superadmin unverified: {superadmin_unverified}")
            print(f"  Staff unverified: {staff_unverified}")
        
        # Show all superadmin and staff users
        print(f"\n" + "=" * 50)
        print("ALL SUPERADMIN AND STAFF USERS")
        print("=" * 50)
        
        all_admin_staff = User.objects.filter(
            models.Q(is_superuser=True) | models.Q(is_staff=True)
        ).order_by('-is_superuser', 'email')
        
        for user in all_admin_staff:
            user_type = "SUPERADMIN" if user.is_superuser else "STAFF"
            verified_status = "VERIFIED" if user.phone_verified else "NOT VERIFIED"
            print(f"  {user_type}: {user.email} - {verified_status}")
        
    except Exception as e:
        print(f"Error updating superadmin/staff verification: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the update."""
    print("Updating Database for Superadmin and Staff Phone Verification")
    print("=" * 80)
    
    update_superadmin_staff_verification()

if __name__ == "__main__":
    main()
