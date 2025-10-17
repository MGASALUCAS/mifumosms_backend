#!/usr/bin/env python3
"""
Check Phone Network Mapping
==========================

This script checks the correct network mapping for Tanzania phone numbers.
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.zenopay_service import ZenoPayService

def check_phone_networks():
    """Check phone network mapping"""
    print("Tanzania Phone Network Mapping")
    print("=" * 50)
    
    # Tanzania phone number prefixes
    networks = {
        "075": "Vodacom M-Pesa",
        "076": "Vodacom M-Pesa", 
        "074": "Vodacom M-Pesa",
        "078": "Vodacom M-Pesa",
        "065": "Tigo Pesa",
        "066": "Tigo Pesa",
        "067": "Tigo Pesa",
        "068": "Tigo Pesa",
        "069": "Tigo Pesa",
        "071": "Airtel Money",
        "073": "Airtel Money",
        "075": "Airtel Money (some)",
        "062": "Halotel",
        "063": "Halotel",
        "064": "Halotel",
        "061": "Halotel",  # This is the key one!
    }
    
    print("Tanzania Mobile Network Prefixes:")
    for prefix, network in networks.items():
        print(f"   {prefix}xxx -> {network}")
    
    print(f"\nYour phone number: 0614853618")
    print(f"Prefix: 061")
    print(f"Network: {networks.get('061', 'Unknown')}")
    
    return networks.get('061', 'Unknown')

def test_halotel_provider():
    """Test with Halotel provider since your phone starts with 061"""
    print("\nTesting with Halotel provider (since your phone starts with 061):")
    
    zenopay_service = ZenoPayService()
    
    try:
        payment_response = zenopay_service.create_payment(
            order_id=f"DEBUG-HALOTEL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            buyer_email="admin@example.com",
            buyer_name="Admin User",
            buyer_phone="0614853618",  # Your actual phone
            amount=150000,
            webhook_url="https://ileana-unsupposed-nonmortally.ngrok-free.dev/api/billing/payments/webhook/",
            mobile_money_provider="halotel"  # Use Halotel instead
        )
        
        print(f"   Payment Response: {payment_response}")
        
        if payment_response.get('success'):
            print("   SUCCESS: Halotel payment created!")
            print("   Check your phone for Halotel Money notification!")
        else:
            print(f"   FAILED: {payment_response.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ERROR: {str(e)}")

def test_all_providers():
    """Test all providers to see which one works"""
    print("\nTesting all providers with your phone (0614853618):")
    
    zenopay_service = ZenoPayService()
    providers = ["vodacom", "tigo", "airtel", "halotel"]
    
    for provider in providers:
        print(f"\n   Testing {provider.upper()}:")
        try:
            payment_response = zenopay_service.create_payment(
                order_id=f"DEBUG-{provider.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
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
    print("Phone Network Check")
    print("=" * 50)
    
    network = check_phone_networks()
    
    if network == "Halotel":
        print("\nCORRECT: Your phone (0614853618) is a Halotel number!")
        print("Use 'halotel' as mobile_money_provider in Postman")
        test_halotel_provider()
    else:
        print(f"\nYour phone network: {network}")
        test_all_providers()
    
    print("\n" + "="*50)
    print("SOLUTION FOR POSTMAN:")
    print("="*50)
    print("Change your Postman request to use:")
    print('"mobile_money_provider": "halotel"')
    print("\nMake sure you have Halotel Money app installed!")

if __name__ == '__main__':
    main()
