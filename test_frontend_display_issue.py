#!/usr/bin/env python3
"""
Test to verify API is returning data correctly for frontend display.
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from billing.models import SMSBalance
from messaging.models_sender_requests import SenderIDRequest

User = get_user_model()

def test_frontend_display_issue():
    """Test to verify API returns data for frontend display."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Frontend Display Issue")
    print("=" * 50)
    
    # Check existing data in database
    print("\n1. Checking database for existing requests...")
    all_requests = SenderIDRequest.objects.all()
    print(f"   Total requests in database: {all_requests.count()}")
    
    for req in all_requests:
        print(f"   - ID: {req.id}")
        print(f"     Sender ID: {req.requested_sender_id}")
        print(f"     User: {req.user.email} (ID: {req.user.id})")
        print(f"     Tenant: {req.tenant.name}")
        print(f"     Status: {req.status}")
        print(f"     Created: {req.created_at}")
        print()
    
    # Test with a specific user
    print("\n2. Testing API with user ID 62 (from your logs)...")
    
    # Find user with ID 62
    try:
        user = User.objects.get(id=62)
        print(f"   Found user: {user.email} (ID: {user.id})")
        
        # Get authentication token for this user
        auth_url = f"{base_url}/api/auth/login/"
        auth_data = {
            "email": user.email,
            "password": "testpassword123"  # You might need to set this
        }
        
        try:
            auth_response = requests.post(auth_url, json=auth_data)
            if auth_response.status_code == 200:
                auth_result = auth_response.json()
                if 'tokens' in auth_result:
                    token = auth_result['tokens']['access']
                    print(f"   Token obtained: {token[:20]}...")
                    
                    headers = {
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                    
                    # Test API call
                    print("\n3. Testing API call...")
                    response = requests.get(f"{base_url}/api/messaging/sender-requests/?page=1&page_size=10", headers=headers)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   Response: {json.dumps(data, indent=2)}")
                        
                        if 'results' in data:
                            results = data['results']
                            print(f"\n4. API returned {len(results)} requests:")
                            
                            for i, req in enumerate(results):
                                print(f"   Request {i+1}:")
                                print(f"     ID: {req.get('id', 'N/A')}")
                                print(f"     Sender ID: {req.get('requested_sender_id', 'N/A')}")
                                print(f"     User: {req.get('user', 'N/A')}")
                                print(f"     User ID: {req.get('user_id', 'N/A')}")
                                print(f"     User Email: {req.get('user_email', 'N/A')}")
                                print(f"     Status: {req.get('status', 'N/A')}")
                                print(f"     Created: {req.get('created_at', 'N/A')}")
                                print()
                            
                            # Test filtering logic
                            print("5. Testing frontend filtering logic...")
                            current_user_id = 62
                            
                            for req in results:
                                request_user_id = req.get('user_id') or req.get('user')
                                print(f"   Request user ID: {request_user_id}")
                                print(f"   Current user ID: {current_user_id}")
                                print(f"   Match: {request_user_id == current_user_id}")
                                print()
                        else:
                            print("   No results in response")
                    else:
                        print(f"   API call failed: {response.text}")
                else:
                    print(f"   Auth failed: {auth_result}")
            else:
                print(f"   Auth failed with status: {auth_response.status_code}")
                print(f"   Response: {auth_response.text}")
        except Exception as e:
            print(f"   Auth error: {e}")
    except User.DoesNotExist:
        print("   User with ID 62 not found")
    
    print("\n6. Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_frontend_display_issue()




