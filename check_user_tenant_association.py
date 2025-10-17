#!/usr/bin/env python3
"""
Check User-Tenant Association
============================

This script checks which users are associated with which tenants.
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

def check_user_tenant_association():
    """Check user-tenant associations"""
    print("User-Tenant Association Check")
    print("=" * 50)
    
    # Get all users
    print("\n1. All Users:")
    users = User.objects.all()
    for user in users:
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print()
    
    # Get all tenants
    print("\n2. All Tenants:")
    tenants = Tenant.objects.all()
    for tenant in tenants:
        print(f"   ID: {tenant.id}")
        print(f"   Name: {tenant.name}")
        print(f"   Subdomain: {tenant.subdomain}")
        print()
    
    # Get all memberships
    print("\n3. User-Tenant Memberships:")
    memberships = Membership.objects.all()
    for membership in memberships:
        print(f"   User: {membership.user.email} (ID: {membership.user.id})")
        print(f"   Tenant: {membership.tenant.name} (ID: {membership.tenant.id})")
        print(f"   Role: {membership.role}")
        print(f"   Status: {membership.status}")
        print()
    
    # Check SMS packages
    print("\n4. SMS Packages:")
    packages = SMSPackage.objects.filter(is_active=True)
    for package in packages:
        print(f"   ID: {package.id}")
        print(f"   Name: {package.name}")
        print(f"   Credits: {package.credits}")
        print(f"   Price: {package.price}")
        print()
    
    # Find a user with tenant association
    print("\n5. Users with Tenant Association:")
    users_with_tenants = User.objects.filter(memberships__isnull=False).distinct()
    for user in users_with_tenants:
        print(f"   User: {user.email} (ID: {user.id})")
        for membership in user.memberships.all():
            print(f"     - Tenant: {membership.tenant.name} (Role: {membership.role})")
        print()
    
    # Recommendations
    print("\n6. Recommendations for Postman Testing:")
    if users_with_tenants.exists():
        user = users_with_tenants.first()
        print(f"   Use this user for testing:")
        print(f"   Email: {user.email}")
        print(f"   Password: (use the password you set for this user)")
        print(f"   Associated Tenants: {[m.tenant.name for m in user.memberships.all()]}")
    else:
        print("   No users with tenant associations found!")
        print("   You need to create a membership for a user.")

if __name__ == '__main__':
    check_user_tenant_association()
