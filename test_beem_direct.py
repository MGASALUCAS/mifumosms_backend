"""
Test Beem Africa API Directly
This will directly call the Beem Africa API to send a real SMS
"""
import requests
import base64
import json
from datetime import datetime

def test_beem_direct():
    """Test sending SMS directly through Beem Africa API"""
    
    print("=" * 60)
    print("  BEEM AFRICA API DIRECT TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Phone: +255757347863")
    print()
    
    # Beem Africa API credentials
    api_key = "62f8c3a2cb510335"
    secret_key = "YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ=="
    
    # API URL
    send_url = "https://apisms.beem.africa/v1/send"
    
    print(f"API Key: {api_key}")
    print(f"Secret Key: {secret_key[:20]}...")
    print(f"Send URL: {send_url}")
    print()
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    # SMS data
    message = "BEEM DIRECT TEST: This is a direct test from Beem Africa API to +255757347863. If you receive this, the API is working!"
    phone_number = "+255757347863"
    sender_id = "MIFUMO"
    
    print(f"Sending SMS to: {phone_number}")
    print(f"Message: {message[:80]}...")
    print(f"Sender ID: {sender_id}")
    print()
    
    # Prepare request data
    data = {
        "source_addr": sender_id,
        "schedule_time": "",
        "encoding": 0,
        "message": message,
        "recipients": [
            {
                "recipient_id": 1,
                "dest_addr": phone_number
            }
        ]
    }
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    print("Sending request to Beem Africa API...")
    print(f"Request URL: {send_url}")
    print(f"Request Data: {json.dumps(data, indent=2)}")
    print()
    
    try:
        # Send SMS
        response = requests.post(send_url, json=data, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print()
            print("OK SMS sent successfully!")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Check if there's a success indicator
            if response_data.get('successful'):
                print("SUCCESS: SMS was sent successfully!")
                print("Check your phone (+255757347863) for the message.")
            else:
                print("WARNING: API returned success but SMS might not have been sent.")
                print("Check the response for any error messages.")
        
        elif response.status_code == 401:
            print("X Authentication failed!")
            print("The API key or secret key might be incorrect.")
        
        elif response.status_code == 400:
            print("X Bad request!")
            print("Check the request format or phone number format.")
        
        else:
            print(f"X Request failed with status {response.status_code}")
            print("Check the response for error details.")
    
    except requests.exceptions.RequestException as e:
        print(f"X Request failed: {str(e)}")
    
    except Exception as e:
        print(f"X Error: {str(e)}")
    
    print()
    print("=" * 60)
    print("  BEEM DIRECT TEST SUMMARY")
    print("=" * 60)
    print("Test completed!")
    print("If you received the SMS message on +255757347863, the Beem Africa API is working!")
    print("If not, check:")
    print("1. API credentials are correct")
    print("2. Phone number format is correct (+255757347863)")
    print("3. Sender ID 'MIFUMO' is registered with Beem Africa")
    print("4. Account has sufficient balance")
    print("5. Network connectivity")

if __name__ == "__main__":
    test_beem_direct()

