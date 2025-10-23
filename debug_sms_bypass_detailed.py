#!/usr/bin/env python3
"""
Debug SMS bypass detailed for superadmin users
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

def debug_sms_bypass_detailed():
    """Debug SMS bypass detailed for superadmin users."""
    print("=" * 80)
    print("DEBUGGING SMS BYPASS DETAILED FOR SUPERADMIN USERS")
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
        print(f"  phone_number: {admin_user.phone_number}")
        
        # Test SMS verification service directly
        print(f"\n" + "=" * 50)
        print("TESTING SMS VERIFICATION SERVICE DIRECTLY")
        print("=" * 50)
        
        tenant = admin_user.get_tenant()
        if tenant:
            print(f"Tenant: {tenant.name} (ID: {tenant.id})")
            sms_service = SMSVerificationService(str(tenant.id))
        else:
            print("No tenant found, using default SMS service")
            sms_service = SMSVerificationService()
        
        # Test send_verification_code directly
        print(f"\nTesting send_verification_code directly...")
        result = sms_service.send_verification_code(admin_user, "verification")
        print(f"Direct send_verification_code result: {result}")
        
        if result.get('bypassed'):
            print("SUCCESS: SMS verification bypassed for superadmin!")
        else:
            print("WARNING: SMS verification not bypassed!")
        
        # Test verify_code directly
        print(f"\nTesting verify_code directly...")
        result = sms_service.verify_code(admin_user, "123456")
        print(f"Direct verify_code result: {result}")
        
        if result.get('bypassed'):
            print("SUCCESS: Code verification bypassed for superadmin!")
        else:
            print("WARNING: Code verification not bypassed!")
        
        # Test API endpoints
        print(f"\n" + "=" * 50)
        print("TESTING API ENDPOINTS")
        print("=" * 50)
        
        # Test send verification code API
        sms_data = {
            'phone_number': admin_user.phone_number,
            'message_type': 'verification'
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/send-code/',
            json=sms_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Send SMS code API response status: {response.status_code}")
        print(f"Send SMS code API response: {response.text}")
        
        if response.status_code == 200:
            sms_response = response.json()
            if sms_response.get('bypassed'):
                print("SUCCESS: SMS verification bypassed via API!")
            else:
                print("WARNING: SMS verification not bypassed via API!")
        
        # Test verify code API
        verify_data = {
            'phone_number': admin_user.phone_number,
            'verification_code': '123456'
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/verify-code/',
            json=verify_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Verify code API response status: {response.status_code}")
        print(f"Verify code API response: {response.text}")
        
        if response.status_code == 200:
            verify_response = response.json()
            if verify_response.get('bypassed'):
                print("SUCCESS: Code verification bypassed via API!")
            else:
                print("WARNING: Code verification not bypassed via API!")
        
        # Check user after tests
        print(f"\n" + "=" * 50)
        print("USER STATUS AFTER TESTS")
        print("=" * 50)
        
        admin_user.refresh_from_db()
        print(f"Admin user after tests:")
        print(f"  is_superuser: {admin_user.is_superuser}")
        print(f"  is_staff: {admin_user.is_staff}")
        print(f"  phone_verified: {admin_user.phone_verified}")
        print(f"  phone_number: {admin_user.phone_number}")
        
    except Exception as e:
        print(f"Error debugging SMS bypass detailed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging SMS Bypass Detailed for Superadmin Users")
    print("=" * 80)
    
    debug_sms_bypass_detailed()

if __name__ == "__main__":
    main()
