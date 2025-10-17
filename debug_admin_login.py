#!/usr/bin/env python3
"""
Debug Admin Login Issues
This script helps debug why admin login is refreshing instead of working
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

from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import call_command

User = get_user_model()

def check_admin_user():
    """Check if admin user exists and can login"""
    print("=== Admin User Check ===")
    try:
        # Check if superuser exists
        superusers = User.objects.filter(is_superuser=True)
        print(f"Number of superusers: {superusers.count()}")
        
        if superusers.exists():
            for user in superusers:
                print(f"Superuser: {user.email} (Active: {user.is_active})")
        else:
            print("❌ No superusers found!")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        return False

def test_admin_login():
    """Test admin login process"""
    print("\n=== Testing Admin Login ===")
    try:
        client = Client()
        
        # First, get the login page to get CSRF token
        print("1. Getting login page...")
        response = client.get('/admin/login/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Login page not accessible")
            return False
        
        # Extract CSRF token
        csrf_token = None
        if 'csrfmiddlewaretoken' in response.content.decode():
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.content.decode())
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   CSRF token found: {csrf_token[:20]}...")
            else:
                print("❌ CSRF token not found in form")
        else:
            print("❌ CSRF token not present")
        
        # Try to login
        print("2. Attempting login...")
        login_data = {
            'username': 'admin@mifumo.com',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_token,
        }
        
        response = client.post('/admin/login/', data=login_data, follow=True)
        print(f"   Login response status: {response.status_code}")
        print(f"   Redirected to: {response.url}")
        
        # Check if we're logged in
        if response.status_code == 200 and '/admin/' in response.url:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed")
            print(f"   Response content preview: {response.content.decode()[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def check_csrf_settings():
    """Check CSRF settings"""
    print("\n=== CSRF Settings Check ===")
    from django.conf import settings
    
    print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
    print(f"CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
    print(f"CSRF_COOKIE_SAMESITE: {settings.CSRF_COOKIE_SAMESITE}")
    print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    print(f"SESSION_COOKIE_SAMESITE: {settings.SESSION_COOKIE_SAMESITE}")

def check_site_settings():
    """Check site settings"""
    print("\n=== Site Settings Check ===")
    try:
        site = Site.objects.get_current()
        print(f"Current site: {site.domain} (ID: {site.id})")
        
        # Check if site domain matches your server
        if '104.131.116.55' not in site.domain:
            print("⚠️  Site domain doesn't match your server IP")
            print("   Consider updating site domain to include your server IP")
    except Exception as e:
        print(f"❌ Error checking site: {e}")

def create_test_admin():
    """Create a test admin user if needed"""
    print("\n=== Creating Test Admin ===")
    try:
        if not User.objects.filter(is_superuser=True).exists():
            print("Creating test admin user...")
            User.objects.create_superuser(
                email='admin@mifumo.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            print("✅ Test admin created: admin@mifumo.com / admin123")
        else:
            print("ℹ️  Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")

def main():
    print("🔍 Admin Login Debug Tool")
    print("=" * 40)
    
    # Check admin user
    check_admin_user()
    
    # Check CSRF settings
    check_csrf_settings()
    
    # Check site settings
    check_site_settings()
    
    # Create test admin if needed
    create_test_admin()
    
    # Test login
    test_admin_login()
    
    print("\n" + "=" * 40)
    print("🎯 Debug completed!")
    print("\nIf login is still not working:")
    print("1. Check browser developer tools for JavaScript errors")
    print("2. Check browser network tab for failed requests")
    print("3. Try clearing browser cookies and cache")
    print("4. Check if you're using the correct URL: http://104.131.116.55:8000/admin/login/")

if __name__ == "__main__":
    main()
