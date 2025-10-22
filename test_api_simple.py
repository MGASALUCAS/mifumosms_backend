#!/usr/bin/env python3
"""
Simple API Test Script
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_api():
    # Use DRF APIClient instead of Django Client
    client = APIClient()
    user = User.objects.filter(memberships__isnull=False).first()
    print(f'Testing with user: {user.email}')
    
    # Get user's tenant
    tenant = user.memberships.first().tenant
    print(f'Tenant: {tenant.name}')
    
    # Generate JWT token for authentication
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Test different URL patterns
    urls_to_test = [
        '/api/messaging/sender-ids',
        '/api/messaging/sender-ids/',
        '/api/messaging/sender-requests/available',
        '/api/messaging/sender-requests/available/',
    ]
    
    for url in urls_to_test:
        print(f'\nTesting: {url}')
        # Use the URL with trailing slash directly to avoid redirect issues
        test_url = url if url.endswith('/') else url + '/'
        response = client.get(test_url)
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f'Success: {data.get("success", False)}')
                if 'data' in data:
                    print(f'Data count: {len(data["data"])}')
                    if data["data"]:
                        print(f'First item: {data["data"][0]}')
            except Exception as e:
                print(f'Invalid JSON response: {e}')
        else:
            print(f'Error: {response.content[:100]}')
    
    # Test with live server on port 8001
    print(f'\n🌐 Testing with live server on port 8001...')
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Test live server endpoints
    live_urls = [
        'http://localhost:8001/api/messaging/sender-ids/',
        'http://localhost:8001/api/messaging/sender-requests/available/',
        'http://localhost:8001/api/messaging/sender-requests/default/overview/',
    ]
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    for url in live_urls:
        print(f'\nTesting live server: {url}')
        try:
            # Force HTTP instead of HTTPS
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            print(f'Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'Success: {data.get("success", False)}')
                if 'data' in data:
                    print(f'Data count: {len(data["data"])}')
                    if data["data"]:
                        print(f'First item: {data["data"][0]}')
            else:
                print(f'Error: {response.text[:100]}')
        except Exception as e:
            print(f'Connection error: {e}')

if __name__ == "__main__":
    test_api()
