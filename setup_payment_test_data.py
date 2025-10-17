#!/usr/bin/env python3
"""
Setup Payment Test Data
This script creates the necessary test data for payment flow testing
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from billing.models import SMSPackage, SMSBalance
from tenants.models import Tenant
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def setup_test_data():
    print("Setting up Payment Test Data")
    print("=" * 40)
    
    # 1. Create or get tenant
    tenant, created = Tenant.objects.get_or_create(
        subdomain='default',
        defaults={
            'name': 'Mifumo WMS Default',
            'is_active': True
        }
    )
    
    if created:
        print(f"SUCCESS: Created tenant: {tenant.name}")
    else:
        print(f"SUCCESS: Found existing tenant: {tenant.name}")
    
    # 2. Create or get superuser
    user, created = User.objects.get_or_create(
        email='admin@mifumo.com',
        defaults={
            'first_name': 'Admin',
            'last_name': 'User',
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
            'password': make_password('admin123')
        }
    )
    
    if created:
        print(f"SUCCESS: Created superuser: {user.email}")
    else:
        print(f"SUCCESS: Found existing superuser: {user.email}")
    
    # 3. Create SMS balance for tenant
    balance, created = SMSBalance.objects.get_or_create(
        tenant=tenant,
        defaults={
            'credits': 0,
            'total_purchased': 0,
            'total_used': 0
        }
    )
    
    if created:
        print(f"SUCCESS: Created SMS balance for tenant: {balance.credits} credits")
    else:
        print(f"SUCCESS: Found existing SMS balance: {balance.credits} credits")
    
    # 4. Verify SMS packages exist
    packages = SMSPackage.objects.filter(is_active=True)
    if packages.exists():
        print(f"SUCCESS: Found {packages.count()} active SMS packages:")
        for package in packages:
            print(f"   - {package.name}: {package.credits} credits for {package.price} TZS")
    else:
        print("ERROR: No active SMS packages found")
        return False
    
    print(f"\nSUCCESS: Test data setup completed!")
    print(f"Tenant: {tenant.name} (ID: {tenant.id})")
    print(f"User: {user.email} (ID: {user.id})")
    print(f"SMS Balance: {balance.credits} credits")
    print(f"SMS Packages: {packages.count()} available")
    
    return True

def test_payment_flow_with_data():
    """Test payment flow with the setup data."""
    print("\nTesting Payment Flow with Setup Data")
    print("=" * 50)
    
    # Get test data
    tenant = Tenant.objects.filter(subdomain='default').first()
    user = User.objects.filter(email='admin@mifumo.com').first()
    package = SMSPackage.objects.filter(is_active=True).first()
    
    if not all([tenant, user, package]):
        print("ERROR: Missing test data")
        return False
    
    print(f"Using test data:")
    print(f"  Tenant: {tenant.name}")
    print(f"  User: {user.email}")
    print(f"  Package: {package.name}")
    
    # Test SMS balance
    balance = SMSBalance.objects.get(tenant=tenant)
    print(f"  Initial SMS balance: {balance.credits}")
    
    # Test adding credits
    test_credits = 1000
    balance.add_credits(test_credits)
    print(f"  Added {test_credits} credits")
    print(f"  New balance: {balance.credits}")
    
    # Test using credits
    if balance.use_credits(1):
        print(f"  Used 1 credit successfully")
        print(f"  Final balance: {balance.credits}")
    else:
        print(f"  Failed to use 1 credit")
    
    print(f"\nSUCCESS: Payment flow test completed successfully!")
    return True

def main():
    print("Payment Test Data Setup")
    print("=" * 50)
    
    # Setup test data
    if setup_test_data():
        # Test payment flow
        test_payment_flow_with_data()
        
        print(f"\nSUCCESS: Payment system is ready for testing!")
        print(f"You can now run the complete payment flow test.")
    else:
        print(f"\nERROR: Failed to setup test data")

if __name__ == "__main__":
    main()
