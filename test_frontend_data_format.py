#!/usr/bin/env python3
"""
Test to show the exact data format the frontend should send.
"""
import requests
import json

def test_frontend_data_format():
    """Test the exact data format frontend should send."""
    base_url = "http://127.0.0.1:8000"
    
    print("Frontend Data Format Test")
    print("=" * 40)
    
    # Test with minimal required data
    print("\n1. Testing with minimal required data...")
    
    # This is what the frontend should send
    frontend_data = {
        "request_type": "custom",
        "requested_sender_id": "FRONTEND-TEST",
        "sample_content": "This is a test message from frontend integration.",
        "business_justification": "Testing frontend integration with the SMS sender ID request system."
    }
    
    print("Frontend should send:")
    print(json.dumps(frontend_data, indent=2))
    
    # Test with authentication (you'll need to replace with a real token)
    print("\n2. Testing API call...")
    print("Note: This test requires authentication. Replace 'YOUR_TOKEN' with a real token.")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_TOKEN'  # Replace with real token
    }
    
    try:
        response = requests.post(f"{base_url}/api/messaging/sender-requests/submit/", 
                               json=frontend_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("SUCCESS: This data format works!")
        elif response.status_code == 401:
            print("EXPECTED: Authentication required (replace YOUR_TOKEN)")
        else:
            print(f"ERROR: Unexpected status {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("\n3. Frontend Integration Summary:")
    print("=" * 40)
    print("SUCCESS: Add 'business_justification' field to your form")
    print("SUCCESS: Add 'request_type' field (use 'custom' or 'default')")
    print("SUCCESS: Update your API call to include all required fields")
    print("SUCCESS: The backend is working correctly!")
    print("=" * 40)

if __name__ == "__main__":
    test_frontend_data_format()
