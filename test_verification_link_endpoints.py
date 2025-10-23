#!/usr/bin/env python3
"""
Test verification link endpoints for phone number verification
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

def test_verification_link_endpoints():
    """Test verification link endpoints."""
    print("=" * 80)
    print("TESTING VERIFICATION LINK ENDPOINTS")
    print("=" * 80)
    
    try:
        # Test 1: Send verification link for normal user
        print("=" * 50)
        print("TEST 1: SEND VERIFICATION LINK FOR NORMAL USER")
        print("=" * 50)
        
        # Create a test user (not superadmin)
        test_phone = "0689726061"  # Different from admin phone
        test_user, created = User.objects.get_or_create(
            email='testuser@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'phone_number': test_phone,
                'is_superuser': False,
                'is_staff': False,
                'is_verified': False,
                'phone_verified': False
            }
        )
        
        if created:
            print(f"Created test user: {test_user.email}")
        else:
            print(f"Using existing test user: {test_user.email}")
        
        # Test send verification link
        link_data = {
            'phone_number': test_phone
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/send-verification-link/',
            json=link_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Send verification link response status: {response.status_code}")
        print(f"Send verification link response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            link_response = response.json()
            if link_response.get('bypassed'):
                print("SUCCESS: Verification bypassed for admin user!")
            else:
                print("SUCCESS: Verification link sent for normal user!")
                verification_link = link_response.get('verification_link')
                print(f"Verification link: {verification_link}")
        else:
            print("FAILED: Send verification link failed!")
        
        # Test 2: Send verification link for superadmin user
        print(f"\n" + "=" * 50)
        print("TEST 2: SEND VERIFICATION LINK FOR SUPERADMIN USER")
        print("=" * 50)
        
        admin_phone = "0689726060"  # Admin phone
        admin_link_data = {
            'phone_number': admin_phone
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/send-verification-link/',
            json=admin_link_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Send verification link for admin response status: {response.status_code}")
        print(f"Send verification link for admin response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            admin_link_response = response.json()
            if admin_link_response.get('bypassed'):
                print("SUCCESS: Verification bypassed for superadmin user!")
            else:
                print("WARNING: Verification link sent for superadmin user!")
        else:
            print("FAILED: Send verification link for admin failed!")
        
        # Test 3: Verify account link (if we have a valid token)
        print(f"\n" + "=" * 50)
        print("TEST 3: VERIFY ACCOUNT LINK")
        print("=" * 50)
        
        # Get the test user's verification token
        test_user.refresh_from_db()
        if test_user.verification_token:
            verify_data = {
                'token': test_user.verification_token,
                'phone_number': test_phone
            }
            
            response = requests.post(
                'http://127.0.0.1:8001/api/auth/sms/verify-account-link/',
                json=verify_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Verify account link response status: {response.status_code}")
            print(f"Verify account link response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                verify_response = response.json()
                print("SUCCESS: Account verified successfully!")
                print(f"User verified: {verify_response.get('user', {}).get('is_verified')}")
                print(f"Phone verified: {verify_response.get('user', {}).get('phone_verified')}")
            else:
                print("FAILED: Account verification failed!")
        else:
            print("No verification token found for test user")
        
        # Test 4: Resend verification link
        print(f"\n" + "=" * 50)
        print("TEST 4: RESEND VERIFICATION LINK")
        print("=" * 50)
        
        resend_data = {
            'phone_number': test_phone
        }
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/resend-verification-link/',
            json=resend_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Resend verification link response status: {response.status_code}")
        print(f"Resend verification link response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            resend_response = response.json()
            if resend_response.get('bypassed'):
                print("SUCCESS: Verification bypassed for admin user!")
            elif resend_response.get('message') == 'Account is already verified':
                print("SUCCESS: Account is already verified!")
            else:
                print("SUCCESS: New verification link sent!")
        else:
            print("FAILED: Resend verification link failed!")
        
        # Summary
        print(f"\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        print("New verification link endpoints:")
        print("1. POST /api/auth/sms/send-verification-link/ - Send verification link via SMS")
        print("2. POST /api/auth/sms/verify-account-link/ - Verify account using link")
        print("3. POST /api/auth/sms/resend-verification-link/ - Resend verification link")
        
        print(f"\nFeatures:")
        print("- Sends verification link via SMS instead of just code")
        print("- Link expires in 1 hour")
        print("- Bypasses verification for superadmin/staff users")
        print("- Handles already verified users")
        print("- Returns verification link in response for testing")
        
        print(f"\nFrontend integration:")
        print("- Show 'Get verification link' button for users who see verification message")
        print("- User enters phone number")
        print("- System sends SMS with clickable link")
        print("- User clicks link to verify account")
        print("- Redirect to dashboard after verification")
        
    except Exception as e:
        print(f"Error testing verification link endpoints: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Verification Link Endpoints")
    print("=" * 80)
    
    test_verification_link_endpoints()

if __name__ == "__main__":
    main()
