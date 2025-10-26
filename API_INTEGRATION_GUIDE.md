# Mifumo SMS API Integration Guide

## Overview

The Mifumo SMS API provides a powerful and reliable way to send SMS messages programmatically. Our API follows industry standards similar to African's Talking and Beem Africa, making it easy to integrate into your existing systems.

## Base URL

```
Production: https://mifumosms.servehttp.com/api/integration/v1/
Development: http://127.0.0.1:8001/api/integration/v1/
```

## Authentication

All API requests require authentication using an API key. Include your API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY_HERE
```

### Getting Your API Key

1. Register for an account at [Mifumo SMS Dashboard](https://mifumosms.servehttp.com)
2. Navigate to Settings → API & Webhooks
3. Click "Create New Key" to generate your API key
4. Copy the API key and secret key for use in your application

---

## API Endpoints

### 1. Send SMS

Send SMS messages to one or more recipients.

**Endpoint:** `POST /sms/send/`

**Request Body:**
```json
{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789", "+255987654321"],
  "sender_id": "Taarifa-SMS",
  "schedule_time": "2024-01-01T10:00:00Z"
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | ✅ | SMS text content (max 160 characters) |
| `recipients` | array | ✅ | List of phone numbers in E.164 format (+255XXXXXXXXX) |
| `sender_id` | string | ❌ | Custom sender ID (default: "Taarifa-SMS") |
| `schedule_time` | string | ❌ | ISO 8601 datetime for scheduled sending |

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "SMS sent successfully",
  "data": {
    "message_id": "msg_123456789",
    "recipients": ["+255123456789", "+255987654321"],
    "cost": 10.0,
    "currency": "USD",
    "provider": "beem_africa",
    "status": "sent"
  },
  "error_code": null,
  "details": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Message text is required",
  "error_code": "MISSING_MESSAGE",
  "details": null
}
```

---

### 2. Get Message Status

Check the delivery status of a sent message.

**Endpoint:** `GET /sms/status/{message_id}/`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message_id` | string | ✅ | The message ID returned from send SMS |

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Message status retrieved successfully",
  "data": {
    "message_id": "msg_123456789",
    "status": "delivered",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:05:00Z",
    "recipient_count": 2,
    "content_preview": "Hello from Mifumo SMS!",
    "sender_id": "Taarifa-SMS",
    "delivery_details": [
      {
        "recipient": "+255123456789",
        "status": "delivered",
        "delivered_at": "2024-01-01T10:05:00Z",
        "error_message": null
      },
      {
        "recipient": "+255987654321",
        "status": "pending",
        "delivered_at": null,
        "error_message": null
      }
    ]
  }
}
```

---

### 3. Get Delivery Reports

Retrieve delivery reports for multiple messages with filtering and pagination.

**Endpoint:** `GET /sms/delivery-reports/`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | ❌ | Start date filter (ISO 8601 format) |
| `end_date` | string | ❌ | End date filter (ISO 8601 format) |
| `status` | string | ❌ | Filter by message status (sent, delivered, failed) |
| `page` | integer | ❌ | Page number (default: 1) |
| `per_page` | integer | ❌ | Items per page (max: 100, default: 50) |

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Delivery reports retrieved successfully",
  "data": {
    "reports": [
      {
        "message_id": "msg_123456789",
        "status": "delivered",
        "created_at": "2024-01-01T10:00:00Z",
        "recipient_count": 2,
        "content_preview": "Hello from Mifumo SMS!",
        "sender_id": "Taarifa-SMS"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 50,
      "total": 1,
      "pages": 1
    }
  }
}
```

---

### 4. Get Account Balance

Check your account balance and credit information.

**Endpoint:** `GET /sms/balance/`

**Success Response (200 OK):**
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

---

## Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_REQUIRED` | Missing or invalid Authorization header |
| `INVALID_API_KEY` | API key is invalid or expired |
| `INSUFFICIENT_PERMISSIONS` | API key doesn't have required permissions |
| `MISSING_MESSAGE` | Message text is required |
| `MISSING_RECIPIENTS` | Recipients list is required |
| `INVALID_PHONE_FORMAT` | Phone number format is invalid |
| `NO_VALID_RECIPIENTS` | No valid recipients found |
| `MESSAGE_NOT_FOUND` | Message ID not found |
| `SMS_SEND_FAILED` | Failed to send SMS |
| `INTERNAL_ERROR` | Internal server error |

---

## Code Examples

### cURL

**Send SMS:**
```bash
curl -X POST "https://mifumosms.servehttp.com/api/integration/v1/sms/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "message": "Hello from Mifumo SMS!",
    "recipients": ["+255123456789"],
    "sender_id": "Taarifa-SMS"
  }'
```

