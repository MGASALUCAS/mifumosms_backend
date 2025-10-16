#!/usr/bin/env python
"""
Debug script to check ZenoPay configuration and test API call.
"""
import os
import sys
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_zenopay_direct():
    """Test ZenoPay API directly with a sample request."""
    print("=" * 60)
    print("ZENOPAY API DIRECT TEST")
    print("=" * 60)
    
    # Test API endpoint
    url = "https://zenoapi.com/api/payments/mobile_money_tanzania"
    
    # Sample payload
    payload = {
        "order_id": "test-order-123",
        "buyer_email": "test@example.com",
        "buyer_name": "Test User",
        "buyer_phone": "255744963858",
        "amount": 1000
    }
    
    # Test with empty API key (should fail)
    headers_empty = {
        'Content-Type': 'application/json',
        'x-api-key': ''
    }
    
    print("Testing with empty API key...")
    try:
        response = requests.post(url, json=payload, headers=headers_empty, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("INSTRUCTIONS TO FIX THE ISSUE:")
    print("=" * 60)
    print("1. Create a .env file in the mifumosms_backend directory")
    print("2. Add the following line to the .env file:")
    print("   ZENOPAY_API_KEY=your_actual_zenopay_api_key_here")
    print("3. Make sure to replace 'your_actual_zenopay_api_key_here' with your real API key")
    print("4. Restart your Django server")
    print("5. Test the payment initiation again")
    print("\nThe error occurs because the ZENOPAY_API_KEY is not configured.")
    print("The ZenoPay API requires authentication via the x-api-key header.")
    print("=" * 60)

if __name__ == "__main__":
    test_zenopay_direct()
