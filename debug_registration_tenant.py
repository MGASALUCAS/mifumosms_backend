#!/usr/bin/env python3
"""
Debug registration tenant issue
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

def debug_registration_tenant():
    """Debug registration tenant issue."""
    print("=" * 80)
    print("DEBUGGING REGISTRATION TENANT ISSUE")
    print("=" * 80)
    
    try:
        # Get the user
        user = User.objects.filter(email='admin9@mifumo.com').first()
        if not user:
            print("User admin9@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Tenant: {user.get_tenant().name if user.get_tenant() else 'None'}")
        print(f"Tenant ID: {user.get_tenant().id if user.get_tenant() else 'None'}")
        
        # Send a fresh verification code
        print("\n" + "=" * 80)
        print("SENDING FRESH VERIFICATION CODE")
        print("=" * 80)
        
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        result = sms_verification.send_verification_code(user, "account_confirmation")
        print(f"Send result: {result}")
        
        if result.get('success'):
            # Refresh user to get the new code
            user.refresh_from_db()
            verification_code = user.phone_verification_code
            print(f"New verification code: {verification_code}")
            
            # Test verification
            print("\n" + "=" * 80)
            print("TESTING VERIFICATION")
            print("=" * 80)
            
            verification_data = {
                'phone_number': user.phone_number,
                'verification_code': verification_code
            }
            
            print(f"Sending verification data: {verification_data}")
            
            response = requests.post(
                'http://127.0.0.1:8001/api/auth/sms/verify-code/',
                json=verification_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                print("SUCCESS: Verification worked!")
            else:
                print("FAILED: Verification failed")
        else:
            print("FAILED: Could not send verification code")
            print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"Error debugging registration tenant: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging Registration Tenant Issue")
    print("=" * 80)
    
    debug_registration_tenant()

if __name__ == "__main__":
    main()
