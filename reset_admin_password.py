#!/usr/bin/env python3
"""
Reset password for admin@mifumo.com
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

def reset_admin_password():
    """Reset password for admin@mifumo.com."""
    print("=" * 80)
    print("RESETTING PASSWORD FOR ADMIN@MIFUMO.COM")
    print("=" * 80)
    
    try:
        # Find the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User found: {user.email}")
        print(f"  is_active: {user.is_active}")
        print(f"  is_staff: {user.is_staff}")
        print(f"  is_superuser: {user.is_superuser}")
        
        # Reset password
        new_password = "admin123"
        print(f"\nResetting password to: {new_password}")
        
        user.set_password(new_password)
        user.save()
        
        print("SUCCESS: Password reset successfully!")
        
        # Verify the password
        if user.check_password(new_password):
            print("SUCCESS: Password verification successful!")
        else:
            print("FAILED: Password verification failed!")
        
        # Test authentication
        from django.contrib.auth import authenticate
        authenticated_user = authenticate(email='admin@mifumo.com', password=new_password)
        if authenticated_user:
            print("SUCCESS: User authentication successful!")
            print("The user can now login to the admin panel.")
        else:
            print("FAILED: User authentication failed!")
        
        print(f"\nLogin credentials:")
        print(f"  Email: admin@mifumo.com")
        print(f"  Password: admin123")
        print(f"  Admin Panel URL: http://127.0.0.1:8001/admin/")
        
    except Exception as e:
        print(f"Error resetting admin password: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run password reset."""
    print("Resetting Password for admin@mifumo.com")
    print("=" * 80)
    
    reset_admin_password()

if __name__ == "__main__":
    main()
