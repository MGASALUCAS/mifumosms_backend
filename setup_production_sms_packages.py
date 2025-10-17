#!/usr/bin/env python3
"""
Production SMS Packages Setup Script
====================================

This script sets up SMS packages in the production server with proper
sender ID configurations and package types.

Usage:
    python setup_production_sms_packages.py
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage


def clear_existing_packages():
    """Clear existing SMS packages to start fresh."""
    print("🗑️  Clearing existing SMS packages...")
    count = SMSPackage.objects.count()
    SMSPackage.objects.all().delete()
    print(f"   ✅ Deleted {count} existing packages")


def create_sms_packages():
    """Create SMS packages with proper configurations."""
    print("\n📦 Creating SMS packages with sender ID configurations...")
    
    packages_data = [
        {
            'name': 'Lite',
            'package_type': 'lite',
            'credits': 5000,
            'price': Decimal('150000.00'),
            'unit_price': Decimal('30.00'),
            'is_popular': False,
            'is_active': True,
            'features': [
                'Basic SMS sending',
                'Standard delivery reports',
                'Email support'
            ],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': [],
            'sender_id_restriction': 'default_only'
        },
        {
            'name': 'Standard',
            'package_type': 'standard',
            'credits': 50000,
            'price': Decimal('1250000.00'),
            'unit_price': Decimal('25.00'),
            'is_popular': True,
            'is_active': True,
            'features': [
                'High volume SMS sending',
                'Advanced delivery reports',
                'Priority support',
                'Scheduled messaging'
            ],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'Quantum'],
            'sender_id_restriction': 'allowed_list'
        },
        {
            'name': 'Pro',
            'package_type': 'pro',
            'credits': 250000,
            'price': Decimal('4500000.00'),
            'unit_price': Decimal('18.00'),
            'is_popular': False,
            'is_active': True,
            'features': [
                'Unlimited SMS sending',
                'Real-time delivery reports',
                '24/7 phone support',
                'Advanced analytics',
                'API access',
                'Custom sender IDs'
            ],
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': [],
            'sender_id_restriction': 'none'
        },
        {
            'name': 'Enterprise',
            'package_type': 'enterprise',
            'credits': 1000000,
            'price': Decimal('12000000.00'),
            'unit_price': Decimal('12.00'),
            'is_popular': False,
            'is_active': True,
            'features': [
                'Massive volume SMS',
                'Enterprise-grade delivery reports',
                'Dedicated account manager',
                'Advanced analytics dashboard',
                'Full API access',
                'Custom sender IDs',
                'White-label solutions',
                'SLA guarantees'
            ],
            'default_sender_id': 'Quantum',
            'allowed_sender_ids': [],
            'sender_id_restriction': 'none'
        }
    ]
    
    created_packages = []
    
    for package_data in packages_data:
        print(f"\n   Creating {package_data['name']} package...")
        
        package = SMSPackage.objects.create(**package_data)
        created_packages.append(package)
        
        print(f"   ✅ Created: {package.name}")
        print(f"      Type: {package.package_type}")
        print(f"      Credits: {package.credits:,}")
        print(f"      Price: TZS {package.price:,.2f}")
        print(f"      Unit Price: TZS {package.unit_price:.2f}")
        print(f"      Default Sender ID: {package.default_sender_id}")
        print(f"      Sender ID Restriction: {package.sender_id_restriction}")
        print(f"      Allowed Sender IDs: {package.allowed_sender_ids}")
        print(f"      Popular: {'Yes' if package.is_popular else 'No'}")
        print(f"      Active: {'Yes' if package.is_active else 'No'}")
        print(f"      Features: {len(package.features)} features")
    
    return created_packages


def display_packages():
    """Display all created packages."""
    print("\n📋 SMS Packages Summary:")
    print("=" * 80)
    
    packages = SMSPackage.objects.all().order_by('price')
    
    for package in packages:
        print(f"\n📦 {package.name} ({package.package_type.upper()})")
        print(f"   Credits: {package.credits:,}")
        print(f"   Price: TZS {package.price:,.2f}")
        print(f"   Unit Price: TZS {package.unit_price:.2f}")
        print(f"   Savings: {package.savings_percentage}%")
        print(f"   Default Sender ID: {package.default_sender_id}")
        print(f"   Sender ID Restriction: {package.sender_id_restriction}")
        print(f"   Allowed Sender IDs: {package.allowed_sender_ids}")
        print(f"   Popular: {'✅' if package.is_popular else '❌'}")
        print(f"   Active: {'✅' if package.is_active else '❌'}")
        print(f"   Features: {', '.join(package.features)}")


def test_sender_id_logic():
    """Test the sender ID logic for each package."""
    print("\n🧪 Testing Sender ID Logic:")
    print("=" * 50)
    
    packages = SMSPackage.objects.all()
    test_sender_ids = ['Taarifa-SMS', 'Quantum', 'CustomID', 'TestSender']
    
    for package in packages:
        print(f"\n📦 {package.name} ({package.sender_id_restriction}):")
        
        for sender_id in test_sender_ids:
            is_allowed = package.is_sender_id_allowed(sender_id)
            effective = package.get_effective_sender_id(sender_id)
            available = package.get_available_sender_ids()
            
            print(f"   '{sender_id}': Allowed={is_allowed}, Effective='{effective}'")
        
        print(f"   Available Sender IDs: {available}")


def main():
    """Main function to set up SMS packages."""
    print("🚀 Setting up SMS Packages for Production")
    print("=" * 50)
    
    try:
        # Clear existing packages
        clear_existing_packages()
        
        # Create new packages
        created_packages = create_sms_packages()
        
        # Display summary
        display_packages()
        
        # Test sender ID logic
        test_sender_id_logic()
        
        print(f"\n✅ Successfully created {len(created_packages)} SMS packages!")
        print("\n📝 Package Configuration Summary:")
        print("   • Lite: Default sender ID only (Taarifa-SMS)")
        print("   • Standard: Allowed list (Taarifa-SMS, Quantum)")
        print("   • Pro: No restriction (all registered sender IDs)")
        print("   • Enterprise: No restriction (all registered sender IDs)")
        
        print("\n🎯 Next Steps:")
        print("   1. Verify packages in Django admin")
        print("   2. Test SMS sending with different packages")
        print("   3. Configure frontend to use package restrictions")
        
    except Exception as e:
        print(f"\n❌ Error setting up SMS packages: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
