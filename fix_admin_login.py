#!/usr/bin/env python3
"""
Fix Admin Login Issues
This script fixes the admin login problems
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

from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

def fix_site_domain():
    """Fix the site domain to match your server"""
    print("🌐 Fixing site domain...")
    try:
        site = Site.objects.get(id=1)
        old_domain = site.domain
        site.domain = '104.131.116.55:8000'
        site.name = 'Mifumo WMS Production'
        site.save()
        print(f"✅ Site domain updated: {old_domain} → {site.domain}")
        return True
    except Exception as e:
        print(f"❌ Failed to update site domain: {e}")
        return False

def test_admin_login():
    """Test admin login with proper settings"""
    print("\n🔍 Testing admin login...")
    try:
        client = Client()
        
        # Test with proper host header
        response = client.get('/admin/login/', HTTP_HOST='104.131.116.55:8000')
        print(f"Login page status: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Login page not accessible")
            return False
        
        # Get CSRF token
        csrf_token = None
        content = response.content.decode()
        if 'csrfmiddlewaretoken' in content:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF token found: {csrf_token[:20]}...")
            else:
                print("❌ CSRF token not found in form")
                return False
        else:
            print("❌ CSRF token not present")
            return False
        
        # Try to login
        print("🔐 Attempting login...")
        login_data = {
            'username': 'admin@mifumo.com',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_token,
        }
        
        response = client.post('/admin/login/', data=login_data, 
                             HTTP_HOST='104.131.116.55:8000', follow=True)
        
        print(f"Login response status: {response.status_code}")
        print(f"Redirected to: {response.url}")
        
        if response.status_code == 200 and '/admin/' in response.url:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed")
            # Check for error messages
            if 'error' in content.lower() or 'invalid' in content.lower():
                print("   Error messages found in response")
            return False
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def check_cookie_settings():
    """Check current cookie settings"""
    print("\n🍪 Checking cookie settings...")
    from django.conf import settings
    
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
    print(f"CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
    
    if settings.SESSION_COOKIE_SECURE or settings.CSRF_COOKIE_SECURE:
        print("⚠️  SECURE cookies are enabled - this will cause issues with HTTP")
        print("   Make sure SESSION_COOKIE_SECURE=False and CSRF_COOKIE_SECURE=False")
    else:
        print("✅ Cookie settings are correct for HTTP")

def main():
    print("🔧 Admin Login Fix Tool")
    print("=" * 40)
    
    # Fix site domain
    fix_site_domain()
    
    # Check cookie settings
    check_cookie_settings()
    
    # Test admin login
    test_admin_login()
    
    print("\n" + "=" * 40)
    print("🎉 Admin login fix completed!")
    print("\nNext steps:")
    print("1. Restart your Django server")
    print("2. Clear browser cookies and cache")
    print("3. Try logging in at: http://104.131.116.55:8000/admin/login/")
    print("4. Use credentials: admin@mifumo.com / admin123")

if __name__ == "__main__":
    main()
