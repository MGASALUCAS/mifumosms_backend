#!/usr/bin/env python3
"""
Fix Static Files for Production
This script collects static files and fixes serving issues
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
from django.contrib.staticfiles.finders import get_finders

def check_static_settings():
    """Check current static file settings"""
    print("=== Static File Settings ===")
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print(f"STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    print()

def collect_static_files():
    """Collect all static files"""
    print("🔄 Collecting static files...")
    try:
        call_command('collectstatic', '--noinput', '--clear', verbosity=2)
        print("✅ Static files collected successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to collect static files: {e}")
        return False

def check_static_files_exist():
    """Check if static files exist in STATIC_ROOT"""
    static_root = Path(settings.STATIC_ROOT)
    if not static_root.exists():
        print(f"❌ STATIC_ROOT directory doesn't exist: {static_root}")
        return False
    
    # Check for drf-yasg static files
    drf_yasg_css = static_root / 'drf-yasg' / 'style.css'
    drf_yasg_js = static_root / 'drf-yasg' / 'swagger-ui-dist' / 'swagger-ui.css'
    
    print(f"📁 STATIC_ROOT: {static_root}")
    print(f"📄 drf-yasg/style.css exists: {drf_yasg_css.exists()}")
    print(f"📄 drf-yasg/swagger-ui-dist/swagger-ui.css exists: {drf_yasg_js.exists()}")
    
    # List some files in static root
    if static_root.exists():
        files = list(static_root.rglob('*.css'))[:5]  # First 5 CSS files
        print(f"📋 Sample CSS files: {[f.name for f in files]}")
    
    return drf_yasg_css.exists() and drf_yasg_js.exists()

def test_static_serving():
    """Test if static files are being served correctly"""
    print("\n🔍 Testing static file serving...")
    try:
        from django.test import Client
        client = Client()
        
        # Test a static file
        response = client.get('/static/drf-yasg/style.css')
        print(f"Static file response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Static files are being served correctly")
            return True
        else:
            print("❌ Static files are not being served correctly")
            return False
    except Exception as e:
        print(f"❌ Static file test failed: {e}")
        return False

def main():
    print("🔧 Static Files Fix Tool")
    print("=" * 40)
    
    # Check current settings
    check_static_settings()
    
    # Collect static files
    if not collect_static_files():
        print("❌ Cannot proceed without collecting static files")
        return
    
    # Check if files exist
    if not check_static_files_exist():
        print("❌ Static files are missing after collection")
        return
    
    # Test static serving
    test_static_serving()
    
    print("\n" + "=" * 40)
    print("🎉 Static files fix completed!")
    print("\nIf static files are still not working:")
    print("1. Check your web server configuration (nginx/apache)")
    print("2. Ensure STATIC_URL and STATIC_ROOT are correct")
    print("3. Make sure your web server serves files from STATIC_ROOT")

if __name__ == "__main__":
    main()
