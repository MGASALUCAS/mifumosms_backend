#!/usr/bin/env python
"""
Test script to verify SMS API functionality.
"""

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership

User = get_user_model()

def get_auth_token():
    """Get JWT token for API authentication."""
    try:
        # Get admin user
        user = User.objects.get(email='admin2@mifumo.com')
        
        # Login to get token
        login_data = {
            'email': 'admin2@mifumo.com',
            'password': 'admin123'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting auth token: {str(e)}")
        return None

def test_sms_send():
    """Test SMS sending via API."""
    try:
        # Get auth token
        token = get_auth_token()
        if not token:
            return False
        
        # Prepare SMS data
        sms_data = {
            "message": "Hello mgasa Mifumo WMS! This is a test message, debugging.",
            "recipients": ["255689726060"],
            "sender_id": "Taarifa-SMS"
        }
        
        # Send SMS
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/messaging/sms/sms/beem/send/',
            json=sms_data,
            headers=headers
        )
        
        print(f"📱 SMS API Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ SMS sent successfully!")
            return True
        else:
            print("❌ SMS sending failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SMS: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing SMS API...")
    print("=" * 50)
    
    success = test_sms_send()
    
    if success:
        print("\n🎉 SMS API test completed successfully!")
    else:
        print("\n❌ SMS API test failed!")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
