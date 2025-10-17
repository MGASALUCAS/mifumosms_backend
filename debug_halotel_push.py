#!/usr/bin/env python3
"""
Debug Halotel Push Notification
==============================

This script specifically debugs why Halotel push notifications aren't working.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService

def debug_halotel_push():
    """Debug Halotel push notification issues"""
    print("Halotel Push Notification Debug")
    print("=" * 50)
    
    zenopay_service = ZenoPayService()
    
    # Test with different amounts
    test_amounts = [1000, 5000, 10000, 150000]
    
    print("Testing different amounts with Halotel:")
    print("(Some providers have minimum amounts for push notifications)")
    print()
    
    for amount in test_amounts:
        print(f"Testing amount: {amount:,} TZS")
        try:
            payment_response = zenopay_service.create_payment(
                order_id=f"DEBUG-HALOTEL-{amount}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                buyer_email="admin@example.com",
                buyer_name="Admin User",
                buyer_phone="0614853618",  # Your Halotel number
                amount=amount,
                webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
                mobile_money_provider="halotel"
            )
            
            if payment_response.get('success'):
                print(f"   SUCCESS: Payment created for {amount:,} TZS")
                print(f"   Order ID: {payment_response.get('order_id')}")
                print(f"   Message: {payment_response.get('message')}")
                print(f"   Check your phone for Halotel Money notification!")
            else:
                print(f"   FAILED: {payment_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ERROR: {str(e)}")
        
        print()

def check_halotel_app_requirements():
    """Check Halotel app requirements"""
    print("Halotel Money App Requirements:")
    print("=" * 50)
    print("1. Make sure you have Halotel Money app installed")
    print("2. Check if your phone number is registered with Halotel Money")
    print("3. Verify that push notifications are enabled for Halotel Money")
    print("4. Check if you have sufficient balance in your Halotel Money account")
    print("5. Some providers require minimum amounts for push notifications")
    print()

def test_alternative_providers():
    """Test with alternative providers to see if it's Halotel-specific"""
    print("Testing Alternative Providers:")
    print("=" * 50)
    
    zenopay_service = ZenoPayService()
    providers = ["vodacom", "tigo", "airtel"]
    
    for provider in providers:
        print(f"Testing {provider.upper()}:")
        try:
            payment_response = zenopay_service.create_payment(
                order_id=f"DEBUG-{provider.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                buyer_email="admin@example.com",
                buyer_name="Admin User",
                buyer_phone="0614853618",  # Your number
                amount=150000,
                webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
                mobile_money_provider=provider
            )
            
            if payment_response.get('success'):
                print(f"   SUCCESS: {provider} payment created")
                print(f"   Check your phone for {provider} notification!")
            else:
                print(f"   FAILED: {provider} - {payment_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ERROR: {provider} - {str(e)}")
        
        print()

def check_phone_number_registration():
    """Check if phone number is properly registered"""
    print("Phone Number Registration Check:")
    print("=" * 50)
    print("Your phone: 0614853618")
    print("Network: Halotel")
    print()
    print("Common issues:")
    print("1. Phone number not registered with Halotel Money")
    print("2. Halotel Money app not installed")
    print("3. Push notifications disabled")
    print("4. Insufficient balance in Halotel Money account")
    print("5. Halotel Money service temporarily unavailable")
    print()

def main():
    print("Halotel Push Notification Troubleshooting")
    print("=" * 60)
    print("This will help debug why you're not receiving push notifications")
    print()
    
    check_phone_number_registration()
    check_halotel_app_requirements()
    debug_halotel_push()
    test_alternative_providers()
    
    print("=" * 60)
    print("TROUBLESHOOTING STEPS:")
    print("=" * 60)
    print("1. Check if Halotel Money app is installed on your phone")
    print("2. Open Halotel Money app and check your balance")
    print("3. Check if push notifications are enabled for Halotel Money")
    print("4. Try a smaller amount (like 1,000 TZS) to test")
    print("5. Check if your phone number is properly registered")
    print("6. Try calling Halotel customer service to verify your account")
    print()
    print("If none of these work, the issue might be:")
    print("- ZenoPay integration with Halotel")
    print("- Halotel Money service availability")
    print("- Your specific phone number configuration")

if __name__ == '__main__':
    main()
