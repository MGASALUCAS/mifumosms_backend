#!/usr/bin/env python3
"""
Update Existing SMS Packages Script
===================================

This script updates existing SMS packages with proper package types
and sender ID configurations without deleting them.

Usage:
    python update_existing_sms_packages.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage


def update_existing_packages():
    """Update existing SMS packages with proper configurations."""
    print("🔄 Updating existing SMS packages...")
    
    packages = SMSPackage.objects.all()
    
    if not packages.exists():
        print("❌ No SMS packages found. Please create packages first.")
        return
    
    # Package type mapping based on name
    package_configs = {
        'Lite': {
            'package_type': 'lite',
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': [],
            'sender_id_restriction': 'default_only',
            'features': [
                'Basic SMS sending',
                'Standard delivery reports',
                'Email support'
            ]
        },
        'Standard': {
            'package_type': 'standard',
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': ['Taarifa-SMS', 'Quantum'],
            'sender_id_restriction': 'allowed_list',
            'features': [
                'High volume SMS sending',
                'Advanced delivery reports',
                'Priority support',
                'Scheduled messaging'
            ]
        },
        'Pro': {
            'package_type': 'pro',
            'default_sender_id': 'Taarifa-SMS',
            'allowed_sender_ids': [],
            'sender_id_restriction': 'none',
            'features': [
                'Unlimited SMS sending',
                'Real-time delivery reports',
                '24/7 phone support',
                'Advanced analytics',
                'API access',
                'Custom sender IDs'
            ]
        },
        'Enterprise': {
            'package_type': 'enterprise',
            'default_sender_id': 'Quantum',
            'allowed_sender_ids': [],
            'sender_id_restriction': 'none',
            'features': [
                'Massive volume SMS',
                'Enterprise-grade delivery reports',
                'Dedicated account manager',
                'Advanced analytics dashboard',
                'Full API access',
                'Custom sender IDs',
                'White-label solutions',
                'SLA guarantees'
            ]
        }
    }
    
    updated_count = 0
    
    for package in packages:
        print(f"\n📦 Updating {package.name} package...")
        
        # Get configuration for this package
        config = package_configs.get(package.name)
        
        if not config:
            print(f"   ⚠️  No configuration found for '{package.name}', skipping...")
            continue
        
        # Update package fields
        package.package_type = config['package_type']
        package.default_sender_id = config['default_sender_id']
        package.allowed_sender_ids = config['allowed_sender_ids']
        package.sender_id_restriction = config['sender_id_restriction']
        package.features = config['features']
        
        # Save the package
        package.save()
        updated_count += 1
        
        print(f"   ✅ Updated: {package.name}")
        print(f"      Type: {package.package_type}")
        print(f"      Default Sender ID: {package.default_sender_id}")
        print(f"      Sender ID Restriction: {package.sender_id_restriction}")
        print(f"      Allowed Sender IDs: {package.allowed_sender_ids}")
        print(f"      Features: {len(package.features)} features")
    
    return updated_count


def display_updated_packages():
    """Display all updated packages."""
    print("\n📋 Updated SMS Packages:")
    print("=" * 60)
    
    packages = SMSPackage.objects.all().order_by('price')
    
    for package in packages:
        print(f"\n📦 {package.name} ({package.package_type.upper()})")
        print(f"   Credits: {package.credits:,}")
        print(f"   Price: TZS {package.price:,.2f}")
        print(f"   Unit Price: TZS {package.unit_price:.2f}")
        print(f"   Default Sender ID: {package.default_sender_id}")
        print(f"   Sender ID Restriction: {package.sender_id_restriction}")
        print(f"   Allowed Sender IDs: {package.allowed_sender_ids}")
        print(f"   Popular: {'✅' if package.is_popular else '❌'}")
        print(f"   Active: {'✅' if package.is_active else '❌'}")


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
            
            status = "✅" if is_allowed else "❌"
            print(f"   {status} '{sender_id}': Effective='{effective}'")


def main():
    """Main function to update SMS packages."""
    print("🔄 Updating SMS Packages for Production")
    print("=" * 50)
    
    try:
        # Update existing packages
        updated_count = update_existing_packages()
        
        if updated_count == 0:
            print("\n❌ No packages were updated.")
            return
        
        # Display updated packages
        display_updated_packages()
        
        # Test sender ID logic
        test_sender_id_logic()
        
        print(f"\n✅ Successfully updated {updated_count} SMS packages!")
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
        print(f"\n❌ Error updating SMS packages: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
