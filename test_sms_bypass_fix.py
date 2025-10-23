#!/usr/bin/env python3
"""
Test SMS verification bypass fix for superadmin users
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

def test_sms_bypass_fix():
    """Test SMS verification bypass fix for superadmin users."""
    print("=" * 80)
    print("TESTING SMS VERIFICATION BYPASS FIX FOR SUPERADMIN USERS")
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
        print(f"  phone_verified: {admin_user.phone_verified}")
        
        # Test send verification code
        print(f"\n" + "=" * 50)
        print("TESTING SEND VERIFICATION CODE")
        print("=" * 50)
        
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
                print("No SMS was sent, phone automatically verified")
            else:
                print("WARNING: SMS verification not bypassed!")
                print("SMS was sent instead of bypassing")
        else:
            print("FAILED: SMS verification failed!")
        
        # Test verify code
        print(f"\n" + "=" * 50)
        print("TESTING VERIFY CODE")
        print("=" * 50)
        
        verify_data = {
            'phone_number': admin_user.phone_number,
            'verification_code': '123456'  # Any code should work for superadmin
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
                print("Any code was accepted, phone automatically verified")
            else:
                print("WARNING: Code verification not bypassed!")
                print("Code was validated normally")
        else:
            print("FAILED: Code verification failed!")
        
        # Test account confirmation
        print(f"\n" + "=" * 50)
        print("TESTING ACCOUNT CONFIRMATION")
        print("=" * 50)
        
        confirm_data = {
            'verification_code': '123456'  # Any code should work for superadmin
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/confirm-account/',
            json=confirm_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Confirm account response status: {response.status_code}")
        print(f"Confirm account response: {response.text}")
        
        if response.status_code == 200:
            confirm_response = response.json()
            if confirm_response.get('bypassed'):
                print("SUCCESS: Account confirmation bypassed for superadmin!")
                print("Account automatically confirmed")
            else:
                print("WARNING: Account confirmation not bypassed!")
                print("Account confirmation was processed normally")
        else:
            print("FAILED: Account confirmation failed!")
        
        # Summary
        print(f"\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        print("For superadmin users (admin@mifumo.com):")
        print("1. Login API now returns is_superuser, is_staff, phone_verified")
        print("2. Frontend should check these fields to bypass verification")
        print("3. SMS verification endpoints bypass verification for superadmin")
        print("4. No actual SMS is sent, phone is automatically verified")
        print("5. Any verification code is accepted")
        
        print(f"\nFrontend logic should be:")
        print(f"if (user.is_superuser || user.is_staff || user.phone_verified) {{")
        print(f"  // Skip verification, allow dashboard access")
        print(f"  // Don't show 'Account Verification Required'")
        print(f"}} else {{")
        print(f"  // Show verification required")
        print(f"  // Show 'Account Verification Required'")
        print(f"}}")
        
    except Exception as e:
        print(f"Error testing SMS bypass fix: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing SMS Verification Bypass Fix for Superadmin Users")
    print("=" * 80)
    
    test_sms_bypass_fix()

if __name__ == "__main__":
    main()
