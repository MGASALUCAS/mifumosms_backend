#!/usr/bin/env python3
"""
Test Templates API Endpoints
Tests template functionality with authentication
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

def get_admin_user_and_token():
    """Get admin user and generate JWT token."""
    try:
        user = User.objects.get(email='admin@mifumo.com')
        refresh = RefreshToken.for_user(user)
        return user, str(refresh.access_token)
    except User.DoesNotExist:
        print("Admin user not found. Please create admin@mifumo.com user first.")
        return None, None

def test_templates_list():
    """Test templates list endpoint."""
    print("=" * 80)
    print("TESTING TEMPLATES LIST")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/templates/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_template_create():
    """Test template creation endpoint."""
    print("\n" + "=" * 80)
    print("TESTING TEMPLATE CREATE")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = "http://127.0.0.1:8001/api/messaging/templates/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test template data
    template_data = {
        "name": "Test Welcome Template with Variables",
        "body_text": "Hello {{name}}, welcome to our service! Your order {{order_id}} is ready.",
        "category": "onboarding",
        "language": "en",
        "channel": "sms",
        "description": "A welcome template with variables for personalization"
    }
    
    try:
        response = requests.post(url, json=template_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_template_detail(template_id):
    """Test template detail endpoint."""
    print("\n" + "=" * 80)
    print("TESTING TEMPLATE DETAIL")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = f"http://127.0.0.1:8001/api/messaging/templates/{template_id}/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_template_favorite_toggle(template_id):
    """Test template favorite toggle endpoint."""
    print("\n" + "=" * 80)
    print("TESTING TEMPLATE FAVORITE TOGGLE")
    print("=" * 80)
    
    user, token = get_admin_user_and_token()
    if not user or not token:
        return
    
    url = f"http://127.0.0.1:8001/api/messaging/templates/{template_id}/toggle-favorite/"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Run all template tests."""
    print("Testing Templates API Endpoints")
    print("=" * 80)
    
    # Test templates list
    templates_result = test_templates_list()
    
    # Test template creation
    create_result = test_template_create()
    
    # If template was created, test detail and favorite toggle
    if create_result and 'id' in create_result:
        template_id = create_result['id']
        test_template_detail(template_id)
        test_template_favorite_toggle(template_id)
    
    # Save results
    results = {
        "templates_list": templates_result,
        "template_create": create_result
    }
    
    with open("templates_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print("All test results saved to: templates_test_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
