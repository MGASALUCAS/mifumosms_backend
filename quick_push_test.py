#!/usr/bin/env python3
"""
Quick Push Test
==============

This script creates a payment to test push notifications.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService

def test_push_notification():
    """Test push notification"""
    print("Quick Push Notification Test")
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
            print()
            print("TROUBLESHOOTING:")
            print("- Is Halotel Money app installed?")
            print("- Are notifications enabled for Halotel Money?")
            print("- Do you have internet connection?")
            print("- Is your phone number registered with Halotel Money?")
            print("- Contact Halotel support: *149*149#")
            
        else:
            print(f"FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

def main():
    test_push_notification()

if __name__ == '__main__':
    main()
