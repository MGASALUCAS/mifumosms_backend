#!/usr/bin/env python3
"""
Send a real SMS to phone number 0757347857
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.services.sms_verification import SMSVerificationService
from tenants.models import Tenant

def send_real_sms():
    """Send a real SMS to 0757347857."""
    print("=" * 80)
    print("SENDING REAL SMS TO 0757347857")
    print("=" * 80)
    
    try:
        # Use the working tenant
        tenant_id = "18da454d-57d5-4c0f-b09c-e74b3cd1a71a"
        tenant = Tenant.objects.get(id=tenant_id)
        
        print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(tenant_id)
        print(f"SMS Verification Service initialized with sender ID: {sms_verification.sender_id}")
        
        # Send a real verification code
        phone_number = "+255757347857"
        code = "123456"  # Test code
        
        print(f"Sending REAL SMS to: {phone_number}")
        print(f"Sender ID: {sms_verification.sender_id}")
        print(f"Message type: account_confirmation")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=code,
            message_type="account_confirmation"
        )
        
        print(f"SMS result: {result}")
        
        if result.get('success'):
            print("✅ SUCCESS: Real SMS sent to 0757347857!")
            print("\n📱 Check your phone! You should receive an SMS with:")
            print("   'Your Mifumo WMS account confirmation code is: 123456. This code expires in 10 minutes. Do not share this code with anyone.'")
            print(f"\n📞 Phone number: {phone_number}")
            print(f"📤 Sender ID: {sms_verification.sender_id}")
            return True
        else:
            print("❌ FAILED: SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ SMS sending error: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_welcome_sms():
    """Send a welcome SMS to 0757347857."""
    print("\n" + "=" * 80)
    print("SENDING WELCOME SMS TO 0757347857")
    print("=" * 80)
    
    try:
        # Use the working tenant
        tenant_id = "18da454d-57d5-4c0f-b09c-e74b3cd1a71a"
        tenant = Tenant.objects.get(id=tenant_id)
        
        # Test SMS verification service
        sms_verification = SMSVerificationService(tenant_id)
        
        # Send a welcome message
        phone_number = "+255757347857"
        welcome_code = "WELCOME"
        
        print(f"Sending WELCOME SMS to: {phone_number}")
        print(f"Sender ID: {sms_verification.sender_id}")
        
        result = sms_verification.send_verification_sms(
            phone_number=phone_number,
            code=welcome_code,
            message_type="verification"
        )
        
        print(f"Welcome SMS result: {result}")
        
        if result.get('success'):
            print("✅ SUCCESS: Welcome SMS sent to 0757347857!")
            print("\n📱 Check your phone! You should receive a welcome SMS!")
            return True
        else:
            print("❌ FAILED: Welcome SMS not sent")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Welcome SMS error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Send real SMS messages."""
    print("Sending REAL SMS messages to 0757347857")
    print("=" * 80)
    
    # Send account confirmation SMS
    print("\n1. Sending Account Confirmation SMS...")
    success1 = send_real_sms()
    
    # Send welcome SMS
    print("\n2. Sending Welcome SMS...")
    success2 = send_welcome_sms()
    
    # Summary
    print("\n" + "=" * 80)
    print("SMS SENDING SUMMARY")
    print("=" * 80)
    
    if success1:
        print("✅ Account Confirmation SMS: SENT")
    else:
        print("❌ Account Confirmation SMS: FAILED")
    
    if success2:
        print("✅ Welcome SMS: SENT")
    else:
        print("❌ Welcome SMS: FAILED")
    
    if success1 or success2:
        print("\n🎉 SMS MESSAGES SENT!")
        print("📱 Check your phone number 0757347857 for the messages!")
        print("📤 Messages are sent from 'Taarifa-SMS' sender ID")
    else:
        print("\n⚠️  No SMS messages were sent. Check the configuration.")

if __name__ == "__main__":
    main()




