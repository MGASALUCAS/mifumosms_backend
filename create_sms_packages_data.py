#!/usr/bin/env python3
"""
Create SMS Packages Data
This script creates the actual SMS packages in the database
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage

def create_sms_packages():
    print("Creating SMS Packages in Database")
    print("=" * 40)
    
    # Clear existing packages first
    SMSPackage.objects.all().delete()
    print("Cleared existing SMS packages")
    
    # Create the packages as shown in your interface
    packages_data = [
        {
            'name': 'Lite',
            'package_type': 'lite',
            'credits': 5000,
            'price': 150000.00,
            'unit_price': 30.00,
            'is_popular': False,
            'is_active': True,
            'features': ['Basic SMS sending', 'Standard support'],
            'default_sender_id': 'Taarifa-SMS',
            'sender_id_restriction': 'default_only',
            'allowed_sender_ids': []
        },
        {
            'name': 'Standard',
            'package_type': 'standard',
            'credits': 50000,
            'price': 1250000.00,
            'unit_price': 25.00,
            'is_popular': True,
            'is_active': True,
            'features': ['Bulk SMS sending', 'Priority support', 'Delivery reports'],
            'default_sender_id': 'Taarifa-SMS',
            'sender_id_restriction': 'allowed_list',
            'allowed_sender_ids': ['Taarifa-SMS', 'Quantum']
        },
        {
            'name': 'Pro',
            'package_type': 'pro',
            'credits': 250000,
            'price': 4500000.00,
            'unit_price': 18.00,
            'is_popular': False,
            'is_active': True,
            'features': ['Advanced SMS features', 'API access', 'Custom sender IDs', 'Analytics'],
            'default_sender_id': 'Taarifa-SMS',
            'sender_id_restriction': 'none',
            'allowed_sender_ids': []
        },
        {
            'name': 'Enterprise',
            'package_type': 'enterprise',
            'credits': 1000000,
            'price': 12000000.00,
            'unit_price': 12.00,
            'is_popular': False,
            'is_active': True,
            'features': ['Unlimited features', 'Dedicated support', 'Custom integrations', 'White-label'],
            'default_sender_id': 'Quantum',
            'sender_id_restriction': 'none',
            'allowed_sender_ids': []
        }
    ]
    
    created_packages = []
    
    for package_data in packages_data:
        package = SMSPackage.objects.create(**package_data)
        created_packages.append(package)
        print(f"Created: {package.name} - {package.credits} credits - {package.price} TZS")
    
    print(f"\nSuccessfully created {len(created_packages)} SMS packages!")
    return created_packages

def display_packages():
    print("\nSMS Packages in Database")
    print("=" * 40)
    
    packages = SMSPackage.objects.all().order_by('price')
    
    if not packages.exists():
        print("No packages found!")
        return
    
    for package in packages:
        print(f"\nPackage: {package.name}")
        print(f"  Type: {package.package_type}")
        print(f"  Credits: {package.credits:,}")
        print(f"  Price: {package.price:,.2f} TZS")
        print(f"  Unit Price: {package.unit_price:.2f} TZS")
        print(f"  Is Popular: {package.is_popular}")
        print(f"  Is Active: {package.is_active}")
        print(f"  Features: {', '.join(package.features)}")
        print(f"  Default Sender ID: {package.default_sender_id}")
        print(f"  Sender ID Restriction: {package.sender_id_restriction}")
        if package.allowed_sender_ids:
            print(f"  Allowed Sender IDs: {', '.join(package.allowed_sender_ids)}")

def main():
    print("SMS Packages Database Setup")
    print("=" * 50)
    print("Creating SMS packages as shown in your interface:")
    print("- Lite: 5,000 credits for 150,000 TZS")
    print("- Standard: 50,000 credits for 1,250,000 TZS (Popular)")
    print("- Pro: 250,000 credits for 4,500,000 TZS")
    print("- Enterprise: 1,000,000 credits for 12,000,000 TZS")
    print()
    
    # Create packages
    packages = create_sms_packages()
    
    # Display created packages
    display_packages()
    
    print("\nSUCCESS: SMS packages created in database!")
    print("You can now see them in the admin interface at:")
    print("http://localhost:8000/admin/billing/smspackage/")

if __name__ == "__main__":
    main()
