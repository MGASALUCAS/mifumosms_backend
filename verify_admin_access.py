#!/usr/bin/env python3
"""
Verify admin panel access for admin@mifumo.com
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

def verify_admin_access():
    """Verify admin panel access for admin@mifumo.com."""
    print("=" * 80)
    print("VERIFYING ADMIN PANEL ACCESS FOR ADMIN@MIFUMO.COM")
    print("=" * 80)
    
    try:
        # Find the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
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
        
        # Test authentication
        print(f"\n" + "=" * 50)
        print("AUTHENTICATION TEST")
        print("=" * 50)
        
        authenticated_user = authenticate(email='admin@mifumo.com', password='admin123')
        if authenticated_user:
            print("SUCCESS: User authentication successful!")
            print(f"Authenticated user: {authenticated_user.email}")
        else:
            print("FAILED: User authentication failed!")
            return
        
        # Check admin panel access
        print(f"\n" + "=" * 50)
        print("ADMIN PANEL ACCESS CHECK")
        print("=" * 50)
        
        if user.is_active and user.is_staff:
            print("SUCCESS: User can access admin panel!")
            print("  - User is active: YES")
            print("  - User is staff: YES")
            if user.is_superuser:
                print("  - User is superuser: YES")
                print("  - Full admin access: YES")
            else:
                print("  - User is superuser: NO")
                print("  - Limited admin access: YES")
        else:
            print("FAILED: User cannot access admin panel!")
            if not user.is_active:
                print("  - User is not active: YES")
            if not user.is_staff:
                print("  - User is not staff: YES")
        
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
        
        # Final login instructions
        print(f"\n" + "=" * 50)
        print("LOGIN INSTRUCTIONS")
        print("=" * 50)
        
        print("To login to the admin panel:")
        print("1. Go to: http://127.0.0.1:8001/admin/")
        print("2. Enter email: admin@mifumo.com")
        print("3. Enter password: admin123")
        print("4. Click 'Log in'")
        
        print(f"\nIf you still cannot login, check:")
        print("1. Django server is running on port 8001")
        print("2. No firewall blocking the connection")
        print("3. Browser cache is cleared")
        print("4. Try incognito/private browsing mode")
        
    except Exception as e:
        print(f"Error verifying admin access: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run verification."""
    print("Verifying Admin Panel Access for admin@mifumo.com")
    print("=" * 80)
    
    verify_admin_access()

if __name__ == "__main__":
    main()
