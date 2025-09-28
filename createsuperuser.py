#!/usr/bin/env python
"""
Simple alias for createsuperuser that works with custom user model.
Usage: python createsuperuser.py email first_name last_name password
"""
import sys
import os
import django

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python createsuperuser.py email first_name last_name password")
        print("Example: python createsuperuser.py admin@example.com Admin User password123")
        sys.exit(1)
    
    email = sys.argv[1]
    first_name = sys.argv[2]
    last_name = sys.argv[3]
    password = sys.argv[4]
    
    try:
        call_command('create_admin', 
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password)
        print(f"\n✅ Superuser created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🌐 Admin URL: http://localhost:8000/admin/")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
