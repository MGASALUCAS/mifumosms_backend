#!/usr/bin/env python3
"""
Simple Push Test
===============

This script creates a payment and helps you check for notifications.
"""

import os
import sys
import django
from datetime import datetime
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService

def test_push_notification():
    """Test push notification with simple output"""
    print("Push Notification Test")
    print("=" * 50)
    
    zenopay_service = ZenoPayService()
    
    # Test with a small amount
    test_amount = 1000  # 1,000 TZS
    order_id = f"PUSH-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print(f"Creating payment for {test_amount:,} TZS...")
    print(f"Order ID: {order_id}")
    print(f"Phone: 0614853618 (Halotel)")
    print()
    
    try:
        payment_response = zenopay_service.create_payment(
            order_id=order_id,
            buyer_email="admin@example.com",
            buyer_name="Admin User",
            buyer_phone="0614853618",
            amount=test_amount,
            webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
            mobile_money_provider="halotel"
        )
        
        if payment_response.get('success'):
            print("SUCCESS: Payment created!")
            print(f"Order ID: {payment_response.get('order_id')}")
            print(f"Message: {payment_response.get('message')}")
            print()
            print("NOW CHECK YOUR PHONE:")
            print("1. Look for push notification from Halotel Money")
            print("2. Check if Halotel Money app shows payment request")
            print("3. Look for SMS from Halotel")
            print("4. Check notification history")
            print()
            print("Timing: Push notifications usually appear within 10-30 seconds")
            print("If you don't see it within 1 minute, there's an issue")
            
        else:
            print(f"FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

def check_requirements():
    """Check phone requirements"""
    print("\nPHONE REQUIREMENTS CHECK:")
    print("=" * 40)
    print("Please verify on your phone:")
    print()
    print("1. HALOTEL MONEY APP:")
    print("   - App is installed")
    print("   - App opens without errors")
    print("   - You can see your balance")
    print("   - Your number (0614853618) is registered")
    print()
    print("2. NOTIFICATION SETTINGS:")
    print("   - Go to Settings > Apps > Halotel Money")
    print("   - Tap 'Notifications'")
    print("   - Make sure 'Allow notifications' is ON")
    print("   - Enable all notification types")
    print()
    print("3. PHONE SETTINGS:")
    print("   - Do Not Disturb is OFF")
    print("   - Internet connection is working")
    print("   - Time and date are correct")

def main():
    print("Halotel Push Notification Test")
    print("=" * 50)
    
    check_requirements()
    
    input("\nPress Enter when you've checked the requirements above...")
    print()
    
    test_push_notification()
    
    print("\n" + "=" * 50)
    print("NEXT STEPS:")
    print("=" * 50)
    print("1. If you received notification: Great! Try full purchase")
    print("2. If you didn't: Check troubleshooting steps above")
    print("3. Contact Halotel support: *149*149#")
    print("4. Try with different phone number if available")

if __name__ == '__main__':
    main()
