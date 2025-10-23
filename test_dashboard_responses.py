#!/usr/bin/env python3
"""
Test script to capture exact JSON responses from dashboard endpoints for frontend integration
"""
import requests
import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_admin_token():
    """Get JWT token for admin user"""
    try:
        user = User.objects.get(email='admin@mifumo.com')
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return access_token
    except Exception as e:
        print(f"Error getting admin token: {e}")
        return None

def test_endpoint(url, token, endpoint_name):
    """Test a single endpoint and return the JSON response"""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n{'='*80}")
        print(f"ENDPOINT: {endpoint_name}")
        print(f"URL: {url}")
        print(f"STATUS: {response.status_code}")
        print(f"{'='*80}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return data
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    """Test all dashboard endpoints and capture responses"""
    print("Dashboard API JSON Responses for Frontend Integration")
    print("="*80)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("Failed to get admin token. Exiting.")
        return
    
    base_url = "http://127.0.0.1:8001"
    
    # Test all dashboard endpoints
    endpoints = [
        {
            'url': f"{base_url}/api/messaging/dashboard/metrics/",
            'name': 'Dashboard Metrics - Main Cards Data'
        },
        {
            'url': f"{base_url}/api/messaging/dashboard/overview/",
            'name': 'Dashboard Overview - Complete Dashboard Data'
        },
        {
            'url': f"{base_url}/api/messaging/dashboard/comprehensive/",
            'name': 'Dashboard Comprehensive - All Metrics Combined'
        },
        {
            'url': f"{base_url}/api/messaging/activity/recent/",
            'name': 'Recent Activity - Activity Feed'
        },
        {
            'url': f"{base_url}/api/messaging/campaigns/summary/",
            'name': 'Campaigns Summary - Recent Campaigns'
        }
    ]
    
    responses = {}
    
    for endpoint in endpoints:
        response_data = test_endpoint(endpoint['url'], token, endpoint['name'])
        if response_data:
            responses[endpoint['name']] = response_data
    
    # Save all responses to a JSON file
    with open('dashboard_api_responses.json', 'w') as f:
        json.dump(responses, f, indent=2)
    
    print(f"\n{'='*80}")
    print("All responses saved to: dashboard_api_responses.json")
    print("Use this file for frontend integration reference")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
