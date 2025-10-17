#!/usr/bin/env python3
"""
Troubleshoot Push Notification Issues
===================================

This script helps troubleshoot why push notifications might not be received.
"""

import os
import sys
import django
import uuid
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService
from django.conf import settings

def troubleshoot_push_notification():
    """Troubleshoot push notification issues"""
    print("Push Notification Troubleshooting Guide")
    print("=" * 60)
    
    # Check phone number format
    print("\n1. Phone Number Analysis:")
    phone = "0757347863"
    print(f"   Your phone: {phone}")
    print(f"   Format check: {'✓' if phone.startswith('07') else '✗'}")
    print(f"   Length: {len(phone)} digits")
    
    # Test different phone number formats
    print("\n2. Testing different phone number formats:")
    test_phones = [
        "0757347863",  # Original
        "255757347863",  # With country code
        "757347863",  # Without leading zero
    ]
    
    zenopay_service = ZenoPayService()
    for test_phone in test_phones:
        try:
            formatted = zenopay_service._validate_phone_number(test_phone)
            print(f"   {test_phone} → {formatted}")
        except Exception as e:
            print(f"   {test_phone} → ERROR: {str(e)}")
    
    # Test with different mobile money providers
    print("\n3. Testing different mobile money providers:")
    providers = ["vodacom", "tigo", "airtel", "halotel"]
    
    for provider in providers:
        print(f"\n   Testing {provider.upper()}:")
        try:
            unique_order_id = f"TEST-{provider}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
            
            payment_response = zenopay_service.create_payment(
                order_id=unique_order_id,
                buyer_email="admin@example.com",
                buyer_name="Admin User",
                buyer_phone="0757347863",
                amount=150000,
                webhook_url=f"{getattr(settings, 'BASE_URL', '')}/api/billing/payments/webhook/",
                mobile_money_provider=provider
            )
            
            if payment_response.get('success'):
                print(f"     ✓ SUCCESS: {provider} payment created")
                print(f"     Order ID: {unique_order_id}")
                print(f"     Message: {payment_response.get('message', 'N/A')}")
            else:
                print(f"     ✗ FAILED: {provider} - {payment_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"     ✗ ERROR: {provider} - {str(e)}")
    
    # Troubleshooting tips
    print("\n4. Troubleshooting Tips:")
    print("   📱 PHONE SETUP:")
    print("   - Make sure your phone number is correct: 0757347863")
    print("   - Check if you have M-Pesa app installed and updated")
    print("   - Ensure your phone has internet connection (WiFi or mobile data)")
    print("   - Check if your phone is in silent mode or Do Not Disturb")
    print("   - Look in your notification center/panel")
    
    print("\n   💳 M-PESA SETUP:")
    print("   - Make sure your M-Pesa account is active")
    print("   - Check if you have sufficient balance (150,000 TZS)")
    print("   - Verify your M-Pesa PIN is working")
    print("   - Check if you have any M-Pesa restrictions or limits")
    print("   - Try logging into M-Pesa app manually")
    
    print("\n   🔔 NOTIFICATION SETTINGS:")
    print("   - Check if M-Pesa notifications are enabled")
    print("   - Check if push notifications are enabled for M-Pesa")
    print("   - Check if your phone blocks unknown numbers")
    print("   - Try restarting your phone")
    
    print("\n   🌐 NETWORK ISSUES:")
    print("   - Check your internet connection")
    print("   - Try switching between WiFi and mobile data")
    print("   - Check if your network blocks certain services")
    
    print("\n   ⏰ TIMING:")
    print("   - Push notifications can take 1-5 minutes to arrive")
    print("   - Try again if you don't receive it immediately")
    print("   - Check if it's outside business hours")
    
    # Alternative testing methods
    print("\n5. Alternative Testing Methods:")
    print("   - Try with a different phone number")
    print("   - Try with a different mobile money provider")
    print("   - Test with a smaller amount first")
    print("   - Check ZenoPay dashboard for payment status")
    
    return True

def test_with_different_phone():
    """Test with a different phone number"""
    print("\n6. Testing with different phone number:")
    print("   Enter a different phone number to test:")
    print("   (Format: 07XXXXXXXX or 06XXXXXXXX)")
    
    # You can modify this to test with a different number
    test_phone = "0744963858"  # Change this to a different number
    print(f"   Testing with: {test_phone}")
    
    try:
        zenopay_service = ZenoPayService()
        unique_order_id = f"TEST-PHONE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
        
        payment_response = zenopay_service.create_payment(
            order_id=unique_order_id,
            buyer_email="admin@example.com",
            buyer_name="Admin User",
            buyer_phone=test_phone,
            amount=150000,
            webhook_url=f"{getattr(settings, 'BASE_URL', '')}/api/billing/payments/webhook/",
            mobile_money_provider="vodacom"
        )
        
        if payment_response.get('success'):
            print(f"   ✓ SUCCESS: Payment created for {test_phone}")
            print(f"   Check this phone for push notification!")
        else:
            print(f"   ✗ FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ ERROR: {str(e)}")

def main():
    print("Push Notification Troubleshooting")
    print("=" * 60)
    print("This will help you troubleshoot why you're not receiving push notifications")
    print()
    
    troubleshoot_push_notification()
    test_with_different_phone()
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Check your phone for notifications (may take 1-5 minutes)")
    print("2. Try with a different phone number")
    print("3. Check M-Pesa app settings")
    print("4. Verify your M-Pesa account is active")
    print("5. Try a different mobile money provider")
    print("6. Check your internet connection")
    print("7. Restart your phone if needed")

if __name__ == '__main__':
    main()
