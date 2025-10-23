#!/usr/bin/env python3
"""
Test Beem account status and limits
"""

import os
import sys
import django
import requests
import base64

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def test_beem_account_status():
    """Test Beem account status and limits."""
    print("=" * 80)
    print("TESTING BEEM ACCOUNT STATUS")
    print("=" * 80)
    
    try:
        api_key = getattr(settings, 'BEEM_API_KEY', None)
        secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not api_key or not secret_key:
            print("ERROR: API credentials not found!")
            return
        
        print(f"API Key: {api_key[:10]}...")
        print(f"Secret Key: {secret_key[:10]}...")
        
        # Create Basic Auth header
        credentials = f"{api_key}:{secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_header = f"Basic {encoded_credentials}"
        
        # Test 1: Check account balance
        print("\n" + "=" * 80)
        print("TEST 1: CHECK ACCOUNT BALANCE")
        print("=" * 80)
        
        try:
            balance_response = requests.get(
                "https://apisms.beem.africa/public/v1/vendors/balance",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"Balance Status Code: {balance_response.status_code}")
            print(f"Balance Response: {balance_response.text}")
            
            if balance_response.status_code == 200:
                print("SUCCESS: Account balance check successful")
            else:
                print("FAILED: Account balance check failed")
                
        except Exception as e:
            print(f"ERROR: Balance check error: {e}")
        
        # Test 2: Check sender IDs
        print("\n" + "=" * 80)
        print("TEST 2: CHECK SENDER IDS")
        print("=" * 80)
        
        try:
            sender_response = requests.get(
                "https://apisms.beem.africa/public/v1/sender-names",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"Sender IDs Status Code: {sender_response.status_code}")
            print(f"Sender IDs Response: {sender_response.text}")
            
            if sender_response.status_code == 200:
                print("SUCCESS: Sender IDs check successful")
            else:
                print("FAILED: Sender IDs check failed")
                
        except Exception as e:
            print(f"ERROR: Sender IDs check error: {e}")
        
        # Test 3: Try sending with minimal data
        print("\n" + "=" * 80)
        print("TEST 3: MINIMAL SMS SEND TEST")
        print("=" * 80)
        
        try:
            minimal_data = {
                "source_addr": "Taarifa-SMS",
                "message": "Test",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "1",
                    "dest_addr": "255614853618"
                }]
            }
            
            send_response = requests.post(
                "https://apisms.beem.africa/v1/send",
                json=minimal_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"Send Status Code: {send_response.status_code}")
            print(f"Send Response: {send_response.text}")
            
            if send_response.status_code == 200:
                print("SUCCESS: SMS send test successful")
            else:
                print("FAILED: SMS send test failed")
                
        except Exception as e:
            print(f"ERROR: SMS send test error: {e}")
        
        # Test 4: Try with different sender ID
        print("\n" + "=" * 80)
        print("TEST 4: DIFFERENT SENDER ID TEST")
        print("=" * 80)
        
        try:
            quantum_data = {
                "source_addr": "Quantum",
                "message": "Test",
                "encoding": 0,
                "recipients": [{
                    "recipient_id": "1",
                    "dest_addr": "255614853618"
                }]
            }
            
            quantum_response = requests.post(
                "https://apisms.beem.africa/v1/send",
                json=quantum_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': auth_header,
                    'User-Agent': 'MifumoWMS/1.0'
                },
                timeout=30
            )
            
            print(f"Quantum Send Status Code: {quantum_response.status_code}")
            print(f"Quantum Send Response: {quantum_response.text}")
            
            if quantum_response.status_code == 200:
                print("SUCCESS: Quantum SMS send test successful")
            else:
                print("FAILED: Quantum SMS send test failed")
                
        except Exception as e:
            print(f"ERROR: Quantum SMS send test error: {e}")
        
    except Exception as e:
        print(f"Error testing account status: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run account status test."""
    print("Testing Beem Account Status")
    print("=" * 80)
    
    test_beem_account_status()

if __name__ == "__main__":
    main()
