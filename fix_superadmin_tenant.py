#!/usr/bin/env python3
"""
Fix superadmin users without tenants
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
from tenants.models import Tenant

def fix_superadmin_tenant():
    """Fix superadmin users without tenants."""
    print("=" * 80)
    print("FIXING SUPERADMIN USERS WITHOUT TENANTS")
    print("=" * 80)
    
    try:
        # Find superadmin users without tenants
        superadmin_users = User.objects.filter(is_superuser=True)
        
        for user in superadmin_users:
            print(f"Superadmin User: {user.email}")
            print(f"  Tenant: {user.get_tenant()}")
            
            if not user.get_tenant():
                print(f"  No tenant assigned - fixing...")
                
                # Get or create a default tenant for superadmin users
                default_tenant = Tenant.objects.filter(name__icontains='admin').first()
                if not default_tenant:
                    default_tenant = Tenant.objects.first()
                
                if default_tenant:
                    user.tenant_id = default_tenant.id
                    user.save()
                    print(f"  Assigned tenant: {default_tenant.name}")
                else:
                    print(f"  No tenant available to assign")
            else:
                print(f"  Tenant already assigned: {user.get_tenant().name}")
    
    except Exception as e:
        print(f"Error fixing superadmin tenant: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run fix."""
    print("Fixing Superadmin Users Without Tenants")
    print("=" * 80)
    
    fix_superadmin_tenant()

if __name__ == "__main__":
    main()
