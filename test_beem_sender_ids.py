"""
Test Beem Africa Sender IDs
This will check what sender IDs are available and try to send with a valid one
"""
import requests
import base64
import json
from datetime import datetime

def test_beem_sender_ids():
    """Test Beem Africa sender IDs and send SMS with valid sender ID"""
    
    print("=" * 60)
    print("  BEEM AFRICA SENDER IDS TEST")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Phone: +255757347863")
    print()
    
    # Beem Africa API credentials
    api_key = "62f8c3a2cb510335"
    secret_key = "YmM4YWMyNjk0NzNlYTE2ZTZmNGE1MDFjZDBjNjE1YjAyMDJhMjJlY2I2MWEwNDIwNTkwMzBhYmMwNzBiMDU4NQ=="
    
    # API URLs
    sender_url = "https://apisms.beem.africa/public/v1/sender-names"
    send_url = "https://apisms.beem.africa/v1/send"
    
    print(f"API Key: {api_key}")
    print(f"Secret Key: {secret_key[:20]}...")
    print()
    
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    auth_header = f"Basic {encoded_credentials}"
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    
    # Step 1: Get available sender IDs
    print("=" * 60)
    print("  1. GET AVAILABLE SENDER IDS")
    print("=" * 60)
    
    try:
        print("Fetching sender IDs from Beem Africa...")
        sender_response = requests.get(sender_url, headers=headers, timeout=30)
        
        print(f"Sender IDs Response Status: {sender_response.status_code}")
        print(f"Sender IDs Response: {sender_response.text}")
        
        if sender_response.status_code == 200:
            sender_data = sender_response.json()
            print("OK Sender IDs retrieved successfully!")
            print(f"Response: {json.dumps(sender_data, indent=2)}")
            
            # Extract sender IDs
            sender_ids = []
            if 'data' in sender_data and isinstance(sender_data['data'], list):
                for item in sender_data['data']:
                    if 'sender_name' in item:
                        sender_ids.append(item['sender_name'])
            
            print(f"Available Sender IDs: {sender_ids}")
            
            if sender_ids:
                # Use the first available sender ID
                sender_id = sender_ids[0]
                print(f"Using Sender ID: {sender_id}")
            else:
                print("No sender IDs found, trying with 'INFO' (common default)")
                sender_id = "INFO"
        
        else:
            print("X Failed to get sender IDs!")
            print("Trying with common sender IDs...")
            sender_id = "INFO"  # Common default sender ID
    
    except Exception as e:
        print(f"X Error getting sender IDs: {str(e)}")
        print("Trying with common sender IDs...")
        sender_id = "INFO"  # Common default sender ID
    
    print()
    
    # Step 2: Try sending SMS with the sender ID
    print("=" * 60)
    print("  2. SEND SMS WITH SENDER ID")
    print("=" * 60)
    
    # SMS data
    message = f"BEEM SENDER TEST: This is a test from Beem Africa API using sender ID '{sender_id}' to +255757347863. If you receive this, the API is working!"
    phone_number = "+255757347863"
    
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
    
    print("Sending request to Beem Africa API...")
    print(f"Request URL: {send_url}")
    print(f"Request Data: {json.dumps(data, indent=2)}")
    print()
    
    try:
        # Send SMS
        response = requests.post(send_url, json=data, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
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
            response_data = response.json()
            if 'data' in response_data:
                error_code = response_data['data'].get('code', 'Unknown')
                error_message = response_data['data'].get('message', 'Unknown error')
                print(f"Error Code: {error_code}")
                print(f"Error Message: {error_message}")
                
                if error_code == 111:
                    print("The sender ID is not registered with Beem Africa.")
                    print("You need to register a sender ID first.")
                elif error_code == 116:
                    print("Missing or invalid reference ID.")
                elif error_code == 120:
                    print("Invalid API key or secret key.")
        
        else:
            print(f"X Request failed with status {response.status_code}")
            print("Check the response for error details.")
    
    except requests.exceptions.RequestException as e:
        print(f"X Request failed: {str(e)}")
    
    except Exception as e:
        print(f"X Error: {str(e)}")
    
    print()
    print("=" * 60)
    print("  BEEM SENDER IDS TEST SUMMARY")
    print("=" * 60)
    print("Test completed!")
    print("If you received the SMS message on +255757347863, the Beem Africa API is working!")
    print("If not, the issue is likely:")
    print("1. No valid sender ID is registered with Beem Africa")
    print("2. The sender ID needs to be approved by Beem Africa")
    print("3. Account might not have sufficient balance")
    print("4. Phone number might be in a restricted region")

if __name__ == "__main__":
    test_beem_sender_ids()

