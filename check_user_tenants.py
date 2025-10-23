#!/usr/bin/env python3
"""
Check which users don't have tenants.
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

def check_user_tenants():
    """Check which users don't have tenants."""
    print("Checking user tenants...")
    
    users_without_tenants = []
    
    for user in User.objects.all():
        try:
            tenant = user.get_tenant()
            print(f"OK {user.email} -> {tenant.name}")
        except Exception as e:
            print(f"ERROR {user.email} -> ERROR: {str(e)}")
            users_without_tenants.append(user)
    
    print(f"\nUsers without tenants: {len(users_without_tenants)}")
    for user in users_without_tenants:
        print(f"  - {user.email}")

if __name__ == "__main__":
    check_user_tenants()
