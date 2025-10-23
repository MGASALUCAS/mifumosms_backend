#!/usr/bin/env python3
"""
Fix user without tenant.
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from tenants.models import Tenant, Membership

def fix_user_tenant():
    """Fix user without tenant."""
    print("Fixing user without tenant...")
    
    # Get the user without tenant
    user = User.objects.get(email='jose@gmail.com')
    print(f"User: {user.email}")
    
    # Get the first available tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("ERROR: No tenants found")
        return
    
    print(f"Assigning to tenant: {tenant.name}")
    
    # Create membership for user
    membership, created = Membership.objects.get_or_create(
        user=user,
        tenant=tenant,
        defaults={
            'role': 'agent',
            'status': 'active'
        }
    )
    
    if created:
        print("SUCCESS: Created membership for user")
    else:
        print("SUCCESS: Membership already exists")
    
    # Verify
    try:
        user_tenant = user.get_tenant()
        print(f"Verification: {user.email} -> {user_tenant.name}")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    fix_user_tenant()
