#!/usr/bin/env python
"""
Simple test for sender-requests endpoint
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from messaging.models_sender_requests import SenderIDRequest
from messaging.views_sender_requests import SenderIDRequestListCreateView
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

def test_sender_requests_view():
    """Test the sender-requests view directly"""
    
    # Get test user
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
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/api/messaging/sender-requests/?page=1&page_size=10')
    request.user = user
    request.tenant = tenant  # Manually set tenant for testing
    
    # Test the view
    view = SenderIDRequestListCreateView()
    view.request = request
    
    try:
        queryset = view.get_queryset()
        print(f"Queryset count: {queryset.count()}")
        
        # Test pagination
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        print(f"Paginated queryset count: {len(paginated_queryset) if paginated_queryset else 0}")
        
        # Test serializer
        serializer_class = view.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        data = serializer.data
        
        print(f"Serialized data count: {len(data)}")
        for item in data:
            print(f"  - {item.get('requested_sender_id')} - {item.get('status')}")
            
    except Exception as e:
        print(f"Error testing view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sender_requests_view()
