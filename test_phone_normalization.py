#!/usr/bin/env python3
"""
Test phone number normalization
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

def normalize_phone_number(phone_number):
    """Normalize phone number to local format for database lookup."""
    if not phone_number:
        return phone_number
    
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # Remove leading +
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Convert international format to local format
    if cleaned.startswith('255') and len(cleaned) == 12:
        # 255689726060 -> 0689726060
        cleaned = '0' + cleaned[3:]
    elif len(cleaned) == 9 and cleaned.startswith('6'):
        # 689726060 -> 0689726060
        cleaned = '0' + cleaned
    
    return cleaned

def test_phone_normalization():
    """Test phone number normalization."""
    print("=" * 80)
    print("TESTING PHONE NUMBER NORMALIZATION")
    print("=" * 80)
    
    # Test different phone number formats
    phone_formats = [
        "0689726060",           # Local format
        "+255689726060",        # International with +
        "255689726060",         # International without +
        "0689 726 060",         # With spaces
        "0689-726-060",         # With dashes
        "(0689) 726-060",       # With parentheses
        "689726060",            # Without leading 0
    ]
    
    for phone_format in phone_formats:
        normalized = normalize_phone_number(phone_format)
        print(f"'{phone_format}' -> '{normalized}'")
    
    print("\n" + "=" * 80)
    print("TESTING PASSWORD RESET WITH NORMALIZATION")
    print("=" * 80)
    
    try:
        # Get the user
        user = User.objects.filter(email='admin@mifumo.com').first()
        if not user:
            print("User admin@mifumo.com not found!")
            return
        
        print(f"User: {user.email}")
        print(f"Stored phone: {user.phone_number}")
        
        # Send a fresh verification code
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        result = sms_verification.send_verification_code(user, "password_reset")
        
        if not result.get('success'):
            print("FAILED: Could not send verification code")
            return
        
        user.refresh_from_db()
        verification_code = user.phone_verification_code
        print(f"Verification code: {verification_code}")
        
        # Test with international format (most likely what frontend sends)
        print("\n" + "=" * 50)
        print("TESTING WITH INTERNATIONAL FORMAT (+255689726060)")
        print("=" * 50)
        
        reset_data = {
            'phone_number': '+255689726060',  # International format
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
            print("SUCCESS: Password reset worked with international format!")
        else:
            print("FAILED: Password reset failed with international format")
        
    except Exception as e:
        print(f"Error testing phone normalization: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run test."""
    print("Testing Phone Number Normalization")
    print("=" * 80)
    
    test_phone_normalization()

if __name__ == "__main__":
    main()
