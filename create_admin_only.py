#!/usr/bin/env python3
"""
Create Admin User Only
Creates just the admin user for the system
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin():
    """Create admin user"""
    print("👤 Creating admin user...")
    
    try:
        user, created = User.objects.get_or_create(
            email='admin@mifumo.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            print(f"   ✅ Created admin user: {user.email}")
        else:
            print(f"   ℹ️  Admin user already exists: {user.email}")
            # Update password anyway
            user.set_password('admin123')
            user.save()
            print(f"   🔑 Updated password for: {user.email}")
        
        print(f"\n🌐 Admin Dashboard: http://104.131.116.55:8000/admin/")
        print(f"📧 Login: {user.email}")
        print(f"🔑 Password: admin123")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin()
