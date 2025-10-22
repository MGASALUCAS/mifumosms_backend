#!/usr/bin/env python3
"""
Live Server API Test - Sender ID Endpoints
Test the sender ID API endpoints directly on your live server
"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()

def test_api_with_django_client():
    """Test API endpoints using Django test client."""
    print("🧪 Testing Sender ID APIs with Django Test Client")
    print("=" * 60)
    
    # Get a user with a tenant
    user_with_tenant = User.objects.filter(tenant__isnull=False).first()
    if not user_with_tenant:
        print("❌ No users with tenants found")
        return False
    
    print(f"Testing with user: {user_with_tenant.email}")
    print(f"Tenant: {user_with_tenant.tenant.name}")
    
    # Create test client
    client = Client()
    
    # Login the user
    login_success = client.force_login(user_with_tenant)
    print(f"Login successful: {login_success}")
    
    # Test endpoints
    endpoints = [
        ('/api/messaging/sender-ids/', 'Sender IDs List'),
        ('/api/messaging/sender-requests/available/', 'Available Sender IDs'),
        ('/api/messaging/sender-requests/default/overview/', 'Default Sender Overview'),
        ('/api/messaging/sender-requests/status/', 'Sender Request Status'),
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        print(f"\n--- Testing {name} ---")
        print(f"Endpoint: {endpoint}")
        
        try:
            response = client.get(endpoint)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success: {name}")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    results[name] = {'status': 'success', 'data': data}
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    print(f"Response: {response.content}")
                    results[name] = {'status': 'error', 'error': 'Invalid JSON'}
            else:
                print(f"❌ Error: {name}")
                print(f"Response: {response.content}")
                results[name] = {'status': 'error', 'code': response.status_code}
                
        except Exception as e:
            print(f"❌ Exception: {name}")
            print(f"Error: {e}")
            results[name] = {'status': 'exception', 'error': str(e)}
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    success_count = 0
    for name, result in results.items():
        status = result['status']
        if status == 'success':
            print(f"✅ {name}: SUCCESS")
            success_count += 1
        else:
            print(f"❌ {name}: FAILED ({status})")
    
    print(f"\nSuccess Rate: {success_count}/{len(endpoints)} ({success_count/len(endpoints)*100:.1f}%)")
    
    return success_count == len(endpoints)

def test_with_real_requests():
    """Test API endpoints with real HTTP requests."""
    print("\n🌐 Testing Sender ID APIs with Real HTTP Requests")
    print("=" * 60)
    
    # You'll need to replace these with actual values from your live server
    BASE_URL = "https://your-domain.com/api"  # Replace with your actual domain
    TEST_EMAIL = "your-test-user@example.com"  # Replace with actual test user
    TEST_PASSWORD = "your-test-password"       # Replace with actual password
    
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_EMAIL}")
    
    # Create session
    session = requests.Session()
    
    # Login
    print("\n1. Authenticating...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = session.post(f"{BASE_URL}/accounts/login/", json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            if access_token:
                session.headers.update({
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                })
                print("✅ Authentication successful")
            else:
                print("❌ No access token in response")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return False
    
    # Test endpoints
    endpoints = [
        ('/messaging/sender-ids/', 'Sender IDs List'),
        ('/messaging/sender-requests/available/', 'Available Sender IDs'),
        ('/messaging/sender-requests/default/overview/', 'Default Sender Overview'),
        ('/messaging/sender-requests/status/', 'Sender Request Status'),
    ]
    
    results = {}
    
    for endpoint, name in endpoints:
        print(f"\n--- Testing {name} ---")
        print(f"URL: {BASE_URL}{endpoint}")
        
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Success: {name}")
                    print(f"Response: {json.dumps(data, indent=2)}")
                    results[name] = {'status': 'success', 'data': data}
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    print(f"Response: {response.text}")
                    results[name] = {'status': 'error', 'error': 'Invalid JSON'}
            else:
                print(f"❌ Error: {name}")
                print(f"Response: {response.text}")
                results[name] = {'status': 'error', 'code': response.status_code}
                
        except Exception as e:
            print(f"❌ Exception: {name}")
            print(f"Error: {e}")
            results[name] = {'status': 'exception', 'error': str(e)}
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 HTTP Test Results Summary:")
    print("=" * 60)
    
    success_count = 0
    for name, result in results.items():
        status = result['status']
        if status == 'success':
            print(f"✅ {name}: SUCCESS")
            success_count += 1
        else:
            print(f"❌ {name}: FAILED ({status})")
    
    print(f"\nSuccess Rate: {success_count}/{len(endpoints)} ({success_count/len(endpoints)*100:.1f}%)")
    
    return success_count == len(endpoints)

if __name__ == "__main__":
    print("🚀 Live Server Sender ID API Testing")
    print("=" * 60)
    
    # Test with Django client (no HTTP needed)
    django_success = test_api_with_django_client()
    
    # Test with real HTTP requests (requires server to be running)
    print("\n" + "=" * 60)
    print("⚠️  To test with real HTTP requests:")
    print("1. Update BASE_URL, TEST_EMAIL, and TEST_PASSWORD in the script")
    print("2. Make sure your live server is running")
    print("3. Uncomment the line below to run HTTP tests")
    print("=" * 60)
    
    # Uncomment this line to test with real HTTP requests
    # http_success = test_with_real_requests()
    
    print("\n🎯 Next Steps:")
    print("1. Run this script on your live server")
    print("2. Check the output for any errors")
    print("3. Verify sender IDs are being returned correctly")
    print("4. Check frontend API calls match the working endpoints")
