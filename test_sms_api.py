#!/usr/bin/env python3
"""
Test SMS API Endpoints
Test SMS functionality through API endpoints
"""

import os
import sys
import django
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

def test_sms_api():
    print("🌐 Testing SMS API Endpoints")
    print("=" * 40)
    
    client = Client()
    
    # Get superuser for authentication
    superuser = User.objects.filter(is_superuser=True).first()
    if not superuser:
        print("❌ No superuser found!")
        return
    
    # Login
    client.force_login(superuser)
    
    # Test SMS send endpoint
    print("📤 Testing SMS send endpoint...")
    
    sms_data = {
        'recipient_number': '+255614853618',  # Replace with real number
        'message': 'Hello from Mifumo WMS API! This is a test message.',
        'sender_id': 'MIFUMO',
    }
    
    response = client.post('/api/messaging/sms/send/', 
                          data=json.dumps(sms_data),
                          content_type='application/json')
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SMS sent successfully!")
        print(f"   Response: {result}")
    else:
        print(f"❌ SMS send failed: {response.status_code}")
        print(f"   Response: {response.content.decode()}")
    
    # Test other endpoints
    print("\n📋 Testing other SMS endpoints...")
    
    endpoints = [
        '/api/messaging/sms/providers/',
        '/api/messaging/sms/sender-ids/',
        '/api/messaging/sms/templates/',
        '/api/messaging/sms/messages/',
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {endpoint}: {response.status_code}")

def main():
    print("🧪 SMS API Test")
    print("=" * 30)
    
    test_sms_api()
    
    print("\n💡 To test with a real phone number:")
    print("1. Update the recipient_number in the script")
    print("2. Make sure the number is in international format")
    print("3. Run the script again")

if __name__ == "__main__":
    main()
