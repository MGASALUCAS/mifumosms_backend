#!/usr/bin/env python3
"""
Test complete registration flow
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

def test_registration_flow():
    """Test complete registration flow."""
    print("=" * 80)
    print("TESTING COMPLETE REGISTRATION FLOW")
    print("=" * 80)
    
    try:
        # Test user registration
        registration_data = {
            'email': 'test_registration@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPassword123#',
            'password_confirm': 'TestPassword123#',
            'phone_number': '0612345678',
            'timezone': 'UTC'
        }
        
        print("Step 1: User Registration")
        print(f"Sending registration data: {registration_data}")
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/register/',
            json=registration_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response: {response.text}")
        
        if response.status_code == 201:
            print("SUCCESS: User registration worked!")
            
            # Check if user was created
            user = User.objects.filter(email='test_registration@example.com').first()
            if user:
                print(f"User created: {user.email}")
                print(f"Phone: {user.phone_number}")
                print(f"Phone Verified: {user.phone_verified}")
                print(f"Verification Code: {user.phone_verification_code}")
                print(f"Code Sent At: {user.phone_verification_sent_at}")
                
                if user.phone_verification_code:
                    print("SUCCESS: Verification code was set during registration!")
                    
                    # Test SMS verification
                    print("\nStep 2: SMS Verification")
                    verification_data = {
                        'phone_number': user.phone_number,
                        'verification_code': user.phone_verification_code
                    }
                    
                    print(f"Sending verification data: {verification_data}")
                    
                    verify_response = requests.post(
                        'http://127.0.0.1:8001/api/auth/sms/verify-code/',
                        json=verification_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    print(f"Verification response status: {verify_response.status_code}")
                    print(f"Verification response: {verify_response.text}")
                    
                    if verify_response.status_code == 200:
                        print("SUCCESS: SMS verification worked!")
                        print("Complete registration flow is working!")
                    else:
                        print("FAILED: SMS verification failed")
                else:
                    print("FAILED: No verification code was set during registration")
            else:
                print("FAILED: User was not created")
        else:
            print("FAILED: User registration failed")
        
    except Exception as e:
        print(f"Error testing registration flow: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Complete Registration Flow")
    print("=" * 80)
    
    test_registration_flow()

if __name__ == "__main__":
    main()
