#!/usr/bin/env python3
"""
Debug Phone Number Formatting
============================

This script debugs the phone number formatting issue.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService

def debug_phone_number():
    """Debug phone number formatting"""
    print("Phone Number Formatting Debug")
    print("=" * 50)
    
    zenopay_service = ZenoPayService()
    
    # Test different phone number formats
    test_phones = [
        "0757347863",  # Original from troubleshooting
        "0614853618",  # From your Postman response
        "0744963858",  # Another format
    ]
    
    print("Testing phone number formatting:")
    for phone in test_phones:
        try:
            formatted = zenopay_service._validate_phone_number(phone)
            print(f"   {phone} → {formatted}")
        except Exception as e:
            print(f"   {phone} → ERROR: {str(e)}")
    
    print("\nTesting ZenoPay with your actual phone number:")
    try:
        # Test with the phone number from your Postman response
        payment_response = zenopay_service.create_payment(
            order_id=f"DEBUG-{phone}-{__import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')}",
            buyer_email="admin@example.com",
            buyer_name="Admin User",
            buyer_phone="0614853618",  # Your actual phone from Postman
            amount=150000,
            webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
            mobile_money_provider="vodacom"
        )
        
        print(f"   Payment Response: {payment_response}")
        
        if payment_response.get('success'):
            print("   SUCCESS: Payment created with your phone number!")
            print("   Check your phone (0614853618) for push notification!")
        else:
            print(f"   FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")

def test_different_providers_with_your_phone():
    """Test different providers with your actual phone number"""
    print("\nTesting different providers with your phone (0614853618):")
    
    zenopay_service = ZenoPayService()
    providers = ["vodacom", "tigo", "airtel", "halotel"]
    
    for provider in providers:
        print(f"\n   Testing {provider.upper()}:")
        try:
            payment_response = zenopay_service.create_payment(
                order_id=f"DEBUG-{provider}-{__import__('datetime').datetime.now().strftime('%Y%m%d%H%M%S')}",
                buyer_email="admin@example.com",
                buyer_name="Admin User",
                buyer_phone="0614853618",  # Your actual phone
                amount=150000,
                webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
                mobile_money_provider=provider
            )
            
            if payment_response.get('success'):
                print(f"     SUCCESS: {provider} payment created")
                print(f"     Check your phone for {provider} notification!")
            else:
                print(f"     FAILED: {provider} - {payment_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"     ERROR: {provider} - {str(e)}")

def main():
    print("Phone Number Debug Tool")
    print("=" * 50)
    print("This will debug the phone number formatting issue")
    print()
    
    debug_phone_number()
    test_different_providers_with_your_phone()
    
    print("\n" + "="*50)
    print("IMPORTANT NOTES:")
    print("="*50)
    print("1. Your phone number in Postman: 0614853618")
    print("2. This is a 06 number (Tigo network)")
    print("3. Make sure you have Tigo Pesa app installed")
    print("4. Check if you're using the correct mobile money provider")
    print("5. Try using 'tigo' as mobile_money_provider instead of 'vodacom'")

if __name__ == '__main__':
    main()
