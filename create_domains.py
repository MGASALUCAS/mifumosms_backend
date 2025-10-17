#!/usr/bin/env python3
"""
Create Domains for Production
Quick script to create domain mappings
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from tenants.models import Tenant, Domain

def main():
    print("🌐 Creating Domains for Production")
    print("=" * 40)
    
    # Get default tenant
    tenant = Tenant.objects.filter(subdomain='default').first()
    if not tenant:
        print("❌ No default tenant found! Run fix_missing_models.py first.")
        return
    
    print(f"✅ Found tenant: {tenant.name}")
    
    # Create domains
    domains = [
        '104.131.116.55:8000',
        'mifumo.local',
        'localhost:8000',
    ]
    
    for domain_name in domains:
        domain, created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={
                'tenant': tenant,
                'is_primary': domain_name == '104.131.116.55:8000',
                'verified': True,
            }
        )
        
        if created:
            print(f"✅ Created domain: {domain.domain}")
        else:
            print(f"ℹ️  Domain already exists: {domain.domain}")
    
    print("\n🎉 Domains created successfully!")
    print("You should now see Domains in the admin panel.")

if __name__ == "__main__":
    main()
