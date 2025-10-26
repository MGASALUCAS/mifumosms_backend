# API Testing Guide

## Testing Your Integration

This guide helps you test your Mifumo SMS API integration to ensure everything works correctly.

## Prerequisites

1. **API Key**: Get your API key from the dashboard
2. **Test Phone Number**: Use a valid phone number for testing
3. **Development Environment**: Use the development base URL for testing

## Test Environment

**Base URL:** `http://127.0.0.1:8001/api/integration/v1/`

## Step-by-Step Testing

### 1. Test Authentication

First, verify your API key works:

```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/balance/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Balance retrieved successfully",
  "data": {
    "account_id": "ACC-XYZ123",
    "balance": 100.00,
    "currency": "USD",
    "last_updated": "2024-01-01T10:00:00Z"
  }
}
```

### 2. Test SMS Sending

Send a test SMS to verify the sending functionality:

```bash
curl -X POST "http://127.0.0.1:8001/api/integration/v1/sms/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "message": "Test message from API",
    "recipients": ["+255123456789"],
    "sender_id": "Taarifa-SMS"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "SMS sent successfully",
  "data": {
    "message_id": "msg_123456789",
    "recipients": ["+255123456789"],
    "cost": 10.0,
    "currency": "USD",
    "provider": "beem_africa",
    "status": "sent"
  }
}
```

### 3. Test Message Status

Use the message ID from step 2 to check status:

```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/status/msg_123456789/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. Test Delivery Reports

Get delivery reports to see message history:

```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/delivery-reports/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Error Testing

### Test Invalid API Key

```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/balance/" \
  -H "Authorization: Bearer invalid_key"
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Invalid API key",
  "error_code": "INVALID_API_KEY"
}
```

### Test Missing Message

```bash
curl -X POST "http://127.0.0.1:8001/api/integration/v1/sms/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "recipients": ["+255123456789"]
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Message text is required",
  "error_code": "MISSING_MESSAGE"
}
```

### Test Invalid Phone Format

```bash
curl -X POST "http://127.0.0.1:8001/api/integration/v1/sms/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "message": "Test message",
    "recipients": ["0712345678"]
  }'
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Invalid phone number format: 0712345678",
  "error_code": "INVALID_PHONE_FORMAT"
}
```

## Automated Testing Scripts

### Python Test Script

```python
import requests
import json
import time

# Configuration
API_BASE = "http://127.0.0.1:8001/api/integration/v1"
API_KEY = "YOUR_API_KEY_HERE"
TEST_PHONE = "+255123456789"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_api():
    print("Testing Mifumo SMS API...")
    
    # Test 1: Authentication
    print("\n1. Testing authentication...")
    response = requests.get(f"{API_BASE}/sms/balance/", headers=headers)
    if response.status_code == 200:
        print("✅ Authentication successful")
    else:
        print(f"❌ Authentication failed: {response.text}")
        return
    
    # Test 2: Send SMS
    print("\n2. Testing SMS sending...")
    sms_data = {
        "message": f"Test message at {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "recipients": [TEST_PHONE],
        "sender_id": "Taarifa-SMS"
    }
    
    response = requests.post(f"{API_BASE}/sms/send/", json=sms_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print("✅ SMS sent successfully")
        message_id = result['data']['message_id']
        print(f"Message ID: {message_id}")
    else:
        print(f"❌ SMS sending failed: {response.text}")
        return
    
    # Test 3: Check Status
    print("\n3. Testing message status...")
    response = requests.get(f"{API_BASE}/sms/status/{message_id}/", headers=headers)
    if response.status_code == 200:
        print("✅ Status check successful")
        status_data = response.json()
        print(f"Status: {status_data['data']['status']}")
    else:
        print(f"❌ Status check failed: {response.text}")
    
    # Test 4: Get Reports
    print("\n4. Testing delivery reports...")
    response = requests.get(f"{API_BASE}/sms/delivery-reports/", headers=headers)
    if response.status_code == 200:
        print("✅ Delivery reports retrieved")
        reports_data = response.json()
        print(f"Total reports: {reports_data['data']['pagination']['total']}")
    else:
        print(f"❌ Delivery reports failed: {response.text}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_api()
```

### JavaScript Test Script

```javascript
const axios = require('axios');

const API_BASE = 'http://127.0.0.1:8001/api/integration/v1';
const API_KEY = 'YOUR_API_KEY_HERE';
const TEST_PHONE = '+255123456789';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

async function testAPI() {
  console.log('Testing Mifumo SMS API...');
  
  try {
    // Test 1: Authentication
    console.log('\n1. Testing authentication...');
    const balanceResponse = await axios.get(`${API_BASE}/sms/balance/`, { headers });
    console.log('✅ Authentication successful');
    
    // Test 2: Send SMS
    console.log('\n2. Testing SMS sending...');
    const smsData = {
      message: `Test message at ${new Date().toISOString()}`,
      recipients: [TEST_PHONE],
      sender_id: 'Taarifa-SMS'
    };
    
    const sendResponse = await axios.post(`${API_BASE}/sms/send/`, smsData, { headers });
    console.log('✅ SMS sent successfully');
    const messageId = sendResponse.data.data.message_id;
    console.log(`Message ID: ${messageId}`);
    
    // Test 3: Check Status
    console.log('\n3. Testing message status...');
    const statusResponse = await axios.get(`${API_BASE}/sms/status/${messageId}/`, { headers });
    console.log('✅ Status check successful');
    console.log(`Status: ${statusResponse.data.data.status}`);
    
    // Test 4: Get Reports
    console.log('\n4. Testing delivery reports...');
    const reportsResponse = await axios.get(`${API_BASE}/sms/delivery-reports/`, { headers });
    console.log('✅ Delivery reports retrieved');
    console.log(`Total reports: ${reportsResponse.data.data.pagination.total}`);
    
    console.log('\n🎉 All tests completed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

testAPI();
```

## Production Testing

Before going live, test with:

1. **Real phone numbers** you can verify
2. **Production API key** from your dashboard
3. **Production base URL**: `https://mifumosms.servehttp.com/api/integration/v1/`
4. **Different message types** (short, long, special characters)
5. **Multiple recipients** to test bulk sending
6. **Error scenarios** to ensure proper error handling

## Monitoring

Set up monitoring for:
- API response times
- Success/failure rates
- Error code frequency
- Rate limit usage
- Balance levels

## Support

If you encounter issues during testing:
- Check the error codes and messages
- Verify your API key is correct
- Ensure phone numbers are in E.164 format
- Check your account balance
- Contact support: support@mifumosms.com

