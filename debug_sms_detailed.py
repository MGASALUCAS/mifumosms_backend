#!/usr/bin/env python3
"""
Debug SMS sending process in detail.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from accounts.services.sms_verification import SMSVerificationService
from messaging.services.sms_service import SMSService
from messaging.services.beem_sms import BeemSMSService
from django.conf import settings

def debug_sms_process():
    """Debug the SMS sending process step by step."""
    print("Debugging SMS sending process...")
    
    # Get the user
    user = User.objects.filter(phone_number='255614853618').first()
    if not user:
        print("ERROR: User not found!")
        return
    
    print(f"User: {user.email}")
    print(f"Phone: {user.phone_number}")
    print(f"Tenant: {user.get_tenant().name}")
    
    # Check Beem credentials
    print("\n" + "="*50)
    print("CHECKING BEEM CREDENTIALS")
    print("="*50)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    print(f"API Key: {api_key[:10] + '...' if api_key else 'None'}")
    print(f"Secret Key: {secret_key[:10] + '...' if secret_key else 'None'}")
    
    # Test Beem service directly
    print("\n" + "="*50)
    print("TESTING BEEM SERVICE DIRECTLY")
    print("="*50)
    
    try:
        beem_service = BeemSMSService()
        print("Beem service initialized successfully")
        
        # Test with the exact phone number
        result = beem_service.send_sms(
            message="Test message from Mifumo WMS - Password reset test",
            recipients=["255614853618"],
            source_addr="Taarifa-SMS"
        )
        
        print(f"Beem SMS Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: Beem SMS sent successfully!")
        else:
            print(f"ERROR: Beem SMS failed: {result.get('error')}")
            
    except Exception as e:
        print(f"ERROR: Beem service error: {e}")
    
    # Test SMS service
    print("\n" + "="*50)
    print("TESTING SMS SERVICE")
    print("="*50)
    
    try:
        sms_service = SMSService(str(user.get_tenant().id))
        
        result = sms_service.send_sms(
            to="255614853618",
            message="Test message from Mifumo WMS - Password reset test",
            sender_id="Taarifa-SMS",
            recipient_id="test_001"
        )
        
        print(f"SMS Service Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS service sent successfully!")
        else:
            print(f"ERROR: SMS service failed: {result.get('error')}")
            
    except Exception as e:
        print(f"ERROR: SMS service error: {e}")
    
    # Test SMS verification service
    print("\n" + "="*50)
    print("TESTING SMS VERIFICATION SERVICE")
    print("="*50)
    
    try:
        sms_verification = SMSVerificationService(str(user.get_tenant().id))
        
        result = sms_verification.send_verification_sms(
            phone_number="255614853618",
            code="123456",
            message_type="password_reset"
        )
        
        print(f"SMS Verification Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS verification sent successfully!")
        else:
            print(f"ERROR: SMS verification failed: {result.get('error')}")
            
    except Exception as e:
        print(f"ERROR: SMS verification error: {e}")

def check_sms_providers():
    """Check SMS providers configuration."""
    print("\n" + "="*50)
    print("CHECKING SMS PROVIDERS")
    print("="*50)
    
    try:
        from messaging.models import SMSProvider, SMSSenderID
        
        # Get tenant
        user = User.objects.filter(phone_number='255614853618').first()
        tenant = user.get_tenant()
        
        print(f"Tenant: {tenant.name}")
        
        # Check SMS providers
        providers = SMSProvider.objects.filter(tenant=tenant, is_active=True)
        print(f"Active SMS Providers: {providers.count()}")
        
        for provider in providers:
            print(f"  - {provider.name}: {provider.provider_type}")
            print(f"    API Key: {provider.api_key[:10] + '...' if provider.api_key else 'None'}")
            print(f"    Secret: {provider.secret_key[:10] + '...' if provider.secret_key else 'None'}")
        
        # Check sender IDs
        sender_ids = SMSSenderID.objects.filter(tenant=tenant, status='active')
        print(f"Active Sender IDs: {sender_ids.count()}")
        
        for sender in sender_ids:
            print(f"  - {sender.sender_id}: {sender.status}")
            
    except Exception as e:
        print(f"ERROR: Checking providers: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG SMS SENDING PROCESS")
    print("=" * 60)
    
    # Debug SMS process
    debug_sms_process()
    
    # Check SMS providers
    check_sms_providers()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETED")
    print("=" * 60)

