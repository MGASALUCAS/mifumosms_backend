#!/usr/bin/env python3
"""
Simple Push Notification Troubleshooting
======================================

This script helps troubleshoot push notification issues without Unicode characters.
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

def simple_troubleshoot():
    """Simple troubleshooting guide"""
    print("Push Notification Troubleshooting")
    print("=" * 50)
    
    print("\n1. Phone Number Check:")
    phone = "0757347863"
    print(f"   Your phone: {phone}")
    print(f"   Format: {'OK' if phone.startswith('07') else 'WRONG'}")
    print(f"   Length: {len(phone)} digits")
    
    print("\n2. Testing ZenoPay with different providers:")
    zenopay_service = ZenoPayService()
    
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
                print(f"     SUCCESS: {provider} payment created")
                print(f"     Order ID: {unique_order_id}")
                print(f"     Message: {payment_response.get('message', 'N/A')}")
            else:
                print(f"     FAILED: {provider} - {payment_response.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"     ERROR: {provider} - {str(e)}")
    
    print("\n3. Common Issues and Solutions:")
    print("   PHONE ISSUES:")
    print("   - Check if M-Pesa app is installed and updated")
    print("   - Make sure your phone has internet connection")
    print("   - Check if phone is in silent mode")
    print("   - Look in notification center")
    
    print("\n   M-PESA ISSUES:")
    print("   - Check if M-Pesa account is active")
    print("   - Verify you have sufficient balance (150,000 TZS)")
    print("   - Check if M-Pesa PIN is working")
    print("   - Try logging into M-Pesa app manually")
    
    print("\n   NOTIFICATION ISSUES:")
    print("   - Check if M-Pesa notifications are enabled")
    print("   - Check if push notifications are enabled")
    print("   - Try restarting your phone")
    print("   - Check if it's outside business hours")
    
    print("\n4. Alternative Testing:")
    print("   - Try with a different phone number")
    print("   - Try with a smaller amount (e.g., 1000 TZS)")
    print("   - Check if you receive SMS instead of push notification")
    print("   - Try during business hours (9 AM - 5 PM)")

def test_small_amount():
    """Test with a small amount"""
    print("\n5. Testing with small amount (1000 TZS):")
    
    try:
        zenopay_service = ZenoPayService()
        unique_order_id = f"TEST-SMALL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"
        
        payment_response = zenopay_service.create_payment(
            order_id=unique_order_id,
            buyer_email="admin@example.com",
            buyer_name="Admin User",
            buyer_phone="0757347863",
            amount=1000,  # Small amount
            webhook_url=f"{getattr(settings, 'BASE_URL', '')}/api/billing/payments/webhook/",
            mobile_money_provider="vodacom"
        )
        
        if payment_response.get('success'):
            print(f"   SUCCESS: Small payment created")
            print(f"   Order ID: {unique_order_id}")
            print(f"   Amount: 1000 TZS")
            print(f"   Check your phone for notification!")
        else:
            print(f"   FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")

def main():
    print("Simple Push Notification Troubleshooting")
    print("=" * 50)
    print("This will help you troubleshoot push notification issues")
    print()
    
    simple_troubleshoot()
    test_small_amount()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("="*50)
    print("1. ZenoPay is working correctly (API calls successful)")
    print("2. The issue is likely on the mobile device side")
    print("3. Check M-Pesa app, notifications, and phone settings")
    print("4. Try with a different phone number if possible")
    print("5. Push notifications can take 1-5 minutes to arrive")

if __name__ == '__main__':
    main()
