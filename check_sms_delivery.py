#!/usr/bin/env python3
"""
Check SMS delivery status and test different phone formats.
"""
import requests
import json
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from messaging.services.beem_sms import BeemSMSService

def test_different_phone_formats():
    """Test different phone number formats."""
    print("Testing different phone number formats...")
    
    # Different formats to test
    phone_formats = [
        "255614853618",    # International format (current)
        "+255614853618",   # With + prefix
        "0614853618",      # Local format
        "255614853618",    # International without +
    ]
    
    beem_service = BeemSMSService()
    
    for phone in phone_formats:
        print(f"\n--- Testing phone: {phone} ---")
        
        try:
            result = beem_service.send_sms(
                message=f"Test SMS to {phone} - Please confirm if you receive this",
                recipients=[phone],
                source_addr="Taarifa-SMS"
            )
            
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ SMS sent successfully!")
            else:
                print(f"❌ SMS failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def check_beem_balance():
    """Check Beem account balance."""
    print("\n" + "="*50)
    print("CHECKING BEEM ACCOUNT BALANCE")
    print("="*50)
    
    try:
        import requests
        import base64
        from django.conf import settings
        
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not api_key or not secret_key:
            print("❌ Beem credentials not configured")
            return
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        headers = {
            'Authorization': auth_header,
            'User-Agent': 'MifumoWMS/1.0'
        }
        
        # Check balance
        response = requests.get(
            'https://apisms.beem.africa/v1/balance',
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            balance_data = response.json()
            print(f"Balance Data: {json.dumps(balance_data, indent=2)}")
        else:
            print(f"❌ Failed to get balance: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")

def test_with_different_sender_ids():
    """Test with different sender IDs."""
    print("\n" + "="*50)
    print("TESTING DIFFERENT SENDER IDs")
    print("="*50)
    
    sender_ids = [
        "Taarifa-SMS",
        "IVAN-MIMI", 
        "TAARIFA-SMS",
        "MIFUMO",
        "INFO"
    ]
    
    beem_service = BeemSMSService()
    
    for sender_id in sender_ids:
        print(f"\n--- Testing sender ID: {sender_id} ---")
        
        try:
            result = beem_service.send_sms(
                message=f"Test SMS with sender {sender_id} - Please confirm if you receive this",
                recipients=["255614853618"],
                source_addr=sender_id
            )
            
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("✅ SMS sent successfully!")
            else:
                print(f"❌ SMS failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("SMS DELIVERY TROUBLESHOOTING")
    print("=" * 60)
    
    # Test different phone formats
    test_different_phone_formats()
    
    # Check balance
    check_beem_balance()
    
    # Test different sender IDs
    test_with_different_sender_ids()
    
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING COMPLETED")
    print("=" * 60)
    print("\nIf you still don't receive SMS:")
    print("1. Check your phone's spam folder")
    print("2. Try a different phone number")
    print("3. Contact your carrier to check if SMS is blocked")
    print("4. Wait a few minutes - SMS delivery can be delayed")

