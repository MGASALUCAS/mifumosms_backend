#!/usr/bin/env python3
"""
Simple Phone Number Debug
========================

This script debugs the phone number formatting without Unicode characters.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService

def simple_phone_debug():
    """Simple phone number debug"""
    print("Phone Number Debug")
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
            print(f"   {phone} -> {formatted}")
        except Exception as e:
            print(f"   {phone} -> ERROR: {str(e)}")
    
    print("\nTesting ZenoPay with your actual phone number (0614853618):")
    try:
        payment_response = zenopay_service.create_payment(
            order_id=f"DEBUG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
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

def test_tigo_provider():
    """Test with Tigo provider since your phone starts with 06"""
    print("\nTesting with Tigo provider (since your phone starts with 06):")
    
    zenopay_service = ZenoPayService()
    
    try:
        payment_response = zenopay_service.create_payment(
            order_id=f"DEBUG-TIGO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            buyer_email="admin@example.com",
            buyer_name="Admin User",
            buyer_phone="0614853618",  # Your actual phone
            amount=150000,
            webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
            mobile_money_provider="tigo"  # Use Tigo instead of Vodacom
        )
        
        print(f"   Payment Response: {payment_response}")
        
        if payment_response.get('success'):
            print("   SUCCESS: Tigo payment created!")
            print("   Check your phone for Tigo Pesa notification!")
        else:
            print(f"   FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")

def main():
    print("Simple Phone Number Debug")
    print("=" * 50)
    print("This will debug the phone number formatting issue")
    print()
    
    simple_phone_debug()
    test_tigo_provider()
    
    print("\n" + "="*50)
    print("IMPORTANT DISCOVERY:")
    print("="*50)
    print("Your phone number: 0614853618")
    print("This is a 06 number (Tigo network)")
    print("You should use 'tigo' as mobile_money_provider")
    print("Make sure you have Tigo Pesa app installed")
    print("Check for Tigo Pesa notifications, not M-Pesa")

if __name__ == '__main__':
    main()
