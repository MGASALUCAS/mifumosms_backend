#!/usr/bin/env python3
"""
Get Package IDs for Postman Testing
==================================

This script gets the package IDs that you can use in Postman testing.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage

def get_package_ids():
    """Get all active SMS package IDs"""
    print("SMS Package IDs for Postman Testing")
    print("=" * 50)
    
    packages = SMSPackage.objects.filter(is_active=True).order_by('price')
    
    if not packages.exists():
        print("No active SMS packages found!")
        print("Please run: python create_sms_packages_data.py")
        return
    
    print("Active SMS Packages:")
    print()
    
    for package in packages:
        print(f"Package: {package.name}")
        print(f"  ID: {package.id}")
        print(f"  Type: {package.package_type}")
        print(f"  Credits: {package.credits:,}")
        print(f"  Price: {package.price:,.2f} TZS")
        print(f"  Unit Price: {package.unit_price:,.2f} TZS")
        print(f"  Popular: {package.is_popular}")
        print(f"  Active: {package.is_active}")
        print()
    
    print("Copy any of these IDs to use in Postman testing!")
    print()
    print("Example Postman request body:")
    print("{")
    print(f'  "package_id": "{packages.first().id}",')
    print('  "buyer_email": "admin@mifumo.com",')
    print('  "buyer_name": "Admin User",')
    print('  "buyer_phone": "0744963858",')
    print('  "mobile_money_provider": "vodacom"')
    print("}")

if __name__ == '__main__':
    get_package_ids()
