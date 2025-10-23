#!/usr/bin/env python3
"""
Debug SMS Service
Test SMS service initialization and sending
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.models import SMSProvider, Tenant
from messaging.services.sms_service import SMSService
from accounts.services.sms_verification import SMSVerificationService

def test_sms_service():
    """Test SMS service initialization."""
    print("=" * 80)
    print("TESTING SMS SERVICE")
    print("=" * 80)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenant found!")
        return
    
    print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
    
    # Test SMS service initialization
    try:
        sms_service = SMSService(str(tenant.id))
        print("SMS Service initialized successfully")
        
        # Test getting provider
        provider = sms_service.get_provider()
        print(f"Provider found: {provider.name} ({provider.provider_type})")
        
        # Test sending SMS
        result = sms_service.send_sms(
            to="255700000001",
            message="Test message from debug script",
            sender_id="Taarifa-SMS",
            recipient_id="debug_test"
        )
        
        print(f"SMS send result: {result}")
        
    except Exception as e:
        print(f"SMS Service error: {e}")
        import traceback
        traceback.print_exc()

def test_sms_verification_service():
    """Test SMS verification service."""
    print("\n" + "=" * 80)
    print("TESTING SMS VERIFICATION SERVICE")
    print("=" * 80)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenant found!")
        return
    
    print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
    
    # Test SMS verification service
    try:
        sms_verification = SMSVerificationService(tenant.id)
        print("SMS Verification Service initialized successfully")
        
        # Test sending verification code
        result = sms_verification.send_verification_sms(
            phone_number="+255700000001",
            code="123456",
            message_type="verification"
        )
        
        print(f"SMS verification result: {result}")
        
    except Exception as e:
        print(f"SMS Verification Service error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("Debugging SMS Service")
    print("=" * 80)
    
    test_sms_service()
    test_sms_verification_service()

if __name__ == "__main__":
    main()
