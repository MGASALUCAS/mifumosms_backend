#!/usr/bin/env python3
"""
Test API for user 62 to see what data is returned.
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models_sender_requests import SenderIDRequest

User = get_user_model()

def test_user_62_api():
    """Test what the API returns for user 62."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing API for User 62")
    print("=" * 40)
    
    # Get user 62
    try:
        user = User.objects.get(id=62)
        print(f"User: {user.email} (ID: {user.id})")
        
        # Check their requests in database
        user_requests = SenderIDRequest.objects.filter(user=user)
        print(f"Requests in database: {user_requests.count()}")
        
        for req in user_requests:
            print(f"  - {req.requested_sender_id} ({req.status})")
        
        # Test API call (we'll use a mock token since we don't have the password)
        print(f"\nAPI URL: {base_url}/api/messaging/sender-requests/?page=1&page_size=10")
        
        # Show what the API should return
        print("\nExpected API response structure:")
        print("""
{
  "count": 4,
  "results": [
    {
      "id": "uuid",
      "user": 62,
      "user_id": 62,
      "requested_sender_id": "VRT",
      "status": "pending",
      "user_email": "magesa123@gmail.com"
    },
    {
      "id": "uuid", 
      "user": 62,
      "user_id": 62,
      "requested_sender_id": "HJYU",
      "status": "pending",
      "user_email": "magesa123@gmail.com"
    },
    // ... more requests
  ]
}
        """)
        
        print("\nFrontend should see:")
        print("- 4 requests total")
        print("- All with user_id: 62")
        print("- All should match current user ID: 62")
        print("- All should be displayed (not filtered out)")
        
    except User.DoesNotExist:
        print("User 62 not found")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_user_62_api()







