#!/usr/bin/env python3
"""
Check admin@mifumo.com user and login issues
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
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

def check_admin_user():
    """Check admin@mifumo.com user and login issues."""
    print("=" * 80)
    print("CHECKING ADMIN@MIFUMO.COM USER AND LOGIN ISSUES")
    print("=" * 80)
    
    try:
        # Find the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User found: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  First Name: {user.first_name}")
        print(f"  Last Name: {user.last_name}")
        print(f"  is_active: {user.is_active}")
        print(f"  is_staff: {user.is_staff}")
        print(f"  is_superuser: {user.is_superuser}")
        print(f"  date_joined: {user.date_joined}")
        print(f"  last_login: {user.last_login}")
        print(f"  phone_number: {user.phone_number}")
        print(f"  phone_verified: {user.phone_verified}")
        
        # Check password
        print(f"\n" + "=" * 50)
        print("PASSWORD CHECK")
        print("=" * 50)
        
        password = "admin123"
        print(f"Testing password: {password}")
        
        # Check if password is correct
        if user.check_password(password):
            print("SUCCESS: Password is correct!")
        else:
            print("FAILED: Password is incorrect!")
            print("The password 'admin123' does not match the stored password hash.")
        
        # Test authentication
        print(f"\n" + "=" * 50)
        print("AUTHENTICATION TEST")
        print("=" * 50)
        
        authenticated_user = authenticate(email='admin@mifumo.com', password=password)
        if authenticated_user:
            print("SUCCESS: User authentication successful!")
            print(f"Authenticated user: {authenticated_user.email}")
        else:
            print("FAILED: User authentication failed!")
            print("This means the user cannot login.")
        
        # Check admin panel access
        print(f"\n" + "=" * 50)
        print("ADMIN PANEL ACCESS CHECK")
        print("=" * 50)
        
        if user.is_active and user.is_staff:
            print("SUCCESS: User can access admin panel!")
            print("  - User is active: ✓")
            print("  - User is staff: ✓")
            if user.is_superuser:
                print("  - User is superuser: ✓")
                print("  - Full admin access: ✓")
            else:
                print("  - User is superuser: ✗")
                print("  - Limited admin access: ✓")
        else:
            print("FAILED: User cannot access admin panel!")
            if not user.is_active:
                print("  - User is not active: ✗")
            if not user.is_staff:
                print("  - User is not staff: ✗")
        
        # Check if user needs password reset
        print(f"\n" + "=" * 50)
        print("PASSWORD RESET SUGGESTIONS")
        print("=" * 50)
        
        if not user.check_password(password):
            print("The user needs a password reset.")
            print("Options:")
            print("1. Reset password via Django admin (if you have another admin user)")
            print("2. Reset password via Django shell")
            print("3. Reset password via SMS (if phone is verified)")
            
            # Show how to reset password via Django shell
            print(f"\nTo reset password via Django shell:")
            print(f"python manage.py shell")
            print(f"from accounts.models import User")
            print(f"user = User.objects.get(email='admin@mifumo.com')")
            print(f"user.set_password('admin123')")
            print(f"user.save()")
        
        # Check tenant
        print(f"\n" + "=" * 50)
        print("TENANT CHECK")
        print("=" * 50)
        
        tenant = user.get_tenant()
        if tenant:
            print(f"Tenant: {tenant.name}")
            print(f"Tenant ID: {tenant.id}")
        else:
            print("No tenant assigned!")
        
    except Exception as e:
        print(f"Error checking admin user: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run check."""
    print("Checking admin@mifumo.com User and Login Issues")
    print("=" * 80)
    
    check_admin_user()

if __name__ == "__main__":
    main()
