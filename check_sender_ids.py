#!/usr/bin/env python3
"""
Check available sender IDs with Beem API
"""

import os
import sys
import django
import requests
from requests.auth import HTTPBasicAuth

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

from django.conf import settings

def check_sender_ids():
    """Check available sender IDs."""
    print("=" * 80)
    print("CHECKING SENDER IDS")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Check sender IDs endpoint
    sender_url = "https://apisms.beem.africa/public/v1/sender-names"
    
    try:
        response = requests.get(
            sender_url,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'sender_names' in data['data']:
                sender_names = data['data']['sender_names']
                print(f"\nFound {len(sender_names)} sender IDs:")
                for sender in sender_names:
                    print(f"  - {sender.get('name', 'N/A')} (Status: {sender.get('status', 'N/A')})")
            else:
                print("No sender names found in response")
        else:
            print("ERROR: Failed to get sender IDs!")
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_with_default_sender():
    """Test sending SMS with a default sender ID."""
    print("\n" + "=" * 80)
    print("TESTING WITH DEFAULT SENDER ID")
    print("=" * 80)
    
    api_key = getattr(settings, 'BEEM_API_KEY', None)
    secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
    
    if not api_key or not secret_key:
        print("ERROR: API credentials not found!")
        return
    
    # Try with a simple sender ID
    send_url = "https://apisms.beem.africa/v1/send"
    
    payload = {
        "source_addr": "INFO",  # Try with a simple sender ID
        "encoding": 0,
        "message": "Test message from API test",
        "recipients": [
            {
                "dest_addr": "255700000001",
                "recipient_id": "test_1"
            }
        ]
    }
    
    try:
        response = requests.post(
            send_url,
            json=payload,
            auth=HTTPBasicAuth(api_key, secret_key),
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MifumoWMS/1.0'
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: SMS sent successfully!")
        else:
            print("ERROR: Failed to send SMS!")
            
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Run all tests."""
    print("Checking Beem Sender IDs")
    print("=" * 80)
    
    check_sender_ids()
    test_with_default_sender()

if __name__ == "__main__":
    main()
