#!/usr/bin/env python3
"""
Debug frontend verification issue for superadmin users
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

def debug_frontend_verification():
    """Debug frontend verification issue for superadmin users."""
    print("=" * 80)
    print("DEBUGGING FRONTEND VERIFICATION ISSUE FOR SUPERADMIN USERS")
    print("=" * 80)
    
    try:
        # Get admin user
        admin_user = User.objects.filter(email='admin@mifumo.com').first()
        if not admin_user:
            print("Admin user not found!")
            return
        
        print(f"Admin user: {admin_user.email}")
        print(f"  is_superuser: {admin_user.is_superuser}")
        print(f"  is_staff: {admin_user.is_staff}")
        print(f"  is_active: {admin_user.is_active}")
        print(f"  phone_verified: {admin_user.phone_verified}")
        print(f"  phone_number: {admin_user.phone_number}")
        
        # Test login API
        print(f"\n" + "=" * 50)
        print("TESTING LOGIN API")
        print("=" * 50)
        
        login_data = {
            'email': 'admin@mifumo.com',
            'password': 'admin123'
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login response status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            login_response = response.json()
            print("SUCCESS: Login successful!")
            
            # Check if user data includes phone_verified
            if 'user' in login_response:
                user_data = login_response['user']
                print(f"User data from login:")
                print(f"  phone_verified: {user_data.get('phone_verified')}")
                print(f"  is_superuser: {user_data.get('is_superuser')}")
                print(f"  is_staff: {user_data.get('is_staff')}")
                
                # This is what the frontend should check
                if user_data.get('is_superuser') or user_data.get('is_staff'):
                    print("SUCCESS: User is superuser/staff - should bypass verification!")
                else:
                    print("WARNING: User is not superuser/staff - verification required!")
            else:
                print("WARNING: No user data in login response!")
        else:
            print("FAILED: Login failed!")
            return
        
        # Test SMS verification endpoints
        print(f"\n" + "=" * 50)
        print("TESTING SMS VERIFICATION ENDPOINTS")
        print("=" * 50)
        
        # Test send verification code
        sms_data = {
            'phone_number': admin_user.phone_number,
            'message_type': 'verification'
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/send-code/',
            json=sms_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Send SMS code response status: {response.status_code}")
        print(f"Send SMS code response: {response.text}")
        
        if response.status_code == 200:
            sms_response = response.json()
            if sms_response.get('bypassed'):
                print("SUCCESS: SMS verification bypassed for superadmin!")
            else:
                print("WARNING: SMS verification not bypassed!")
        else:
            print("FAILED: SMS verification failed!")
        
        # Test verify code
        verify_data = {
            'phone_number': admin_user.phone_number,
            'verification_code': 'any_code'
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/verify-code/',
            json=verify_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Verify code response status: {response.status_code}")
        print(f"Verify code response: {response.text}")
        
        if response.status_code == 200:
            verify_response = response.json()
            if verify_response.get('bypassed'):
                print("SUCCESS: Code verification bypassed for superadmin!")
            else:
                print("WARNING: Code verification not bypassed!")
        else:
            print("FAILED: Code verification failed!")
        
        # Check what the frontend should do
        print(f"\n" + "=" * 50)
        print("FRONTEND LOGIC CHECK")
        print("=" * 50)
        
        print("The frontend should check:")
        print("1. If user.is_superuser === true -> Skip verification")
        print("2. If user.is_staff === true -> Skip verification")
        print("3. If user.phone_verified === true -> Skip verification")
        print("4. Otherwise -> Show verification required")
        
        print(f"\nFor admin@mifumo.com:")
        print(f"  is_superuser: {admin_user.is_superuser} -> Should skip verification")
        print(f"  is_staff: {admin_user.is_staff} -> Should skip verification")
        print(f"  phone_verified: {admin_user.phone_verified} -> Should skip verification")
        
        if admin_user.is_superuser or admin_user.is_staff or admin_user.phone_verified:
            print("SUCCESS: User should bypass verification!")
            print("The frontend should NOT show 'Account Verification Required'")
        else:
            print("WARNING: User should NOT bypass verification!")
            print("The frontend should show 'Account Verification Required'")
        
    except Exception as e:
        print(f"Error debugging frontend verification: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging Frontend Verification Issue for Superadmin Users")
    print("=" * 80)
    
    debug_frontend_verification()

if __name__ == "__main__":
    main()
