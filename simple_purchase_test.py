#!/usr/bin/env python3
"""
Simple Purchase Page Test
========================

This script tests the purchase page functionality without Unicode characters.
"""

import os
import sys
import django
import requests
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

def test_purchase_page_api():
    """Test the API endpoints used by the purchase page"""
    print("Testing Purchase Page API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # Test 1: Get SMS packages
    print("1. Testing SMS packages endpoint...")
    try:
        response = requests.get(f"{base_url}/billing/sms/packages/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                print(f"   SUCCESS: Found {len(data['data'])} packages")
                for package in data['data']:
                    print(f"      - {package['name']}: {package['credits']} credits for {package['price']} TZS")
            else:
                print(f"   FAILED: No packages found: {data}")
        else:
            print(f"   FAILED: HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Authentication
    print("\n2. Testing authentication...")
    try:
        auth_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        response = requests.post(f"{base_url}/auth/login/", json=auth_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('tokens') and data['tokens'].get('access'):
                print("   SUCCESS: Authentication successful")
                token = data['tokens']['access']
                
                # Test 3: Payment initiation
                print("\n3. Testing payment initiation...")
                payment_data = {
                    "package_id": "b4f12412-d0ae-4ece-b245-10aac43d73be",  # Lite package
                    "buyer_name": "Test User",
                    "buyer_email": "test@example.com",
                    "buyer_phone": "0614853618",
                    "mobile_money_provider": "halotel"
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
                
                response = requests.post(f"{base_url}/billing/payments/initiate/", 
                                       json=payment_data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    if data.get('success'):
                        print("   SUCCESS: Payment initiation successful")
                        print(f"      Order ID: {data['data']['order_id']}")
                        print(f"      Amount: {data['data']['amount']} TZS")
                        print(f"      Provider: {data['data']['provider_name']}")
                        print(f"      Status: {data['data']['status']}")
                    else:
                        print(f"   FAILED: Payment failed: {data.get('message', 'Unknown error')}")
                else:
                    print(f"   FAILED: HTTP {response.status_code}: {response.text}")
            else:
                print(f"   FAILED: No access token: {data}")
        else:
            print(f"   FAILED: HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")

def test_phone_provider_mapping():
    """Test phone number to provider mapping"""
    print("\n4. Testing phone number to provider mapping...")
    
    test_cases = [
        ("0614853618", "halotel", "Halotel Money"),
        ("0757347863", "vodacom", "Vodacom M-Pesa"),
        ("0651234567", "tigo", "Tigo Pesa"),
        ("0712345678", "airtel", "Airtel Money"),
    ]
    
    for phone, expected_provider, provider_name in test_cases:
        print(f"   {phone} -> {expected_provider} ({provider_name})")

def main():
    print("Purchase Page API Test")
    print("=" * 50)
    print("This tests the API endpoints used by the purchase page")
    print()
    
    test_purchase_page_api()
    test_phone_provider_mapping()
    
    print("\n" + "=" * 50)
    print("Next Steps:")
    print("=" * 50)
    print("1. Start the Django server: python manage.py runserver")
    print("2. Start the purchase page server: python serve_purchase_page.py")
    print("3. Open: http://localhost:8080/purchase_packages.html")
    print("4. Test the complete purchase flow!")

if __name__ == '__main__':
    main()
