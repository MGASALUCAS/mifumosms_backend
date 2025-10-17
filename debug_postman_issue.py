#!/usr/bin/env python3
"""
Debug Postman Issue
==================

This script helps debug the "User is not associated with any tenant" issue in Postman.
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

def debug_postman_issue():
    """Debug the Postman tenant association issue"""
    print("Debugging Postman Issue")
    print("=" * 50)
    
    # Check the specific user
    print("\n1. Checking user: admin@example.com")
    try:
        user = User.objects.get(email='admin@example.com')
        print(f"   User found: {user.email} (ID: {user.id})")
        print(f"   Is active: {user.is_active}")
        print(f"   Is staff: {user.is_staff}")
        print(f"   Is superuser: {user.is_superuser}")
    except User.DoesNotExist:
        print("   ERROR: User not found!")
        return False
    
    # Check user memberships
    print("\n2. Checking user memberships:")
    memberships = user.memberships.all()
    if memberships.exists():
        for membership in memberships:
            print(f"   - Tenant: {membership.tenant.name} (ID: {membership.tenant.id})")
            print(f"     Role: {membership.role}")
            print(f"     Status: {membership.status}")
            print(f"     Joined: {membership.joined_at}")
    else:
        print("   ERROR: No memberships found!")
        return False
    
    # Check if user has active memberships
    print("\n3. Checking active memberships:")
    active_memberships = user.memberships.filter(status='active')
    if active_memberships.exists():
        for membership in active_memberships:
            print(f"   - Active in: {membership.tenant.name}")
    else:
        print("   ERROR: No active memberships found!")
        print("   All memberships:")
        for membership in memberships:
            print(f"     - {membership.tenant.name}: {membership.status}")
        return False
    
    # Check SMS packages in the tenant
    print("\n4. Checking SMS packages in user's tenant:")
    for membership in active_memberships:
        tenant = membership.tenant
        packages = SMSPackage.objects.filter(is_active=True)
        print(f"   Tenant: {tenant.name}")
        print(f"   Packages: {packages.count()}")
        for package in packages:
            print(f"     - {package.name}: {package.credits} credits")
    
    # Test authentication
    print("\n5. Testing authentication:")
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"   JWT Token generated: {access_token[:50]}...")
    
    # Test tenant resolution
    print("\n6. Testing tenant resolution:")
    try:
        from tenants.middleware import TenantMiddleware
        from django.http import HttpRequest
        
        # Simulate a request
        request = HttpRequest()
        request.user = user
        request.META['HTTP_HOST'] = '127.0.0.1:8000'
        
        # This is a simplified test - the actual middleware logic
        print(f"   User: {request.user}")
        print(f"   User memberships: {user.memberships.count()}")
        
        # Check if user has any active memberships
        if user.memberships.filter(status='active').exists():
            print("   SUCCESS: User has active memberships")
        else:
            print("   ERROR: User has no active memberships")
            
    except Exception as e:
        print(f"   ERROR: Tenant resolution test failed: {str(e)}")
    
    print("\n7. Recommendations:")
    print("   - Make sure you're using the correct email: admin@example.com")
    print("   - Make sure the JWT token is valid and not expired")
    print("   - Try logging out and logging back in")
    print("   - Check if the user has active memberships")
    
    return True

def fix_membership_status():
    """Fix membership status if needed"""
    print("\n8. Fixing membership status...")
    
    try:
        user = User.objects.get(email='admin@example.com')
        memberships = user.memberships.all()
        
        for membership in memberships:
            if membership.status != 'active':
                print(f"   Updating {membership.tenant.name} membership to active")
                membership.status = 'active'
                membership.save()
            else:
                print(f"   {membership.tenant.name} membership is already active")
        
        print("   SUCCESS: Membership status updated")
        return True
        
    except Exception as e:
        print(f"   ERROR: Failed to fix membership status: {str(e)}")
        return False

def main():
    print("Postman Debug Tool")
    print("=" * 50)
    
    if debug_postman_issue():
        print("\nTrying to fix the issue...")
        fix_membership_status()
        
        print("\n" + "="*50)
        print("DEBUG COMPLETE")
        print("="*50)
        print("If the issue persists:")
        print("1. Make sure you're using admin@example.com in Postman")
        print("2. Try logging out and logging back in")
        print("3. Check the JWT token is not expired")
        print("4. Verify the user has active memberships")
    else:
        print("\nERROR: Debug failed!")

if __name__ == '__main__':
    main()
