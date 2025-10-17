#!/usr/bin/env python3
"""
Quick Production Fix
Run this directly on your production server
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.management import call_command
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

def main():
    print("🔧 Quick Production Fix")
    print("=" * 30)
    
    try:
        # Run migrations
        print("🔄 Running migrations...")
        call_command('migrate', verbosity=1)
        
        # Create site
        print("🌐 Creating site...")
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': '196.249.97.239:8000',
                'name': 'Mifumo WMS Production'
            }
        )
        print(f"Site: {site.domain}")
        
        # Create superuser
        print("👤 Creating superuser...")
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@mifumo.com',
                password='admin123'
            )
            print("✅ Superuser created: admin/admin123")
        else:
            print("ℹ️  Superuser exists")
        
        print("✅ Fix completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
