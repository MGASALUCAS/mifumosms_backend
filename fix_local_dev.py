#!/usr/bin/env python3
"""
Quick Local Development Fix
Run this in your local development environment
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.core.management import call_command
from django.test import Client

def main():
    print("🔧 Local Development Fix")
    print("=" * 30)
    
    try:
        # Collect static files
        print("🔄 Collecting static files...")
        call_command('collectstatic', '--noinput', verbosity=1)
        
        # Test static serving
        print("🔍 Testing static files...")
        client = Client()
        
        test_urls = [
            '/static/drf-yasg/style.css',
            '/static/drf-yasg/swagger-ui-dist/swagger-ui.css',
            '/admin/login/'
        ]
        
        for url in test_urls:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {url}: {response.status_code}")
        
        print("✅ Local development fix completed!")
        print("\nNow restart your Django server:")
        print("python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
