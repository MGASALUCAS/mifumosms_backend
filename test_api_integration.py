#!/usr/bin/env python3
"""
Test API integration functionality.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from accounts.models import User
from api_integration.models import APIAccount, APIKey

def test_api_integration():
    """Test the complete API integration flow."""
    print("=" * 60)
    print("TESTING API INTEGRATION")
    print("=" * 60)
    
    # Get a test user
    user = User.objects.filter(email='ivan123@gmail.com').first()
    if not user:
        print("ERROR: Test user not found!")
        return False
    
    print(f"Using user: {user.email}")
    
    # Step 1: Create API Account
    print("\n1. Creating API Account...")
    # Get user's tenant
    tenant = user.get_tenant()
    if not tenant:
        print("ERROR: User has no tenant!")
        return False
    
    api_account, created = APIAccount.objects.get_or_create(
        owner=user,
        defaults={
            'name': f"{user.get_full_name() or user.email}'s API Account",
            'description': 'Test API account',
            'tenant': tenant,
            'rate_limit_per_minute': 60,
            'rate_limit_per_hour': 1000,
            'rate_limit_per_day': 10000,
        }
    )
    print(f"API Account: {api_account.account_id}")
    
    # Step 2: Create API Key
    print("\n2. Creating API Key...")
    api_key = APIKey.objects.create(
        api_account=api_account,
        key_name="Test API Key",
        permissions=['read', 'write']
    )
    api_key.api_key, api_key.secret_key = api_key.generate_keys()
    api_key.save()
    print(f"API Key: {api_key.api_key}")
    
    # Step 3: Test SMS API
    print("\n3. Testing SMS API...")
    base_url = "http://127.0.0.1:8001/api/integration/v1"
    headers = {
        'Authorization': f'Bearer {api_key.api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test send SMS
    sms_data = {
        "message": "Hello from Mifumo SMS API! This is a test message.",
        "recipients": ["+255614853618"],
        "sender_id": "MIFUMO"
    }
    
    try:
        response = requests.post(f"{base_url}/sms/send/", json=sms_data, headers=headers, timeout=30)
        print(f"Send SMS Status: {response.status_code}")
        print(f"Send SMS Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                message_id = result['data']['message_id']
                print(f"Message ID: {message_id}")
                
                # Test get message status
                print("\n4. Testing Message Status...")
                status_response = requests.get(f"{base_url}/sms/status/{message_id}/", headers=headers, timeout=30)
                print(f"Status Response: {status_response.status_code}")
                print(f"Status Data: {status_response.text}")
                
                # Test delivery reports
                print("\n5. Testing Delivery Reports...")
                reports_response = requests.get(f"{base_url}/sms/delivery-reports/", headers=headers, timeout=30)
                print(f"Reports Response: {reports_response.status_code}")
                print(f"Reports Data: {reports_response.text}")
                
                # Test balance
                print("\n6. Testing Balance...")
                balance_response = requests.get(f"{base_url}/sms/balance/", headers=headers, timeout=30)
                print(f"Balance Response: {balance_response.status_code}")
                print(f"Balance Data: {balance_response.text}")
                
                return True
            else:
                print(f"ERROR: SMS send failed: {result.get('message')}")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Request failed: {e}")
    
    return False

def test_api_dashboard():
    """Test API dashboard functionality."""
    print("\n" + "=" * 60)
    print("TESTING API DASHBOARD")
    print("=" * 60)
    
    # Test dashboard access
    try:
        response = requests.get("http://127.0.0.1:8001/api/integration/dashboard/", timeout=30)
        print(f"Dashboard Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Dashboard accessible")
            return True
        else:
            print(f"Dashboard not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Dashboard test failed: {e}")
    
    return False

def test_api_documentation():
    """Test API documentation."""
    print("\n" + "=" * 60)
    print("TESTING API DOCUMENTATION")
    print("=" * 60)
    
    try:
        response = requests.get("http://127.0.0.1:8001/api/integration/documentation/", timeout=30)
        print(f"Documentation Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Documentation accessible")
            return True
        else:
            print(f"Documentation not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Documentation test failed: {e}")
    
    return False

def create_sample_integration():
    """Create a sample integration for demonstration."""
    print("\n" + "=" * 60)
    print("CREATING SAMPLE INTEGRATION")
    print("=" * 60)
    
    # Get user and API account
    user = User.objects.filter(email='ivan123@gmail.com').first()
    if not user:
        print("ERROR: Test user not found!")
        return False
    
    api_account = APIAccount.objects.filter(owner=user).first()
    if not api_account:
        print("ERROR: API account not found!")
        return False
    
    # Create sample webhook
    from api_integration.models import APIIntegration
    
    webhook = APIIntegration.objects.create(
        api_account=api_account,
        name="Sample Webhook",
        platform="custom",
        webhook_url="https://webhook.site/your-webhook-url",
        config={
            'events': ['message.sent', 'message.delivered']
        },
        status='active'
    )
    
    print(f"Created webhook: {webhook.name}")
    print(f"Webhook URL: {webhook.webhook_url}")
    print(f"Events: {webhook.config['events']}")
    
    return True

if __name__ == "__main__":
    print("Starting API Integration Tests...")
    
    # Test 1: API Integration
    api_success = test_api_integration()
    
    # Test 2: Dashboard
    dashboard_success = test_api_dashboard()
    
    # Test 3: Documentation
    docs_success = test_api_documentation()
    
    # Test 4: Sample Integration
    sample_success = create_sample_integration()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"API Integration: {'PASS' if api_success else 'FAIL'}")
    print(f"Dashboard: {'PASS' if dashboard_success else 'FAIL'}")
    print(f"Documentation: {'PASS' if docs_success else 'FAIL'}")
    print(f"Sample Integration: {'PASS' if sample_success else 'FAIL'}")
    
    if all([api_success, dashboard_success, docs_success, sample_success]):
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour API integration system is ready!")
        print("\nNext steps:")
        print("1. Visit http://127.0.0.1:8001/api/integration/dashboard/ to manage API keys")
        print("2. Visit http://127.0.0.1:8001/api/integration/documentation/ for API docs")
        print("3. Use the API endpoints to integrate with your applications")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
