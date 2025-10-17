#!/usr/bin/env python3
"""
Update SMS Packages with Sender ID Configuration
This script updates existing SMS packages with appropriate sender ID settings
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage

def update_sms_packages():
    print("Updating SMS Packages with Sender ID Configuration")
    print("=" * 60)
    
    # Get all SMS packages
    packages = SMSPackage.objects.all()
    
    if not packages.exists():
        print("ERROR: No SMS packages found!")
        return
    
    print(f"Found {packages.count()} SMS packages to update")
    print()
    
    # Update each package based on its type
    for package in packages:
        print(f"Updating: {package.name} ({package.package_type})")
        
        if package.package_type == 'lite':
            # Lite package - restricted to default sender ID only
            package.default_sender_id = 'Taarifa-SMS'
            package.sender_id_restriction = 'default_only'
            package.allowed_sender_ids = []
            print(f"   SUCCESS: Set to: Default sender ID only (Taarifa-SMS)")
            
        elif package.package_type == 'standard':
            # Standard package - allowed list of common sender IDs
            package.default_sender_id = 'Taarifa-SMS'
            package.sender_id_restriction = 'allowed_list'
            package.allowed_sender_ids = ['Taarifa-SMS', 'Quantum']
            print(f"   SUCCESS: Set to: Allowed list (Taarifa-SMS, Quantum)")
            
        elif package.package_type == 'pro':
            # Pro package - all registered sender IDs allowed
            package.default_sender_id = 'Taarifa-SMS'
            package.sender_id_restriction = 'none'
            package.allowed_sender_ids = []
            print(f"   SUCCESS: Set to: No restriction (all sender IDs)")
            
        elif package.package_type == 'enterprise':
            # Enterprise package - all registered sender IDs allowed
            package.default_sender_id = 'Quantum'  # More professional
            package.sender_id_restriction = 'none'
            package.allowed_sender_ids = []
            print(f"   SUCCESS: Set to: No restriction (all sender IDs)")
            
        elif package.package_type == 'custom':
            # Custom package - custom sender IDs only
            package.default_sender_id = None
            package.sender_id_restriction = 'custom_only'
            package.allowed_sender_ids = []
            print(f"   SUCCESS: Set to: Custom sender IDs only")
        
        package.save()
        print(f"   SAVED: Successfully updated")
        print()

def test_sender_id_logic():
    print("Testing Sender ID Logic")
    print("=" * 40)
    
    packages = SMSPackage.objects.all()
    
    for package in packages:
        print(f"\nTesting: {package.name}")
        print(f"   Default Sender ID: {package.default_sender_id}")
        print(f"   Restriction: {package.sender_id_restriction}")
        print(f"   Allowed List: {package.allowed_sender_ids}")
        
        # Test different sender IDs
        test_sender_ids = ['Taarifa-SMS', 'Quantum', 'MIFUMO', 'CustomID']
        
        for sender_id in test_sender_ids:
            is_allowed = package.is_sender_id_allowed(sender_id)
            effective = package.get_effective_sender_id(sender_id)
            status = "PASS" if is_allowed else "FAIL"
            print(f"   {status} {sender_id}: Allowed={is_allowed}, Effective={effective}")
        
        # Test available sender IDs
        available = package.get_available_sender_ids()
        print(f"   Available: {available}")

def main():
    print("SMS Package Sender ID Configuration")
    print("=" * 50)
    print("This will update your SMS packages with sender ID settings:")
    print("- Lite: Default sender ID only")
    print("- Standard: Allowed list (Taarifa-SMS, Quantum)")
    print("- Pro: No restriction (all sender IDs)")
    print("- Enterprise: No restriction (all sender IDs)")
    print("- Custom: Custom sender IDs only")
    print()
    
    # Update packages
    update_sms_packages()
    
    # Test the logic
    test_sender_id_logic()
    
    print("\nSUCCESS: SMS packages updated successfully!")
    print("Now your SMS packages have sender ID management built-in.")

if __name__ == "__main__":
    main()
