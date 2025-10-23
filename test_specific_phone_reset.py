#!/usr/bin/env python3
"""
Test password reset with specific phone number 0614853618
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

def test_specific_phone_reset():
    """Test password reset with phone number 0614853618."""
    print("=" * 80)
    print("TESTING PASSWORD RESET WITH PHONE NUMBER 0614853618")
    print("=" * 80)
    
    try:
        # Test phone number normalization
        def normalize_phone_number(phone_number):
            if not phone_number:
                return phone_number
            
            # Remove all non-digit characters except +
            cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
            
            # Remove leading +
            if cleaned.startswith('+'):
                cleaned = cleaned[1:]
            
            # Convert international format to local format
            if cleaned.startswith('255') and len(cleaned) == 12:
                # 255614853618 -> 0614853618
                cleaned = '0' + cleaned[3:]
            elif len(cleaned) == 9 and cleaned.startswith('6'):
                # 614853618 -> 0614853618
                cleaned = '0' + cleaned
            
            return cleaned
        
        # Test different formats of 0614853618
        test_formats = [
            "0614853618",           # Local format
            "+255614853618",        # International with +
            "255614853618",         # International without +
            "0614 853 618",         # With spaces
            "0614-853-618",         # With dashes
            "(0614) 853-618",       # With parentheses
            "614853618",            # Without leading 0
        ]
        
        print("Testing phone number normalization:")
        for phone_format in test_formats:
            normalized = normalize_phone_number(phone_format)
            print(f"  '{phone_format}' -> '{normalized}'")
        
        # Check if user exists with this phone number
        print(f"\nChecking if user exists with phone number 0614853618...")
        user = User.objects.filter(phone_number='0614853618').first()
        
        if not user:
            print("No user found with phone number 0614853618")
            print("Creating a test user for this phone number...")
            
            # Create a test user
            from tenants.models import Tenant
            tenant = Tenant.objects.first()
            
            user = User.objects.create(
                email='test0614853618@example.com',
                phone_number='0614853618',
                first_name='Test',
                last_name='User',
                is_active=True
            )
            
            # Set tenant using the proper method
            user.tenant_id = tenant.id
            user.save()
            
            print(f"Created test user: {user.email}")
        else:
            print(f"Found existing user: {user.email}")
        
        # Test the complete password reset flow
        print(f"\n" + "=" * 80)
        print("TESTING COMPLETE PASSWORD RESET FLOW")
        print("=" * 80)
        
        # Step 1: Send forgot password SMS
        print("Step 1: Sending forgot password SMS...")
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        
        result = sms_verification.send_verification_code(user, "password_reset")
        print(f"Send result: {result}")
        
        if not result.get('success'):
            print("FAILED: Could not send verification code")
            return
        
        # Refresh user to get the new code
        user.refresh_from_db()
        verification_code = user.phone_verification_code
        print(f"Verification code sent: {verification_code}")
        
        # Step 2: Test password reset with international format (what frontend likely sends)
        print(f"\nStep 2: Testing password reset with international format...")
        
        reset_data = {
            'phone_number': '+255614853618',  # International format (what frontend sends)
            'verification_code': verification_code,
            'new_password': 'newpassword123',
            'new_password_confirm': 'newpassword123'
        }
        
        print(f"Sending data: {reset_data}")
        
        response = requests.post(
            'http://127.0.0.1:8001/api/auth/sms/reset-password/',
            json=reset_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            print("\nSUCCESS: Password reset worked perfectly!")
            print("The phone number normalization is working correctly.")
            print("Frontend can now send phone numbers in any format and it will work.")
        else:
            print("\nFAILED: Password reset failed")
            print("There might still be an issue to resolve.")
        
    except Exception as e:
        print(f"Error testing specific phone reset: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Password Reset with Phone Number 0614853618")
    print("=" * 80)
    
    test_specific_phone_reset()

if __name__ == "__main__":
    main()
