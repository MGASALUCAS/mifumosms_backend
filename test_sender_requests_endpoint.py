#!/usr/bin/env python
"""
Test script for sender-requests endpoint
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from tenants.models import Tenant, Membership
from messaging.models_sender_requests import SenderIDRequest
import json

User = get_user_model()

def test_sender_requests_endpoint():
    """Test the sender-requests endpoint with pagination"""
    
    # Get or create test user
    user = User.objects.filter(email="normaluser@test.com").first()
    if not user:
        print("Test user not found. Please run test_normal_user_sms.py first.")
        return
    
    print(f"Using test user: {user.email}")
    
    # Get tenant
    tenant = user.tenant
    if not tenant:
        print("User has no tenant")
        return
    
    print(f"Using tenant: {tenant.name}")
    
    # Create some test sender ID requests
    for i in range(5):
        SenderIDRequest.objects.get_or_create(
            tenant=tenant,
            requested_sender_id=f'TEST{i}',
            defaults={
                'user': user,
                'request_type': 'custom',
                'sample_content': f'Test content {i}',
                'business_justification': f'Test justification {i}',
                'status': 'pending'
            }
        )
    
    print(f"Created test sender ID requests")
    
    # Test the endpoint
    client = Client()
    client.force_login(user)
    
    # Test with pagination
    response = client.get('/api/messaging/sender-requests/?page=1&page_size=10')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.content.decode()}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        print(f"Success! Found {len(data)} sender ID requests")
        for request in data:
            print(f"  - {request.get('requested_sender_id')} - {request.get('status')}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_sender_requests_endpoint()
