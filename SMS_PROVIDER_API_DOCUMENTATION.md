# 📱 SMS Provider API Documentation

## Overview

The SMS Provider API allows external users to integrate SMS sending capabilities into their applications. This API provides a simple, RESTful interface for sending SMS messages and tracking delivery status.

## 🔑 Authentication

All API requests require an API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY_HERE
```

## 📋 Quick Start

### 1. Register as SMS Provider

**Endpoint:** `POST /api/sms-provider/register/`

**Request:**
```json
{
  "company_name": "My Company Ltd",
  "contact_email": "admin@mycompany.com",
  "contact_phone": "255712345678",
  "contact_name": "John Doe",
  "description": "SMS integration for our mobile app"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "12345",
    "account_id": "SP_ABC123XYZ789",
    "api_key": "mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "company_name": "My Company Ltd",
    "rate_limits": {
      "per_minute": 100,
      "per_hour": 1000,
      "per_day": 10000
    }
  },
  "message": "SMS Provider registered successfully"
}
```

### 2. Send SMS Message

**Endpoint:** `POST /api/sms-provider/send/`

**Headers:**
```
Authorization: Bearer mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

**Request:**
```json
{
  "to": "255712345678",
  "message": "Hello from My Company! Your verification code is: 123456",
  "sender_id": "Taarifa-SMS"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "uuid-message-id",
    "user_id": "12345",
    "to": "255712345678",
    "message": "Hello from My Company! Your verification code is: 123456",
    "status": "sent",
    "delivery_status": "pending",
    "sent_at": "2024-01-15T10:30:00Z",
    "response_time_ms": 1250
  },
  "message": "SMS sent successfully"
}
```

### 3. Check Message Status

**Endpoint:** `GET /api/sms-provider/status/{message_id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "uuid-message-id",
    "user_id": "12345",
    "to": "255712345678",
    "message": "Hello from My Company! Your verification code is: 123456",
    "status": "delivered",
    "delivery_status": "delivered",
    "sent_at": "2024-01-15T10:30:00Z",
    "delivered_at": "2024-01-15T10:30:15Z",
    "error_message": null
  },
  "message": "Message status retrieved successfully"
}
```

## 📚 API Endpoints

### Registration

#### Register SMS Provider
- **POST** `/api/sms-provider/register/`
- **Description:** Register a new SMS provider account
- **Authentication:** None required
- **Rate Limit:** None

**Request Body:**
```json
{
  "company_name": "string (required)",
  "contact_email": "string (required)",
  "contact_phone": "string (required)",
  "contact_name": "string (optional)",
  "description": "string (optional)"
}
```

**Response Codes:**
- `201` - Registration successful
- `400` - Missing required fields or email already exists
- `500` - Internal server error

### SMS Operations

#### Send SMS
- **POST** `/api/sms-provider/send/`
- **Description:** Send SMS message
- **Authentication:** API Key required
- **Rate Limit:** 100/minute, 1000/hour, 10000/day

**Request Body:**
```json
{
  "to": "string (required) - Phone number in international format",
  "message": "string (required) - SMS message content",
  "sender_id": "string (optional) - Default: Taarifa-SMS"
}
```

**Response Codes:**
- `200` - SMS sent successfully
- `400` - Invalid request or SMS send failed
- `401` - Invalid API key
- `429` - Rate limit exceeded

#### Get Message Status
- **GET** `/api/sms-provider/status/{message_id}/`
- **Description:** Get delivery status of a specific message
- **Authentication:** API Key required
- **Rate Limit:** 100/minute, 1000/hour, 10000/day

**Response Codes:**
- `200` - Status retrieved successfully
- `401` - Invalid API key
- `404` - Message not found

#### Get Delivery Reports
- **GET** `/api/sms-provider/reports/`
- **Description:** Get delivery reports for multiple messages
- **Authentication:** API Key required
- **Rate Limit:** 100/minute, 1000/hour, 10000/day

**Query Parameters:**
- `limit` (optional) - Number of reports to return (default: 50)
- `offset` (optional) - Number of reports to skip (default: 0)
- `status` (optional) - Filter by status (sent, delivered, failed)
- `from_date` (optional) - Filter from date (YYYY-MM-DD)
- `to_date` (optional) - Filter to date (YYYY-MM-DD)

**Response:**
```json
{
  "success": true,
  "data": {
    "reports": [
      {
        "message_id": "uuid",
        "user_id": "12345",
        "to": "255712345678",
        "message": "Hello!",
        "status": "delivered",
        "delivery_status": "delivered",
        "sent_at": "2024-01-15T10:30:00Z",
        "delivered_at": "2024-01-15T10:30:15Z",
        "error_message": null
      }
    ],
    "pagination": {
      "total": 150,
      "limit": 50,
      "offset": 0,
      "has_more": true
    }
  },
  "message": "Delivery reports retrieved successfully"
}
```

### Account Information

