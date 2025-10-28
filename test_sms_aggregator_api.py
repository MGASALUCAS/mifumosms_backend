#!/usr/bin/env python3
"""
Test SMS Aggregator API functionality.
This script demonstrates the SMS Aggregator service capabilities.
"""

import os
import sys
import django
import requests
import json
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mifumo.settings')
django.setup()

# API Configuration
API_BASE_URL = 'http://127.0.0.1:8000/api/sms-aggregator'
TEST_PHONES = {
    'Tanzania': '255757347857',  # Your test phone
    'Kenya': '254712345678',
    'Uganda': '256712345678',
    'Rwanda': '250712345678'
}

def test_sms_aggregator_registration():
    """Test SMS aggregator registration."""
    print("=" * 80)
    print("TESTING SMS AGGREGATOR REGISTRATION")
    print("=" * 80)
    
    registration_data = {
        "company_name": "African SMS Solutions Ltd",
        "contact_email": "admin@africansms.com",
        "contact_phone": "255712345678",
        "contact_name": "John Mwalimu",
        "business_type": "SMS Aggregator",
        "description": "Multi-network SMS aggregation service for African markets"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/register/",
            json=registration_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Registration Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print("✅ SMS Aggregator registration successful!")
                return data['data']
            else:
                print("❌ Registration failed!")
                return None
        else:
            print("❌ Registration failed!")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_network_coverage():
    """Test network coverage information."""
    print("\n" + "=" * 80)
    print("TESTING NETWORK COVERAGE")
    print("=" * 80)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/coverage/",
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Coverage Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Network coverage retrieved successfully!")
                return data['data']
            else:
                print("❌ Coverage retrieval failed!")
                return None
        else:
            print("❌ Coverage retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ Coverage error: {e}")
        return None

def test_send_aggregated_sms(api_key, phone_number, country):
    """Test sending SMS through aggregator."""
    print(f"\n" + "=" * 80)
    print(f"TESTING AGGREGATED SMS SENDING - {country}")
    print("=" * 80)
    
    sms_data = {
        "to": phone_number,
        "message": f"Hello from African SMS Aggregator! This is a test message for {country} sent at {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "sender_id": "Taarifa-SMS"
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/send/",
            json=sms_data,
            headers=headers,
            timeout=30
        )
        
        print(f"SMS Send Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ SMS sent successfully to {country}!")
                return data['data']
            else:
                print(f"❌ SMS sending failed for {country}!")
                return None
        else:
            print(f"❌ SMS sending failed for {country}!")
            return None
            
    except Exception as e:
        print(f"❌ SMS sending error for {country}: {e}")
        return None

def test_message_status(api_key, message_id):
    """Test getting message status."""
    print("\n" + "=" * 80)
    print("TESTING MESSAGE STATUS")
    print("=" * 80)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/status/{message_id}/",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Check: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Status retrieved successfully!")
                return data['data']
            else:
                print("❌ Status retrieval failed!")
                return None
        else:
            print("❌ Status retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def test_delivery_reports(api_key):
    """Test getting delivery reports."""
    print("\n" + "=" * 80)
    print("TESTING DELIVERY REPORTS")
    print("=" * 80)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/reports/",
            headers=headers,
            timeout=30
        )
        
        print(f"Reports Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Reports retrieved successfully!")
                return data['data']
            else:
                print("❌ Reports retrieval failed!")
                return None
        else:
            print("❌ Reports retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ Reports error: {e}")
        return None

def test_api_info(api_key):
    """Test getting API info."""
    print("\n" + "=" * 80)
    print("TESTING API INFO")
    print("=" * 80)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/info/",
            headers=headers,
            timeout=30
        )
        
        print(f"API Info Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API info retrieved successfully!")
                return data['data']
            else:
                print("❌ API info retrieval failed!")
                return None
        else:
            print("❌ API info retrieval failed!")
            return None
            
    except Exception as e:
        print(f"❌ API info error: {e}")
        return None

def main():
    """Run all SMS Aggregator API tests."""
    print("SMS Aggregator API Test Suite")
    print("=" * 80)
    print(f"API Base URL: {API_BASE_URL}")
    print("=" * 80)
    
    # Test 1: Registration
    registration_result = test_sms_aggregator_registration()
    if not registration_result:
        print("\n❌ Registration failed. Cannot continue with other tests.")
        return
    
    api_key = registration_result['api_key']
    user_id = registration_result['user_id']
    account_id = registration_result['account_id']
    
    print(f"\n📋 Registration Details:")
    print(f"   User ID: {user_id}")
    print(f"   Account ID: {account_id}")
    print(f"   API Key: {api_key[:20]}...")
    
    # Test 2: Network Coverage
    coverage_result = test_network_coverage()
    if coverage_result:
        print(f"\n🌍 Network Coverage:")
        print(f"   Countries: {', '.join(coverage_result['countries'])}")
        print(f"   Total Networks: {coverage_result['total_networks']}")
        print(f"   Providers: {', '.join(coverage_result['providers'])}")
    
    # Test 3: API Info
    test_api_info(api_key)
    
    # Test 4: Send SMS to different countries
    sms_results = {}
    for country, phone in TEST_PHONES.items():
        if country == 'Tanzania':  # Only test with your real phone
            result = test_send_aggregated_sms(api_key, phone, country)
            if result:
                sms_results[country] = result
    
    # Test 5: Delivery Reports
    test_delivery_reports(api_key)
    
    # Test 6: Message Status (wait a bit first)
    if sms_results:
        print(f"\n⏳ Waiting 3 seconds before checking message status...")
        time.sleep(3)
        
        for country, result in sms_results.items():
            if result and 'message_id' in result:
                print(f"\n📱 Checking status for {country}...")
                test_message_status(api_key, result['message_id'])
    
    print("\n" + "=" * 80)
    print("🎉 SMS Aggregator API Test Complete!")
    print("=" * 80)
    print("📱 Check your phone for the SMS message!")
    print(f"📞 Phone number: {TEST_PHONES['Tanzania']}")
    print("📤 Sender ID: Taarifa-SMS")
    print("🌍 Network: Detected automatically")
    print("🔄 Provider: Routed through Beem Africa")

if __name__ == "__main__":
    main()