**Get Message Status:**
```bash
curl -X GET "https://mifumosms.servehttp.com/api/integration/v1/sms/status/msg_123456789/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Python

```python
import requests
import json

# Configuration
API_BASE = "https://mifumosms.servehttp.com/api/integration/v1"
API_KEY = "YOUR_API_KEY_HERE"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Send SMS
def send_sms(message, recipients, sender_id="Taarifa-SMS"):
    url = f"{API_BASE}/sms/send/"
    data = {
        "message": message,
        "recipients": recipients,
        "sender_id": sender_id
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Get Message Status
def get_message_status(message_id):
    url = f"{API_BASE}/sms/status/{message_id}/"
    response = requests.get(url, headers=headers)
    return response.json()

# Get Balance
def get_balance():
    url = f"{API_BASE}/sms/balance/"
    response = requests.get(url, headers=headers)
    return response.json()

# Example usage
result = send_sms(
    message="Hello from Python!",
    recipients=["+255123456789"]
)
print(result)
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

// Configuration
const API_BASE = 'https://mifumosms.servehttp.com/api/integration/v1';
const API_KEY = 'YOUR_API_KEY_HERE';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Send SMS
async function sendSMS(message, recipients, senderId = 'Taarifa-SMS') {
  try {
    const response = await axios.post(`${API_BASE}/sms/send/`, {
      message,
      recipients,
      sender_id: senderId
    }, { headers });
    
    return response.data;
  } catch (error) {
    console.error('Error sending SMS:', error.response?.data || error.message);
    throw error;
  }
}

// Get Message Status
async function getMessageStatus(messageId) {
  try {
    const response = await axios.get(`${API_BASE}/sms/status/${messageId}/`, { headers });
    return response.data;
  } catch (error) {
    console.error('Error getting message status:', error.response?.data || error.message);
    throw error;
  }
}

// Get Balance
async function getBalance() {
  try {
    const response = await axios.get(`${API_BASE}/sms/balance/`, { headers });
    return response.data;
  } catch (error) {
    console.error('Error getting balance:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
sendSMS('Hello from Node.js!', ['+255123456789'])
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### PHP

```php
<?php
// Configuration
$apiBase = 'https://mifumosms.servehttp.com/api/integration/v1';
$apiKey = 'YOUR_API_KEY_HERE';

$headers = [
    'Authorization: Bearer ' . $apiKey,
    'Content-Type: application/json'
];

// Send SMS
function sendSMS($message, $recipients, $senderId = 'Taarifa-SMS') {
    global $apiBase, $headers;
    
    $url = $apiBase . '/sms/send/';
    $data = [
        'message' => $message,
        'recipients' => $recipients,
        'sender_id' => $senderId
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// Get Message Status
function getMessageStatus($messageId) {
    global $apiBase, $headers;
    
    $url = $apiBase . '/sms/status/' . $messageId . '/';
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    return json_decode($response, true);
}

// Example usage
$result = sendSMS('Hello from PHP!', ['+255123456789']);
print_r($result);
?>
```

---

## Webhooks

Configure webhooks to receive real-time notifications about message delivery status.

### Webhook Events

- `message.sent` - Message was sent successfully
- `message.delivered` - Message was delivered to recipient
- `message.failed` - Message delivery failed

### Webhook Payload

```json
{
  "event": "message.delivered",
  "message_id": "msg_123456789",
  "recipient": "+255123456789",
  "status": "delivered",
  "delivered_at": "2024-01-01T10:05:00Z",
  "error_message": null,
  "timestamp": "2024-01-01T10:05:00Z"
}
```

### Setting Up Webhooks

1. Go to Settings → API & Webhooks in your dashboard
2. Click "Add Webhook"
3. Enter your webhook URL
4. Select the events you want to receive
5. Save the webhook configuration

---

## Rate Limits

- **SMS Sending:** 100 requests per minute
- **Status Checks:** 200 requests per minute
- **Delivery Reports:** 50 requests per minute
- **Balance Checks:** 20 requests per minute

If you exceed these limits, you'll receive a `429 Too Many Requests` response.

---

## Phone Number Formats

All phone numbers must be in E.164 format:
- ✅ `+255123456789` (Tanzania)
- ✅ `+254712345678` (Kenya)
- ✅ `+256700123456` (Uganda)
- ❌ `0712345678` (Local format)
- ❌ `255123456789` (Missing +)

---

## Support

- **Documentation:** [https://mifumosms.servehttp.com/docs](https://mifumosms.servehttp.com/docs)
- **Support Email:** support@mifumosms.com
- **Status Page:** [https://status.mifumosms.com](https://status.mifumosms.com)

---

## Changelog

### Version 1.0.0 (2024-01-01)
- Initial release
- SMS sending and status checking
- Delivery reports
- Account balance
- Webhook support

