"""
Test Direct SMS Service Call
This will directly call the SMS service to send a real SMS
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.sms_service import SMSService
from messaging.models_sms import SMSProvider
from django.conf import settings

def test_direct_sms():
    """Test sending SMS directly through the SMS service"""
    
    print("=" * 60)
    print("  DIRECT SMS SERVICE TEST")
    print("=" * 60)
    print(f"Test Time: {django.utils.timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Phone: +255757347863")
    print()
    
    # Get the first active SMS provider
    try:
        provider = SMSProvider.objects.filter(is_active=True, provider_type='beem').first()
        if not provider:
            print("X No active Beem SMS provider found!")
            return
        
        print(f"Using SMS Provider: {provider.name}")
        print(f"API Key: {provider.api_key[:10]}...")
        print(f"API URL: {provider.api_url}")
        print()
        
        # Create SMS service instance
        sms_service = SMSService(provider)
        
        # Test SMS data
        message = "DIRECT TEST: This is a direct SMS test from Mifumo SMS service to +255757347863. If you receive this, the SMS service is working correctly!"
        recipients = ["+255757347863"]
        sender_id = "MIFUMO"
        
        print(f"Sending SMS to: {recipients[0]}")
        print(f"Message: {message[:80]}...")
        print(f"Sender ID: {sender_id}")
        print()
        
        # Send SMS
        print("Sending SMS...")
        result = sms_service.send_sms(
            to=recipients[0],
            message=message,
            sender_id=sender_id
        )
        
        print(f"SMS Result: {result}")
        
        if result.get('success'):
            print("OK SMS sent successfully!")
            print(f"Message ID: {result.get('message_id', 'N/A')}")
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Cost: {result.get('cost', 'N/A')}")
            
            # Check balance
            print()
            print("Checking account balance...")
            balance_result = sms_service.check_balance()
            print(f"Balance Result: {balance_result}")
            
        else:
            print("X SMS sending failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            print(f"Details: {result.get('details', 'No details available')}")
    
    except Exception as e:
        print(f"X Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("  DIRECT SMS TEST SUMMARY")
    print("=" * 60)
    print("Test completed!")
    print("Check your phone (+255757347863) for the SMS message.")
    print("If you received it, the SMS service is working correctly!")
    print("If not, there might be an issue with the Beem Africa API credentials.")

if __name__ == "__main__":
    test_direct_sms()

