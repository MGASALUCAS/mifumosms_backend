#!/usr/bin/env python3
"""
Complete Quantum SMS API Test
Tests the full flow from registration to SMS sending with "Quantum" sender ID
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api/integration"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(response, title="Response"):
    """Print formatted API response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def test_quantum_sms_registration():
    """Test SMS provider registration for Quantum"""
    
    print_section("QUANTUM SMS PROVIDER REGISTRATION")
    
    registration_data = {
        "company_name": "Quantum SMS Solutions",
        "contact_email": f"quantum_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "contact_phone": "+255757347863",
        "business_type": "SMS Technology",
        "expected_volume": "5000-10000"
    }
    
    print(f"Company: {registration_data['company_name']}")
    print(f"Email: {registration_data['contact_email']}")
    print(f"Phone: {registration_data['contact_phone']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/sms-provider/register/",
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print("SUCCESS! Quantum SMS Provider registered")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('success') and 'data' in data:
                api_key = data['data'].get('api_key')
                secret_key = data['data'].get('secret_key')
                account_id = data['data'].get('account_id')
                
                print(f"\nQuantum API Credentials:")
                print(f"Account ID: {account_id}")
                print(f"API Key: {api_key}")
                print(f"Secret Key: {secret_key}")
                
                return api_key, secret_key, account_id
            else:
                print("Registration failed - no credentials returned")
                return None, None, None
        else:
            print(f"Registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None, None, None
            
    except Exception as e:
        print(f"Error during registration: {e}")
        return None, None, None

def test_quantum_sms_sending(api_key, secret_key):
    """Test SMS sending with Quantum sender ID"""
    
    if not api_key:
        print("\nSkipping SMS sending test - No API key available")
        return None
    
    print_section("QUANTUM SMS SENDING TEST")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Send SMS with Quantum sender ID
    print("1. Sending SMS with 'Quantum' sender ID")
    print("-" * 40)
    
    sms_data = {
        "message": "Hello from Quantum SMS! This is a test message from the Quantum integration system.",
        "recipients": ["+255757347863"],
        "sender_id": "Quantum",  # Using "Quantum" as requested
        "webhook_url": "https://quantum-sms.com/webhook"
    }
    
    print(f"Message: {sms_data['message']}")
    print(f"Recipients: {sms_data['recipients']}")
    print(f"Sender ID: {sms_data['sender_id']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/sms/send/",
            json=sms_data,
            headers=headers
        )
        
        data = print_response(response, "SMS Send Response")
        
        if response.status_code == 200 and data and data.get('success'):
            message_id = data['data'].get('message_id')
            print("SUCCESS! SMS sent with Quantum sender ID")
            print(f"Message ID: {message_id}")
            return message_id
        else:
            print("FAILED! SMS sending failed")
            return None
            
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

def test_quantum_sms_status(api_key, message_id):
    """Test message status checking"""
    
    if not api_key or not message_id:
        print("\nSkipping status test - No API key or message ID")
        return
    
    print_section("QUANTUM SMS STATUS CHECK")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/v1/sms/status/{message_id}/",
            headers=headers
        )
        
        print_response(response, "Message Status")
        
        if response.status_code == 200:
            print("SUCCESS! Message status retrieved")
        else:
            print("FAILED! Could not retrieve message status")
            
    except Exception as e:
        print(f"Error checking message status: {e}")

def test_quantum_balance(api_key):
    """Test account balance checking"""
    
    if not api_key:
        print("\nSkipping balance test - No API key")
        return
    
    print_section("QUANTUM ACCOUNT BALANCE")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/v1/sms/balance/",
            headers=headers
        )
        
        print_response(response, "Account Balance")
        
        if response.status_code == 200:
            print("SUCCESS! Account balance retrieved")
        else:
            print("FAILED! Could not retrieve account balance")
            
    except Exception as e:
        print(f"Error checking balance: {e}")

