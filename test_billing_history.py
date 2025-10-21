#!/usr/bin/env python3
"""
Test script for billing history endpoints.
"""
import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, Membership
from billing.models import SMSBalance, Purchase, PaymentTransaction, UsageRecord, SMSPackage
from messaging.models import SMSMessage

User = get_user_model()

def test_billing_history_endpoints():
    """Test all billing history endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing Billing History Endpoints")
    print("=" * 50)
    
    # Test data setup
    print("\n1. Setting up test data...")
    
    # Create test tenant
    tenant, created = Tenant.objects.get_or_create(
        name="Test Billing History Organization",
        defaults={
            'subdomain': 'test-billing-history'
        }
    )
    print(f"   Tenant: {tenant.name} ({'created' if created else 'exists'})")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="test-billing-history@example.com",
        defaults={
            'first_name': 'Test',
            'last_name': 'Billing History User',
            'is_active': True
        }
    )
    
    # Set password for the user
    user.set_password('testpassword123')
    user.save()
    print(f"   User: {user.email} ({'created' if created else 'exists'})")
    
    # Create membership
    membership, created = Membership.objects.get_or_create(
        user=user,
        tenant=tenant,
        defaults={'role': 'admin'}
    )
    print(f"   Membership: {membership.role} ({'created' if created else 'exists'})")
    
    # Create SMS balance
    sms_balance, created = SMSBalance.objects.get_or_create(tenant=tenant)
    print(f"   SMS Balance: {sms_balance.credits} credits ({'created' if created else 'exists'})")
    
    # Create test package
    package, created = SMSPackage.objects.get_or_create(
        name="Test History Package",
        defaults={
            'package_type': 'standard',
            'credits': 1000,
            'price': 25000.00,
            'unit_price': 25.00,
            'is_active': True
        }
    )
    print(f"   Package: {package.name} ({'created' if created else 'exists'})")
    
    # Create test purchases
    purchase, created = Purchase.objects.get_or_create(
        tenant=tenant,
        user=user,
        package=package,
        invoice_number="TEST-INV-001",
        defaults={
            'amount': 25000.00,
            'credits': 1000,
            'unit_price': 25.00,
            'payment_method': 'mpesa',
            'status': 'completed'
        }
    )
    print(f"   Purchase: {purchase.invoice_number} ({'created' if created else 'exists'})")
    
    # Create test payment transaction
    payment, created = PaymentTransaction.objects.get_or_create(
        tenant=tenant,
        user=user,
        order_id="TEST-ORD-001",
        zenopay_order_id="ZP-TEST-001",
        invoice_number="TEST-INV-001",
        defaults={
            'amount': 25000.00,
            'currency': 'TZS',
            'buyer_email': user.email,
            'buyer_name': f"{user.first_name} {user.last_name}",
            'buyer_phone': '0744963858',
            'payment_method': 'mpesa',
            'status': 'completed'
        }
    )
    print(f"   Payment: {payment.order_id} ({'created' if created else 'exists'})")
    
    # Create test usage records
    for i in range(5):
        usage_record, created = UsageRecord.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={
                'credits_used': 1,
                'cost': 25.00
            }
        )
        if created:
            print(f"   Usage Record {i+1}: {usage_record.credits_used} credits")
    
    # Get authentication token
    print("\n2. Getting authentication token...")
    auth_url = f"{base_url}/api/auth/login/"
    auth_data = {
        "email": user.email,
        "password": "testpassword123"  # You may need to set this password
    }
    
    try:
        auth_response = requests.post(auth_url, json=auth_data)
        print(f"   Auth response status: {auth_response.status_code}")
        if auth_response.status_code == 200:
            auth_result = auth_response.json()
            print(f"   Auth response: {auth_result}")
            if 'tokens' in auth_result:
                token = auth_result['tokens']['access']
                print(f"   Token obtained: {token[:20]}...")
            else:
                print(f"   Auth failed: {auth_result.get('message', 'Unknown error')}")
                return
        else:
            print(f"   Auth failed with status: {auth_response.status_code}")
            print(f"   Response: {auth_response.text}")
            return
    except Exception as e:
        print(f"   Auth error: {e}")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test endpoints
    print("\n3. Testing billing history endpoints...")
    
    # Test comprehensive billing history
    print("\n   Testing comprehensive billing history...")
    try:
        response = requests.get(f"{base_url}/api/billing/history/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data['data']['summary']
                print(f"   Total Purchased: {summary['total_purchased']}")
                print(f"   Total Credits: {summary['total_credits_purchased']}")
                print(f"   Current Balance: {summary['current_balance']}")
                print(f"   Purchases Count: {summary['total_purchases']}")
                print(f"   Payments Count: {summary['total_payments']}")
                print(f"   Usage Records Count: {summary['total_usage_records']}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test billing history summary
    print("\n   Testing billing history summary...")
    try:
        response = requests.get(f"{base_url}/api/billing/history/summary/?period=30d", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data['data']['summary']
                charts = data['data']['charts']
                print(f"   Period: {summary['period']}")
                print(f"   Total Purchased: {summary['total_purchased']}")
                print(f"   Monthly Usage Records: {len(charts['monthly_usage'])}")
                print(f"   Payment Methods: {len(charts['payment_methods'])}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test detailed purchase history
    print("\n   Testing detailed purchase history...")
    try:
        response = requests.get(f"{base_url}/api/billing/history/purchases/?page=1&page_size=10", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                purchases = data['data']['purchases']
                pagination = data['data']['pagination']
                print(f"   Purchases Count: {len(purchases)}")
                print(f"   Total Count: {pagination['count']}")
                print(f"   Page: {pagination['page']}")
                print(f"   Page Size: {pagination['page_size']}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test detailed payment history
    print("\n   Testing detailed payment history...")
    try:
        response = requests.get(f"{base_url}/api/billing/history/payments/?page=1&page_size=10", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                transactions = data['data']['transactions']
                pagination = data['data']['pagination']
                print(f"   Transactions Count: {len(transactions)}")
                print(f"   Total Count: {pagination['count']}")
                print(f"   Page: {pagination['page']}")
                print(f"   Page Size: {pagination['page_size']}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test detailed usage history
    print("\n   Testing detailed usage history...")
    try:
        response = requests.get(f"{base_url}/api/billing/history/usage/?page=1&page_size=10", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                usage_records = data['data']['usage_records']
                pagination = data['data']['pagination']
                print(f"   Usage Records Count: {len(usage_records)}")
                print(f"   Total Count: {pagination['count']}")
                print(f"   Page: {pagination['page']}")
                print(f"   Page Size: {pagination['page_size']}")
            else:
                print(f"   Error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test filtering
    print("\n   Testing filtering...")
    try:
        # Test date filtering
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{base_url}/api/billing/history/summary/?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        print(f"   Date Filter Status: {response.status_code}")
        
        # Test status filtering
        response = requests.get(
            f"{base_url}/api/billing/history/purchases/?status=completed",
            headers=headers
        )
        print(f"   Status Filter Status: {response.status_code}")
        
        # Test payment method filtering
        response = requests.get(
            f"{base_url}/api/billing/history/payments/?payment_method=mpesa",
            headers=headers
        )
        print(f"   Payment Method Filter Status: {response.status_code}")
        
    except Exception as e:
        print(f"   Filtering Error: {e}")
    
    print("\n4. Billing history endpoints test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_billing_history_endpoints()
