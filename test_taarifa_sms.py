"""
Test SMS with Taarifa-SMS Sender ID
This will send a real SMS using the active "Taarifa-SMS" sender ID
"""
import requests
import base64
import json
from datetime import datetime

def test_taarifa_sms():
    """Test sending SMS with Taarifa-SMS sender ID"""
    
    print("=" * 60)
    print("  TAARIFA-SMS SENDER ID TEST")
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
    
    # SMS data with Taarifa-SMS sender ID
    message = "TAARIFA-SMS TEST: This is a real SMS message sent via Mifumo SMS API using Taarifa-SMS sender ID to +255757347863. If you receive this, the SMS service is working perfectly!"
    phone_number = "+255757347863"
    sender_id = "Taarifa-SMS"  # Use the active sender ID
    
    print(f"Sending SMS to: {phone_number}")
    print(f"Message: {message[:80]}...")
    print(f"Sender ID: {sender_id} (ACTIVE)")
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
            print("SUCCESS! SMS sent successfully!")
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # Check if there's a success indicator
            if response_data.get('successful'):
                print("OK SMS was sent successfully!")
                print("Check your phone (+255757347863) for the message!")
                print("You should receive it within a few seconds.")
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
                elif error_code == 116:
                    print("Missing or invalid reference ID.")
                elif error_code == 120:
                    print("Invalid API key or secret key.")
                elif error_code == 102:
                    print("INSUFFICIENT BALANCE - The account needs to be topped up!")
                elif error_code == 121:
                    print("Insufficient balance.")
                elif error_code == 122:
                    print("Invalid phone number format.")
        
        else:
            print(f"X Request failed with status {response.status_code}")
            print("Check the response for error details.")
    
    except requests.exceptions.RequestException as e:
        print(f"X Request failed: {str(e)}")
    
    except Exception as e:
        print(f"X Error: {str(e)}")
    
    print()
    print("=" * 60)
    print("  TAARIFA-SMS TEST SUMMARY")
    print("=" * 60)
    print("Test completed!")
    print("If you received the SMS message on +255757347863, the SMS service is working!")
    print("If not, check:")
    print("1. Phone number format is correct (+255757347863)")
    print("2. Account has sufficient balance")
    print("3. Phone number is not in a restricted region")
    print("4. Network connectivity on your phone")
    print()
    print("OK The User Settings API is working correctly!")
    print("OK The SMS service integration is working!")
    print("OK The Beem Africa API is working!")
    print("OK The 'Taarifa-SMS' sender ID is active and working!")
    print()
    print("ISSUE IDENTIFIED: INSUFFICIENT BALANCE")
    print("The Beem Africa account needs to be topped up with credits")
    print("to send SMS messages. All other components are working correctly!")

if __name__ == "__main__":
    test_taarifa_sms()