def test_quantum_delivery_reports(api_key):
    """Test delivery reports"""
    
    if not api_key:
        print("\nSkipping delivery reports test - No API key")
        return
    
    print_section("QUANTUM DELIVERY REPORTS")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Get reports for today
    today = datetime.now().strftime('%Y-%m-%d')
    params = {
        'start_date': f'{today}T00:00:00Z',
        'end_date': f'{today}T23:59:59Z',
        'status': 'all'
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/v1/sms/delivery-reports/",
            headers=headers,
            params=params
        )
        
        print_response(response, "Delivery Reports")
        
        if response.status_code == 200:
            print("SUCCESS! Delivery reports retrieved")
        else:
            print("FAILED! Could not retrieve delivery reports")
            
    except Exception as e:
        print(f"Error getting delivery reports: {e}")

def test_quantum_api_info():
    """Test API information endpoints"""
    
    print_section("QUANTUM API INFORMATION")
    
    # Test API Status
    print("1. Testing API Status")
    try:
        response = requests.get(f"{API_BASE}/v1/status/")
        print_response(response, "API Status")
    except Exception as e:
        print(f"Error checking API status: {e}")
    
    # Test API Info
    print("\n2. Testing API Information")
    try:
        response = requests.get(f"{API_BASE}/v1/info/")
        print_response(response, "API Info")
    except Exception as e:
        print(f"Error checking API info: {e}")

def test_quantum_error_handling(api_key):
    """Test error handling scenarios"""
    
    if not api_key:
        print("\nSkipping error handling test - No API key")
        return
    
    print_section("QUANTUM ERROR HANDLING TEST")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Invalid phone number
    print("1. Testing invalid phone number")
    invalid_sms_data = {
        "message": "Test message",
        "recipients": ["invalid_phone"],
        "sender_id": "Quantum"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/sms/send/",
            json=invalid_sms_data,
            headers=headers
        )
        print_response(response, "Invalid Phone Error")
    except Exception as e:
        print(f"Error testing invalid phone: {e}")
    
    # Test 2: Empty message
    print("\n2. Testing empty message")
    empty_sms_data = {
        "message": "",
        "recipients": ["+255757347863"],
        "sender_id": "Quantum"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/v1/sms/send/",
            json=empty_sms_data,
            headers=headers
        )
        print_response(response, "Empty Message Error")
    except Exception as e:
        print(f"Error testing empty message: {e}")
    
    # Test 3: Invalid API key
    print("\n3. Testing invalid API key")
    invalid_headers = {
        "Authorization": "Bearer invalid_key_12345",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{API_BASE}/v1/sms/balance/",
            headers=invalid_headers
        )
        print_response(response, "Invalid API Key Error")
    except Exception as e:
        print(f"Error testing invalid API key: {e}")

def main():
    """Main test function"""
    
    print("="*60)
    print("  QUANTUM SMS API - COMPLETE INTEGRATION TEST")
    print("="*60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Phone: +255757347863")
    print(f"Sender ID: Quantum")
    print(f"Base URL: {BASE_URL}")
    
    # Step 1: Register Quantum SMS Provider
    api_key, secret_key, account_id = test_quantum_sms_registration()
    
    # Step 2: Test API Information
    test_quantum_api_info()
    
    # Step 3: Send SMS with Quantum sender ID
    message_id = test_quantum_sms_sending(api_key, secret_key)
    
    # Step 4: Check message status
    test_quantum_sms_status(api_key, message_id)
    
    # Step 5: Check account balance
    test_quantum_balance(api_key)
    
    # Step 6: Get delivery reports
    test_quantum_delivery_reports(api_key)
    
    # Step 7: Test error handling
    test_quantum_error_handling(api_key)
    
    # Final Summary
    print_section("QUANTUM SMS TEST SUMMARY")
    
    if api_key:
        print("SUCCESS: Quantum SMS API credentials obtained!")
        print(f"Account ID: {account_id}")
        print(f"API Key: {api_key}")
        print(f"Secret Key: {secret_key}")
        print("\nQuantum SMS Integration is working!")
        print("\nExample usage with Quantum sender ID:")
        print(f'curl -X POST "{API_BASE}/v1/sms/send/" \\')
        print(f'  -H "Authorization: Bearer {api_key}" \\')
        print(f'  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"message": "Hello from Quantum SMS!", "recipients": ["+255757347863"], "sender_id": "Quantum"}}\'')
    else:
        print("FAILED: Could not obtain Quantum SMS API credentials")
        print("Check the registration endpoint and try again.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

