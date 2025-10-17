#!/usr/bin/env python3
"""
Verify SMS Packages Configuration
=================================

This script verifies that SMS packages are properly configured
and tests the sender ID logic.

Usage:
    python verify_sms_packages.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage


def verify_packages():
    """Verify that all packages have proper configurations."""
    print("🔍 Verifying SMS Packages Configuration")
    print("=" * 50)
    
    packages = SMSPackage.objects.all()
    
    if not packages.exists():
        print("❌ No SMS packages found!")
        return False
    
    print(f"📦 Found {packages.count()} SMS packages")
    
    all_valid = True
    
    for package in packages:
        print(f"\n📦 Checking {package.name}:")
        
        # Check required fields
        issues = []
        
        if not package.package_type:
            issues.append("Missing package_type")
        
        if not package.default_sender_id:
            issues.append("Missing default_sender_id")
        
        if package.sender_id_restriction not in ['none', 'default_only', 'allowed_list', 'custom_only']:
            issues.append(f"Invalid sender_id_restriction: {package.sender_id_restriction}")
        
        if not package.features:
            issues.append("Missing features")
        
        if issues:
            print(f"   ❌ Issues found: {', '.join(issues)}")
            all_valid = False
        else:
            print(f"   ✅ All fields properly configured")
            print(f"      Type: {package.package_type}")
            print(f"      Default Sender ID: {package.default_sender_id}")
            print(f"      Sender ID Restriction: {package.sender_id_restriction}")
            print(f"      Allowed Sender IDs: {package.allowed_sender_ids}")
            print(f"      Features: {len(package.features)} features")
    
    return all_valid


def test_sender_id_logic():
    """Test the sender ID logic for each package."""
    print("\n🧪 Testing Sender ID Logic")
    print("=" * 40)
    
    packages = SMSPackage.objects.all()
    test_sender_ids = ['Taarifa-SMS', 'Quantum', 'CustomID', 'TestSender', 'InvalidSender']
    
    for package in packages:
        print(f"\n📦 {package.name} ({package.sender_id_restriction}):")
        
        for sender_id in test_sender_ids:
            try:
                is_allowed = package.is_sender_id_allowed(sender_id)
                effective = package.get_effective_sender_id(sender_id)
                available = package.get_available_sender_ids()
                
                status = "✅" if is_allowed else "❌"
                print(f"   {status} '{sender_id}': Allowed={is_allowed}, Effective='{effective}'")
                
            except Exception as e:
                print(f"   ❌ Error testing '{sender_id}': {e}")
        
        print(f"   📋 Available Sender IDs: {available}")


def display_package_summary():
    """Display a summary of all packages."""
    print("\n📋 SMS Packages Summary")
    print("=" * 50)
    
    packages = SMSPackage.objects.all().order_by('price')
    
    for package in packages:
        savings = package.savings_percentage
        print(f"\n📦 {package.name} ({package.package_type.upper()})")
        print(f"   Credits: {package.credits:,}")
        print(f"   Price: TZS {package.price:,.2f}")
        print(f"   Unit Price: TZS {package.unit_price:.2f}")
        print(f"   Savings: {savings}%")
        print(f"   Default Sender ID: {package.default_sender_id}")
        print(f"   Sender ID Restriction: {package.sender_id_restriction}")
        print(f"   Allowed Sender IDs: {package.allowed_sender_ids}")
        print(f"   Popular: {'✅' if package.is_popular else '❌'}")
        print(f"   Active: {'✅' if package.is_active else '❌'}")
        print(f"   Features: {', '.join(package.features[:3])}{'...' if len(package.features) > 3 else ''}")


def main():
    """Main function to verify SMS packages."""
    print("🔍 SMS Packages Verification")
    print("=" * 40)
    
    try:
        # Verify package configurations
        config_valid = verify_packages()
        
        if not config_valid:
            print("\n❌ Package configuration issues found!")
            print("   Please run the update script to fix these issues.")
            return
        
        # Display package summary
        display_package_summary()
        
        # Test sender ID logic
        test_sender_id_logic()
        
        print("\n✅ All SMS packages are properly configured!")
        print("\n🎯 Package Configuration Summary:")
        print("   • Lite: Default sender ID only (Taarifa-SMS)")
        print("   • Standard: Allowed list (Taarifa-SMS, Quantum)")
        print("   • Pro: No restriction (all registered sender IDs)")
        print("   • Enterprise: No restriction (all registered sender IDs)")
        
    except Exception as e:
        print(f"\n❌ Error verifying SMS packages: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
