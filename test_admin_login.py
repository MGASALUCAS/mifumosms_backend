#!/usr/bin/env python3
"""
Simple Admin Login Test
Test admin login functionality
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def main():
    print("🔍 Testing Admin Login")
    print("=" * 30)
    
    User = get_user_model()
    client = Client()
    
    # Check if admin exists
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found!")
        return
    
    print(f"✅ Admin user found: {admin.email}")
    
    # Test login
    response = client.post('/admin/login/', {
        'username': admin.email,
        'password': 'admin123',
    })
    
    print(f"Login response: {response.status_code}")
    print(f"Redirected to: {response.url}")
    
    if response.status_code == 302 and '/admin/' in response.url:
        print("✅ Login successful!")
    else:
        print("❌ Login failed")
        print("Response content:", response.content.decode()[:200])

if __name__ == "__main__":
    main()
