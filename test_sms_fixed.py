#!/usr/bin/env python3
"""
Fixed test script for SMS forgot password functionality.
"""
import requests
import json
import time
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from accounts.services.sms_verification import SMSVerificationService
from messaging.services.beem_sms import BeemSMSService
from django.conf import settings

def test_forgot_password_with_correct_phone():
    """Test forgot password with correct phone number format."""
    print("Testing forgot password with correct phone number format...")
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with different phone number formats
    test_phones = [
        "0757347857",  # Local format
        "255757347857",  # International format
        "+255757347857",  # E.164 format
    ]
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    for phone in test_phones:
        print(f"\n--- Testing with phone: {phone} ---")
        
        test_data = {"phone_number": phone}
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=30)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('success'):
                    print("✅ SUCCESS: Password reset code sent!")
                    return True
                else:
                    print(f"❌ API Error: {response_json.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request Error: {e}")
    
    return False

def test_beem_credentials():
    """Test Beem API credentials."""
    print("\n" + "="*60)
    print("TESTING BEEM API CREDENTIALS")
    print("="*60)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    print(f"API Key: {api_key[:10] + '...' if api_key else 'None'}")
    print(f"Secret Key: {secret_key[:10] + '...' if secret_key else 'None'}")
    
    if not api_key or not secret_key:
        print("❌ Beem API credentials not configured!")
        return False
    
    try:
        beem_service = BeemSMSService()
        print("✅ Beem service initialized successfully")
        
        # Test with correct method signature
        result = beem_service.send_sms(
            message="Test message from Mifumo WMS",
            recipients=["255700000001"],
            source_addr="Taarifa-SMS"
        )
        
        print(f"Beem SMS Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Beem SMS service is working!")
            return True
        else:
            print(f"❌ Beem SMS service failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Beem SMS: {e}")
        return False

def test_sms_verification_service():
    """Test SMS verification service with correct phone format."""
    print("\n" + "="*60)
    print("TESTING SMS VERIFICATION SERVICE")
    print("="*60)
    
    try:
        # Get a user with phone number
        user = User.objects.filter(phone_number__isnull=False).exclude(phone_number='').first()
        
        if not user:
            print("❌ No user with phone number found")
            return False
        
        print(f"Testing with user: {user.email} (Phone: {user.phone_number})")
        
        # Test SMS verification service
        sms_service = SMSVerificationService(str(user.get_tenant().id))
        
        print("\n1. Testing send_verification_code...")
        result = sms_service.send_verification_code(user, "password_reset")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ SMS verification service is working!")
            return True
        else:
            print(f"❌ SMS verification service failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SMS service: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_phone_normalization():
    """Check phone number normalization."""
    print("\n" + "="*60)
    print("CHECKING PHONE NUMBER NORMALIZATION")
    print("="*60)
    
    from accounts.views import normalize_phone_number
    
    test_phones = [
        "0757347857",
        "255757347857", 
        "+255757347857",
        "255700000001",
        "+255700000001"
    ]
    
    for phone in test_phones:
        normalized = normalize_phone_number(phone)
        print(f"Original: {phone} -> Normalized: {normalized}")
    
    # Check what users exist with normalized phones
    print("\nUsers in database:")
    users = User.objects.filter(phone_number__isnull=False).exclude(phone_number='')[:5]
    for user in users:
        print(f"  ID: {user.id}, Phone: {user.phone_number}, Email: {user.email}")

if __name__ == "__main__":
    print("=" * 60)
    print("SMS FORGOT PASSWORD COMPREHENSIVE TEST (FIXED)")
    print("=" * 60)
    
    # Check phone normalization first
    check_phone_normalization()
    
    # Test 1: API endpoint with correct phone formats
    test_forgot_password_with_correct_phone()
    
    # Test 2: Beem credentials
    test_beem_credentials()
    
    # Test 3: SMS verification service
    test_sms_verification_service()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

