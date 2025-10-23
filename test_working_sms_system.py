#!/usr/bin/env python3
"""
Test the working SMS system to see what sender IDs work
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.models import SMSProvider, SMSSenderID, Tenant
from messaging.services.sms_service import SMSService

def test_working_sms_system():
    """Test the working SMS system to see what sender IDs work."""
    print("=" * 80)
    print("TESTING WORKING SMS SYSTEM")
    print("=" * 80)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("No tenant found!")
        return
    
    print(f"Using tenant: {tenant.name} (ID: {tenant.id})")
    
    # Get SMS providers
    providers = SMSProvider.objects.filter(tenant=tenant, is_active=True)
    print(f"Active SMS providers: {providers.count()}")
    
    for provider in providers:
        print(f"  - {provider.name} ({provider.provider_type}) - Default: {provider.is_default}")
    
    # Get sender IDs
    sender_ids = SMSSenderID.objects.filter(tenant=tenant, status='active')
    print(f"Active sender IDs: {sender_ids.count()}")
    
    for sender_id in sender_ids:
        print(f"  - {sender_id.sender_id} (Status: {sender_id.status})")
    
    # Test SMS service
    try:
        sms_service = SMSService(str(tenant.id))
        print("\nSMS Service initialized successfully")
        
        # Test with first available sender ID
        if sender_ids.exists():
            test_sender_id = sender_ids.first().sender_id
            print(f"Testing with sender ID: {test_sender_id}")
            
            result = sms_service.send_sms(
                to="255700000001",
                message="Test message from working SMS system",
                sender_id=test_sender_id,
                recipient_id="test_working_system"
            )
            
            print(f"SMS send result: {result}")
            
        else:
            print("No sender IDs available for testing")
            
    except Exception as e:
        print(f"SMS Service error: {e}")
        import traceback
        traceback.print_exc()

def test_direct_beem_api():
    """Test direct Beem API with different sender IDs."""
    print("\n" + "=" * 80)
    print("TESTING DIRECT BEEM API WITH DIFFERENT SENDER IDS")
    print("=" * 80)
    
    import requests
    import base64
    from django.conf import settings
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Test with different sender IDs
    sender_ids_to_test = ["Quantum", "Taarifa-SMS", "INFO", "MIFUMO"]
    
    for sender_id in sender_ids_to_test:
        print(f"\nTesting with sender ID: {sender_id}")
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        # Prepare request data
        data = {
            "source_addr": sender_id,
            "message": f"Test message with {sender_id}",
            "encoding": 0,
            "recipients": [{
                "recipient_id": f"test_{sender_id.lower()}",
                "dest_addr": "255700000001"
            }]
        }
        
        try:
            response = requests.post(
                "https://apisms.beem.africa/v1/send",
                json=data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            
            if response.status_code == 200:
                print(f"  SUCCESS: {sender_id} works!")
                break
            else:
                print(f"  FAILED: {sender_id} - {response.json().get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ERROR: {e}")

def main():
    """Run all tests."""
    print("Testing Working SMS System")
    print("=" * 80)
    
    test_working_sms_system()
    test_direct_beem_api()

if __name__ == "__main__":
    main()
