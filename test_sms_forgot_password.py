#!/usr/bin/env python3
"""
Test script to check SMS forgot password functionality.
"""
import requests
import json
import time

def test_forgot_password_with_valid_phone():
    """Test forgot password with a valid phone number."""
    print("Testing forgot password with valid phone number...")
    
    url = "http://127.0.0.1:8001/api/auth/sms/forgot-password/"
    
    # Test with a valid phone number from the database
    test_data = {
        "phone_number": "255700000001"  # User ID 82
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Making POST request to: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                
                # Check if SMS was actually sent
                if response_json.get('success'):
                    print("\n✅ SUCCESS: Password reset code sent!")
                    if response_json.get('bypassed'):
                        print("ℹ️  SMS was bypassed (likely for admin user)")
                    else:
                        print("📱 SMS should have been sent to the phone number")
                else:
                    print(f"❌ FAILED: {response_json.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Error parsing JSON: {e}")
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_sms_verification_service():
    """Test SMS verification service directly."""
    print("\n" + "="*60)
    print("TESTING SMS VERIFICATION SERVICE DIRECTLY")
    print("="*60)
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
        django.setup()
        
        from accounts.models import User
        from accounts.services.sms_verification import SMSVerificationService
        
        # Get a user with phone number
        user = User.objects.filter(phone_number__isnull=False).exclude(phone_number='').first()
        
        if not user:
            print("❌ No user with phone number found")
            return
        
        print(f"Testing with user: {user.email} (Phone: {user.phone_number})")
        
        # Test SMS verification service
        sms_service = SMSVerificationService(str(user.get_tenant().id))
        
        print("\n1. Testing send_verification_code...")
        result = sms_service.send_verification_code(user, "password_reset")
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ SMS verification service is working!")
        else:
            print(f"❌ SMS verification service failed: {result.get('error')}")
            
    except Exception as e:
        print(f"Error testing SMS service: {e}")
        import traceback
        traceback.print_exc()

def test_beem_sms_directly():
    """Test Beem SMS service directly."""
    print("\n" + "="*60)
    print("TESTING BEEM SMS SERVICE DIRECTLY")
    print("="*60)
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
        django.setup()
        
        from messaging.services.beem_sms import BeemSMSService
        
        # Test Beem SMS service
        beem_service = BeemSMSService()
        
        print("Testing Beem SMS service...")
        result = beem_service.send_sms(
            to="255700000001",
            message="Test message from Mifumo WMS - Password reset test",
            sender_id="Taarifa-SMS"
        )
        
        print(f"Beem SMS Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Beem SMS service is working!")
        else:
            print(f"❌ Beem SMS service failed: {result.get('error')}")
            
    except Exception as e:
        print(f"Error testing Beem SMS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("SMS FORGOT PASSWORD COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: API endpoint with valid phone
    test_forgot_password_with_valid_phone()
    
    # Test 2: SMS verification service directly
    test_sms_verification_service()
    
    # Test 3: Beem SMS service directly
    test_beem_sms_directly()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)

