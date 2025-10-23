#!/usr/bin/env python3
"""
Debug registration flow and SMS verification
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

def debug_registration_flow():
    """Debug registration flow and SMS verification."""
    print("=" * 80)
    print("DEBUGGING REGISTRATION FLOW AND SMS VERIFICATION")
    print("=" * 80)
    
    try:
        # Check if user exists
        user = User.objects.filter(email='admin9@mifumo.com').first()
        if not user:
            print("User admin9@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Phone: {user.phone_number}")
        print(f"Phone Verified: {user.phone_verified}")
        print(f"Verification Code: {user.phone_verification_code}")
        print(f"Code Sent At: {user.phone_verification_sent_at}")
        print(f"Verification Attempts: {user.phone_verification_attempts}")
        print(f"Locked Until: {user.phone_verification_locked_until}")
        
        # Test SMS verification endpoint
        print("\n" + "=" * 80)
        print("TESTING SMS VERIFICATION ENDPOINT")
        print("=" * 80)
        
        # Test with the verification code from the user
        verification_data = {
            'phone_number': user.phone_number,
            'verification_code': user.phone_verification_code
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
            print("SUCCESS: SMS verification worked!")
        else:
            print("FAILED: SMS verification failed")
            
            # Let's check what the exact error is
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error response")
        
        # Test with different phone number formats
        print("\n" + "=" * 80)
        print("TESTING DIFFERENT PHONE NUMBER FORMATS")
        print("=" * 80)
        
        phone_formats = [
            user.phone_number,  # 0614853618
            '+255614853618',    # International format
            '255614853618',     # International without +
        ]
        
        for phone_format in phone_formats:
            print(f"\nTesting with phone format: {phone_format}")
            
            verification_data = {
                'phone_number': phone_format,
                'verification_code': user.phone_verification_code
            }
            
            response = requests.post(
                'http://127.0.0.1:8001/api/auth/sms/verify-code/',
                json=verification_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"  Response status: {response.status_code}")
            print(f"  Response content: {response.text}")
            
            if response.status_code == 200:
                print("  SUCCESS: This format works!")
                break
            else:
                print("  FAILED: This format doesn't work")
        
    except Exception as e:
        print(f"Error debugging registration flow: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run debug."""
    print("Debugging Registration Flow and SMS Verification")
    print("=" * 80)
    
    debug_registration_flow()

if __name__ == "__main__":
    main()
