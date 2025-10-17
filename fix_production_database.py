#!/usr/bin/env python3
"""
Production Database Fix Script
This script fixes missing database tables and creates necessary data for production
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.core.management import call_command

User = get_user_model()

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_missing_tables():
    """Check which Django tables are missing"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'django_%'")
        existing_tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = [
        'django_site',
        'django_migrations',
        'django_content_type',
        'django_session',
        'auth_user',
        'auth_group',
        'auth_permission',
    ]
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    print(f"📊 Existing Django tables: {len(existing_tables)}")
    print(f"❌ Missing tables: {missing_tables}")
    
    return missing_tables

def run_migrations():
    """Run Django migrations to create missing tables"""
    print("\n🔄 Running Django migrations...")
    try:
        # First, create migrations for all apps
        call_command('makemigrations', verbosity=2)
        
        # Then apply migrations
        call_command('migrate', verbosity=2)
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_site_data():
    """Create Site object for production"""
    print("\n🌐 Creating Site data...")
    try:
        # Get or create the site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': '196.249.97.239:8000',
                'name': 'Mifumo WMS Production'
            }
        )
        
        if created:
            print(f"✅ Created site: {site.domain}")
        else:
            print(f"ℹ️  Site already exists: {site.domain}")
            
        return True
    except Exception as e:
        print(f"❌ Failed to create site: {e}")
        return False

def create_superuser():
    """Create superuser if none exists"""
    print("\n👤 Checking for superuser...")
    try:
        if not User.objects.filter(is_superuser=True).exists():
            print("Creating superuser...")
            call_command('createsuperuser', interactive=False, 
                        username='admin', email='admin@mifumo.com')
            print("✅ Superuser created successfully")
        else:
            print("ℹ️  Superuser already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False

def test_admin_access():
    """Test if admin is accessible"""
    print("\n🔍 Testing admin access...")
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        response = client.get('/admin/login/')
        
        if response.status_code == 200:
            print("✅ Admin login page accessible")
            return True
        else:
            print(f"❌ Admin login page returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin access test failed: {e}")
        return False

def main():
    print("🔧 Production Database Fix Tool")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        return
    
    # Check missing tables
    missing_tables = check_missing_tables()
    
    if missing_tables:
        print(f"\n🔄 Found {len(missing_tables)} missing tables. Running migrations...")
        if not run_migrations():
            print("❌ Migration failed. Please check your database configuration.")
            return
    else:
        print("✅ All required tables exist")
    
    # Create site data
    create_site_data()
    
    # Create superuser
    create_superuser()
    
    # Test admin access
    test_admin_access()
    
    print("\n" + "=" * 50)
    print("🎉 Database fix completed!")
    print("\nNext steps:")
    print("1. Restart your Django server")
    print("2. Try accessing /admin/login/ again")
    print("3. Login with your superuser credentials")

if __name__ == "__main__":
    main()
