#!/usr/bin/env python3
"""
Fix User-Tenant Association
==========================

This script creates the proper user-tenant association for testing.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from billing.models import SMSPackage

User = get_user_model()

def fix_user_tenant_association():
    """Fix user-tenant association for testing"""
    print("Fixing User-Tenant Association")
    print("=" * 50)
    
    # Get the user
    try:
        user = User.objects.get(email='admin@example.com')
        print(f"Found user: {user.email}")
    except User.DoesNotExist:
        print("User admin@example.com not found!")
        return False
    
    # Get the default tenant (where SMS packages are)
    try:
        default_tenant = Tenant.objects.get(subdomain='default')
        print(f"Found default tenant: {default_tenant.name}")
    except Tenant.DoesNotExist:
        print("Default tenant not found!")
        return False
    
    # Check if membership already exists
    existing_membership = Membership.objects.filter(
        user=user, 
        tenant=default_tenant
    ).first()
    
    if existing_membership:
        print(f"Membership already exists: {existing_membership}")
        print(f"Status: {existing_membership.status}")
        print(f"Role: {existing_membership.role}")
        
        # Update status to active if needed
        if existing_membership.status != 'active':
            existing_membership.status = 'active'
            existing_membership.save()
            print("Updated membership status to active")
    else:
        # Create new membership
        membership = Membership.objects.create(
            user=user,
            tenant=default_tenant,
            role='owner',
            status='active'
        )
        print(f"Created new membership: {membership}")
    
    # Verify the association
    print("\nVerifying association...")
    user_memberships = user.memberships.all()
    print(f"User {user.email} is now associated with:")
    for membership in user_memberships:
        print(f"  - {membership.tenant.name} (Role: {membership.role}, Status: {membership.status})")
    
    # Check SMS packages in the tenant
    print(f"\nSMS Packages in {default_tenant.name}:")
    packages = SMSPackage.objects.filter(is_active=True)
    for package in packages:
        print(f"  - {package.name}: {package.credits} credits for {package.price} TZS (ID: {package.id})")
    
    print("\nSUCCESS: User-tenant association fixed!")
    print("You can now use admin@example.com for Postman testing")
    
    return True

if __name__ == '__main__':
    fix_user_tenant_association()
