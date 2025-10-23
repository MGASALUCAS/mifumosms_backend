#!/usr/bin/env python3
"""
Test the working messaging system approach for SMS verification
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.sms_service import SMSService
from messaging.models_sms import SMSProvider, SMSSenderID
from tenants.models import Tenant

def test_working_messaging_approach():
    """Test using the working messaging system approach."""
    print("=" * 80)
    print("TESTING WORKING MESSAGING SYSTEM APPROACH")
    print("=" * 80)
    
    try:
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found!")
            return
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test using SMSService (the working approach)
        sms_service = SMSService(str(tenant.id))
        print("SMSService initialized successfully")
        
        # Test sending SMS to the specific phone number
        phone_number = "255614853618"  # Tanzanian number format (without +)
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Using sender ID: Taarifa-SMS")
        
        result = sms_service.send_sms(
            to=phone_number,
            message="Test message from working messaging system to 0614853618",
            sender_id="Taarifa-SMS",
            recipient_id="test_working_0614853618"
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS sent to 0614853618 using working messaging system!")
        else:
            print("FAILED: SMS not sent to 0614853618")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Response: {result.get('response', {})}")
            
    except Exception as e:
        print(f"SMSService error: {e}")
        import traceback
        traceback.print_exc()

def test_direct_beem_sms_service():
    """Test using the direct BeemSMSService from sms_service.py."""
    print("\n" + "=" * 80)
    print("TESTING DIRECT BEEMSMS SERVICE FROM SMS_SERVICE.PY")
    print("=" * 80)
    
    try:
        # Get first tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("No tenant found!")
            return
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Get or create SMS provider
        provider = SMSProvider.objects.filter(
            tenant=tenant,
            is_active=True,
            is_default=True
        ).first()
        
        if not provider:
            provider = SMSProvider.objects.filter(
                tenant=tenant,
                is_active=True
            ).first()
        
        if not provider:
            print("No active SMS provider found!")
            return
        
        print(f"Using provider: {provider.name} (ID: {provider.id})")
        
        # Test using direct BeemSMSService from sms_service.py
        from messaging.services.sms_service import BeemSMSService
        
        beem_service = BeemSMSService(provider)
        print("BeemSMSService from sms_service.py initialized successfully")
        
        # Test sending SMS to the specific phone number
        phone_number = "255614853618"  # Tanzanian number format (without +)
        
        print(f"Sending SMS to: {phone_number}")
        print(f"Using sender ID: Taarifa-SMS")
        
        result = beem_service.send_sms(
            to=phone_number,
            message="Test message from direct BeemSMSService to 0614853618",
            sender_id="Taarifa-SMS",
            recipient_id="test_direct_0614853618"
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("SUCCESS: SMS sent to 0614853618 using direct BeemSMSService!")
        else:
            print("FAILED: SMS not sent to 0614853618")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Response: {result.get('response', {})}")
            
    except Exception as e:
        print(f"Direct BeemSMSService error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("Testing Working Messaging System Approach")
    print("=" * 80)
    
    test_working_messaging_approach()
    test_direct_beem_sms_service()

if __name__ == "__main__":
    main()
