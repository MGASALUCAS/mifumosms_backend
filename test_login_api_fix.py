#!/usr/bin/env python3
"""
Test login API fix for superadmin users
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

def test_login_api_fix():
    """Test login API fix for superadmin users."""
    print("=" * 80)
    print("TESTING LOGIN API FIX FOR SUPERADMIN USERS")
    print("=" * 80)
    
    try:
        # Test login API
        print("Testing login API...")
        
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
            
            # Check if user data includes the required fields
            if 'user' in login_response:
                user_data = login_response['user']
                print(f"\nUser data from login:")
                print(f"  id: {user_data.get('id')}")
                print(f"  email: {user_data.get('email')}")
                print(f"  first_name: {user_data.get('first_name')}")
                print(f"  last_name: {user_data.get('last_name')}")
                print(f"  phone_number: {user_data.get('phone_number')}")
                print(f"  phone_verified: {user_data.get('phone_verified')}")
                print(f"  is_superuser: {user_data.get('is_superuser')}")
                print(f"  is_staff: {user_data.get('is_staff')}")
                print(f"  is_active: {user_data.get('is_active')}")
                
                # Check if frontend should bypass verification
                print(f"\n" + "=" * 50)
                print("FRONTEND VERIFICATION LOGIC")
                print("=" * 50)
                
                should_bypass = (
                    user_data.get('is_superuser') or 
                    user_data.get('is_staff') or 
                    user_data.get('phone_verified')
                )
                
                if should_bypass:
                    print("SUCCESS: User should bypass verification!")
                    print("The frontend should NOT show 'Account Verification Required'")
                    print("The frontend should allow access to the dashboard")
                else:
                    print("WARNING: User should NOT bypass verification!")
                    print("The frontend should show 'Account Verification Required'")
                
                # Show what the frontend should check
                print(f"\nFrontend should check:")
                print(f"  if (user.is_superuser || user.is_staff || user.phone_verified) {{")
                print(f"    // Skip verification, allow dashboard access")
                print(f"  }} else {{")
                print(f"    // Show verification required")
                print(f"  }}")
                
            else:
                print("WARNING: No user data in login response!")
        else:
            print("FAILED: Login failed!")
            print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error testing login API fix: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Login API Fix for Superadmin Users")
    print("=" * 80)
    
    test_login_api_fix()

if __name__ == "__main__":
    main()
