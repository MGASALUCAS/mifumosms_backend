#!/usr/bin/env python3
"""
Test frontend verification logic for superadmin users
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

def test_frontend_verification_logic():
    """Test what the frontend receives for verification logic."""
    print("=" * 80)
    print("TESTING FRONTEND VERIFICATION LOGIC FOR SUPERADMIN USERS")
    print("=" * 80)
    
    try:
        # Test login API
        print("Testing login API response...")
        
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
        
        if response.status_code == 200:
            login_response = response.json()
            print("SUCCESS: Login successful!")
            
            # Extract user data
            user_data = login_response.get('user', {})
            
            print(f"\n" + "=" * 50)
            print("USER DATA RECEIVED BY FRONTEND")
            print("=" * 50)
            
            print(f"User ID: {user_data.get('id')}")
            print(f"Email: {user_data.get('email')}")
            print(f"First Name: {user_data.get('first_name')}")
            print(f"Last Name: {user_data.get('last_name')}")
            print(f"Phone Number: {user_data.get('phone_number')}")
            print(f"Phone Verified: {user_data.get('phone_verified')}")
            print(f"Is Superuser: {user_data.get('is_superuser')}")
            print(f"Is Staff: {user_data.get('is_staff')}")
            print(f"Is Active: {user_data.get('is_active')}")
            print(f"Is Verified: {user_data.get('is_verified')}")
            
            print(f"\n" + "=" * 50)
            print("FRONTEND VERIFICATION LOGIC CHECK")
            print("=" * 50)
            
            # Check what the frontend should do
            is_superuser = user_data.get('is_superuser', False)
            is_staff = user_data.get('is_staff', False)
            phone_verified = user_data.get('phone_verified', False)
            is_verified = user_data.get('is_verified', False)
            
            print(f"Frontend should check these conditions:")
            print(f"1. is_superuser: {is_superuser}")
            print(f"2. is_staff: {is_staff}")
            print(f"3. phone_verified: {phone_verified}")
            print(f"4. is_verified: {is_verified}")
            
            # Frontend logic simulation
            should_bypass_verification = (
                is_superuser or 
                is_staff or 
                phone_verified
            )
            
            print(f"\nFrontend logic result:")
            print(f"should_bypass_verification = is_superuser || is_staff || phone_verified")
            print(f"should_bypass_verification = {is_superuser} || {is_staff} || {phone_verified}")
            print(f"should_bypass_verification = {should_bypass_verification}")
            
            if should_bypass_verification:
                print(f"\nSUCCESS: Frontend should SKIP verification!")
                print(f"Frontend should NOT show 'Account Verification Required'")
                print(f"Frontend should allow access to dashboard")
            else:
                print(f"\nWARNING: Frontend should NOT skip verification!")
                print(f"Frontend should show 'Account Verification Required'")
            
            print(f"\n" + "=" * 50)
            print("FRONTEND CODE EXAMPLE")
            print("=" * 50)
            
            print(f"Frontend should implement this logic:")
            print(f"")
            print(f"// After login, check user data")
            print(f"const user = loginResponse.user;")
            print(f"")
            print(f"// Check if user should bypass verification")
            print(f"const shouldBypassVerification = (")
            print(f"  user.is_superuser ||")
            print(f"  user.is_staff ||")
            print(f"  user.phone_verified")
            print(f");")
            print(f"")
            print(f"if (shouldBypassVerification) {{")
            print(f"  // Skip verification, allow dashboard access")
            print(f"  // Don't show 'Account Verification Required'")
            print(f"  // Redirect to dashboard")
            print(f"}} else {{")
            print(f"  // Show verification required")
            print(f"  // Show 'Account Verification Required'")
            print(f"  // Show phone verification form")
            print(f"}}")
            
            print(f"\n" + "=" * 50)
            print("DEBUGGING INFO")
            print("=" * 50)
            
            print(f"If frontend still shows verification error, check:")
            print(f"1. Frontend is checking the correct fields")
            print(f"2. Frontend is using the updated login response")
            print(f"3. Frontend cache is cleared")
            print(f"4. Frontend is using the latest API response")
            
            # Test SMS verification endpoints
            print(f"\n" + "=" * 50)
            print("SMS VERIFICATION ENDPOINTS TEST")
            print("=" * 50)
            
            # Test send verification code
            sms_data = {
                'phone_number': user_data.get('phone_number'),
                'message_type': 'verification'
            }
            
            sms_response = requests.post(
                'http://127.0.0.1:8001/api/auth/sms/send-code/',
                json=sms_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Send SMS code response status: {sms_response.status_code}")
            if sms_response.status_code == 200:
                sms_data = sms_response.json()
                print(f"Send SMS code response: {json.dumps(sms_data, indent=2)}")
                
                if sms_data.get('bypassed'):
                    print(f"SUCCESS: SMS verification is bypassed for superadmin!")
                else:
                    print(f"WARNING: SMS verification is not bypassed!")
            
        else:
            print("FAILED: Login failed!")
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error testing frontend verification logic: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Frontend Verification Logic for Superadmin Users")
    print("=" * 80)
    
    test_frontend_verification_logic()

if __name__ == "__main__":
    main()