#### Get API Info
- **GET** `/api/sms-provider/info/`
- **Description:** Get account information and API details
- **Authentication:** API Key required
- **Rate Limit:** 100/minute, 1000/hour, 10000/day

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "12345",
    "account_id": "SP_ABC123XYZ789",
    "company_name": "My Company Ltd",
    "api_key": "mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "rate_limits": {
      "minute": {
        "used": 5,
        "limit": 100,
        "remaining": 95
      },
      "hour": {
        "used": 150,
        "limit": 1000,
        "remaining": 850
      },
      "day": {
        "used": 2500,
        "limit": 10000,
        "remaining": 7500
      }
    },
    "total_sms_sent": 2500,
    "account_status": "active",
    "api_version": "1.0.0",
    "endpoints": {
      "send_sms": "/api/sms-provider/send/",
      "message_status": "/api/sms-provider/status/{message_id}/",
      "delivery_reports": "/api/sms-provider/reports/",
      "api_info": "/api/sms-provider/info/"
    }
  },
  "message": "API information retrieved successfully"
}
```

## 📊 Status Codes

### Message Status
- `sent` - Message sent to provider
- `delivered` - Message delivered to recipient
- `failed` - Message failed to send

### Delivery Status
- `pending` - Delivery status unknown
- `delivered` - Message confirmed delivered
- `failed` - Message delivery failed

## ⚠️ Error Codes

| Code | Description |
|------|-------------|
| `MISSING_FIELD` | Required field missing |
| `INVALID_AUTH_HEADER` | Invalid Authorization header format |
| `INVALID_API_KEY` | Invalid or expired API key |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `SMS_SEND_FAILED` | SMS sending failed |
| `MESSAGE_NOT_FOUND` | Message ID not found |
| `EMAIL_EXISTS` | Email already registered |
| `REGISTRATION_ERROR` | Registration failed |
| `INTERNAL_ERROR` | Internal server error |

## 🔧 Integration Examples

### JavaScript/Node.js

```javascript
const API_BASE_URL = 'https://your-domain.com/api/sms-provider';
const API_KEY = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

// Send SMS
async function sendSMS(to, message) {
  const response = await fetch(`${API_BASE_URL}/send/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      to: to,
      message: message,
      sender_id: 'Taarifa-SMS'
    })
  });
  
  return await response.json();
}

// Check message status
async function getMessageStatus(messageId) {
  const response = await fetch(`${API_BASE_URL}/status/${messageId}/`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  });
  
  return await response.json();
}

// Usage
sendSMS('255712345678', 'Hello from our app!')
  .then(result => {
    if (result.success) {
      console.log('SMS sent:', result.data.message_id);
      // Check status after a delay
      setTimeout(() => {
        getMessageStatus(result.data.message_id)
          .then(status => console.log('Status:', status.data.delivery_status));
      }, 5000);
    } else {
      console.error('SMS failed:', result.message);
    }
  });
```

### Python

```python
import requests
import time

API_BASE_URL = 'https://your-domain.com/api/sms-provider'
API_KEY = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def send_sms(to, message):
    """Send SMS message"""
    data = {
        'to': to,
        'message': message,
        'sender_id': 'Taarifa-SMS'
    }
    
    response = requests.post(f'{API_BASE_URL}/send/', json=data, headers=headers)
    return response.json()

def get_message_status(message_id):
    """Get message delivery status"""
    response = requests.get(f'{API_BASE_URL}/status/{message_id}/', headers=headers)
    return response.json()

def get_delivery_reports(limit=50, status=None):
    """Get delivery reports"""
    params = {'limit': limit}
    if status:
        params['status'] = status
    
    response = requests.get(f'{API_BASE_URL}/reports/', params=params, headers=headers)
    return response.json()

# Usage
result = send_sms('255712345678', 'Hello from Python!')
if result['success']:
    print(f"SMS sent: {result['data']['message_id']}")
    
    # Check status after delay
    time.sleep(5)
    status = get_message_status(result['data']['message_id'])
    print(f"Status: {status['data']['delivery_status']}")
else:
    print(f"SMS failed: {result['message']}")
```

### PHP

```php
<?php
$apiBaseUrl = 'https://your-domain.com/api/sms-provider';
$apiKey = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

function sendSMS($to, $message) {
    global $apiBaseUrl, $apiKey;
    
    $data = [
        'to' => $to,
        'message' => $message,
        'sender_id' => 'Taarifa-SMS'
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $apiBaseUrl . '/send/');
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $apiKey,
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

function getMessageStatus($messageId) {
    global $apiBaseUrl, $apiKey;
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $apiBaseUrl . '/status/' . $messageId . '/');
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $apiKey
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// Usage
$result = sendSMS('255712345678', 'Hello from PHP!');
if ($result['success']) {
    echo "SMS sent: " . $result['data']['message_id'] . "\n";
    
    // Check status after delay
    sleep(5);
    $status = getMessageStatus($result['data']['message_id']);
    echo "Status: " . $status['data']['delivery_status'] . "\n";
} else {
    echo "SMS failed: " . $result['message'] . "\n";
}
?>
```

## 🚀 Getting Started

1. **Register** your company using the registration endpoint
2. **Save** your API key and user ID securely
3. **Start sending** SMS messages using the send endpoint
4. **Track delivery** using the status and reports endpoints
5. **Monitor usage** using the API info endpoint

## 📞 Support

For technical support or questions about the SMS Provider API, please contact:
- Email: api-support@mifumo.com
- Documentation: https://docs.mifumo.com/sms-provider-api

---

**Version:** 1.0.0  
**Last Updated:** January 2024







