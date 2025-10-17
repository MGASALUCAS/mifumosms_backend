#!/usr/bin/env python3
"""
CSRF Fix for Production Server
This script helps fix CSRF cookie issues in production
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

from django.conf import settings
from django.core.management import execute_from_command_line

def check_csrf_settings():
    """Check current CSRF settings"""
    print("=== Current CSRF Settings ===")
    print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
    print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
    print(f"CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
    print(f"CSRF_COOKIE_SAMESITE: {settings.CSRF_COOKIE_SAMESITE}")
    print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
    print(f"SESSION_COOKIE_SAMESITE: {settings.SESSION_COOKIE_SAMESITE}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print()

def test_csrf_token():
    """Test CSRF token generation"""
    from django.middleware.csrf import get_token
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/admin/login/')
    
    try:
        token = get_token(request)
        print(f"✅ CSRF token generated successfully: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ CSRF token generation failed: {e}")
        return False

def clear_sessions():
    """Clear all sessions to force re-login"""
    try:
        from django.contrib.sessions.models import Session
        count = Session.objects.count()
        Session.objects.all().delete()
        print(f"✅ Cleared {count} sessions")
        return True
    except Exception as e:
        print(f"❌ Failed to clear sessions: {e}")
        return False

def main():
    print("🔧 CSRF Production Fix Tool")
    print("=" * 50)
    
    # Check current settings
    check_csrf_settings()
    
    # Test CSRF token generation
    print("=== Testing CSRF Token Generation ===")
    csrf_ok = test_csrf_token()
    
    # Clear sessions
    print("\n=== Clearing Sessions ===")
    clear_sessions()
    
    print("\n=== Recommendations ===")
    print("1. Make sure your production server IP (196.249.97.239) is in CSRF_TRUSTED_ORIGINS")
    print("2. Ensure SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE are False for HTTP")
    print("3. Set CSRF_COOKIE_HTTPONLY to False to allow JavaScript access")
    print("4. Restart your Django server after making changes")
    print("5. Clear browser cookies and try logging in again")
    
    if csrf_ok:
        print("\n✅ CSRF configuration appears to be working correctly")
    else:
        print("\n❌ CSRF configuration needs attention")

if __name__ == "__main__":
    main()
