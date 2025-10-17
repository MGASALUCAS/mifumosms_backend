#!/usr/bin/env python3
"""
Fix Static Files for Local Development
This script fixes static file serving in local development
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

from django.core.management import call_command
from django.conf import settings
from django.test import Client

def check_local_settings():
    """Check local development settings"""
    print("=== Local Development Settings ===")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    print()

def collect_static_files():
    """Collect static files for local development"""
    print("🔄 Collecting static files...")
    try:
        call_command('collectstatic', '--noinput', verbosity=1)
        print("✅ Static files collected")
        return True
    except Exception as e:
        print(f"❌ Failed to collect static files: {e}")
        return False

def test_static_serving():
    """Test static file serving in local development"""
    print("\n🔍 Testing static file serving...")
    try:
        client = Client()
        
        # Test drf-yasg static files
        test_urls = [
            '/static/drf-yasg/style.css',
            '/static/drf-yasg/swagger-ui-dist/swagger-ui.css',
            '/static/drf-yasg/swagger-ui-init.js'
        ]
        
        for url in test_urls:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {url}: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Static file test failed: {e}")
        return False

def test_admin_access():
    """Test admin access in local development"""
    print("\n🔍 Testing admin access...")
    try:
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
    print("🔧 Local Development Static Files Fix")
    print("=" * 45)
    
    # Check settings
    check_local_settings()
    
    # Collect static files
    collect_static_files()
    
    # Test static serving
    test_static_serving()
    
    # Test admin access
    test_admin_access()
    
    print("\n" + "=" * 45)
    print("🎉 Local development fix completed!")
    print("\nIf static files are still not working:")
    print("1. Make sure you're running with DEBUG=True")
    print("2. Check that STATICFILES_DIRS includes your static directories")
    print("3. Restart your Django development server")
    print("4. Try accessing: http://127.0.0.1:8000/admin/login/")

if __name__ == "__main__":
    main()
