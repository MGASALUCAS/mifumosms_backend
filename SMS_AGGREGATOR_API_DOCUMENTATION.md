# 🌍 SMS Aggregator API Documentation

## Overview

The SMS Aggregator API is a comprehensive SMS gateway service that acts as a bridge between applications and African mobile networks. Similar to Beem Africa, it provides multi-network SMS routing, delivery tracking, and compliance handling across multiple African countries.

## 🎯 Key Features

### **SMS Aggregator Capabilities:**
- **Multi-Network Routing**: Automatically routes SMS to appropriate African mobile networks
- **Network Detection**: Intelligently detects recipient's mobile network and country
- **Delivery Tracking**: Real-time delivery status and reporting
- **Compliance Handling**: Country-specific regulatory compliance
- **Reliability**: Multiple provider failover and load balancing
- **Cost Optimization**: Routes through most cost-effective provider

## 🔑 Authentication

All API requests require an API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY_HERE
```

## 📋 Quick Start

### 1. Register as SMS Aggregator

**Endpoint:** `POST /api/sms-aggregator/register/`

**Request:**
```json
{
  "company_name": "African SMS Solutions Ltd",
  "contact_email": "admin@africansms.com",
  "contact_phone": "255712345678",
  "contact_name": "John Mwalimu",
  "business_type": "SMS Aggregator",
  "description": "Multi-network SMS aggregation service"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "12345",
    "account_id": "SA_ABC123XYZ789",
    "api_key": "mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "company_name": "African SMS Solutions Ltd",
    "business_type": "SMS Aggregator",
    "rate_limits": {
      "per_minute": 500,
      "per_hour": 5000,
      "per_day": 50000
    },
    "network_coverage": {
      "countries": ["Tanzania", "Kenya", "Uganda", "Rwanda"],
      "networks": {
        "Tanzania": ["vodacom", "airtel", "tiGo", "halotel", "zantel"],
        "Kenya": ["safaricom", "airtel", "telkom"],
        "Uganda": ["mtn", "airtel", "utl"],
        "Rwanda": ["mtn", "airtel"]
      },
      "providers": ["beem_africa", "africas_talking", "twilio"],
      "total_networks": 12
    }
  },
  "message": "SMS Aggregator registered successfully"
}
```

### 2. Send Aggregated SMS

**Endpoint:** `POST /api/sms-aggregator/send/`

**Headers:**
```
Authorization: Bearer mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Content-Type: application/json
```

**Request:**
```json
{
  "to": "255757347857",
  "message": "Hello from African SMS Aggregator! Your verification code is: 123456",
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
    "to": "255757347857",
    "message": "Hello from African SMS Aggregator! Your verification code is: 123456",
    "status": "sent",
    "delivery_status": "pending",
    "network_info": {
      "country": "Tanzania",
      "network": "vodacom",
      "provider": "beem_africa",
      "confidence": 0.9,
      "prefix": "25575"
    },
    "provider": "beem_africa",
    "routing_time_ms": 1250,
    "sent_at": "2024-01-15T10:30:00Z"
  },
  "message": "SMS routed successfully through aggregator"
}
```

### 3. Check Message Status

**Endpoint:** `GET /api/sms-aggregator/status/{message_id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": "uuid-message-id",
    "user_id": "12345",
    "to": "255757347857",
    "message": "Hello from African SMS Aggregator!",
    "status": "delivered",
    "delivery_status": "delivered",
    "provider": "beem_africa",
    "sent_at": "2024-01-15T10:30:00Z",
    "delivered_at": "2024-01-15T10:30:15Z",
    "error_message": null
  },
  "message": "Message status retrieved successfully"
}
```

## 📚 API Endpoints

### Registration

#### Register SMS Aggregator
- **POST** `/api/sms-aggregator/register/`
- **Description:** Register a new SMS aggregator account
- **Authentication:** None required
- **Rate Limit:** None

**Request Body:**
```json
{
  "company_name": "string (required)",
  "contact_email": "string (required)",
  "contact_phone": "string (required)",
  "contact_name": "string (optional)",
  "business_type": "string (required)",
  "description": "string (optional)"
}
```

### SMS Operations

#### Send Aggregated SMS
- **POST** `/api/sms-aggregator/send/`
- **Description:** Send SMS through multi-network aggregator
- **Authentication:** API Key required
- **Rate Limit:** 500/minute, 5000/hour, 50000/day

**Request Body:**
```json
{
  "to": "string (required) - Phone number in international format",
  "message": "string (required) - SMS message content",
  "sender_id": "string (optional) - Default: Taarifa-SMS"
}
```

**Response Features:**
- **Network Detection**: Automatically detects recipient's network
- **Provider Routing**: Routes to best available provider
- **Compliance Check**: Validates message against country regulations
- **Routing Time**: Shows how long routing took

#### Get Message Status
- **GET** `/api/sms-aggregator/status/{message_id}/`
- **Description:** Get delivery status with network information
- **Authentication:** API Key required

#### Get Delivery Reports
- **GET** `/api/sms-aggregator/reports/`
- **Description:** Get comprehensive delivery reports
- **Authentication:** API Key required

**Query Parameters:**
- `limit` (optional) - Number of reports (default: 50)
- `offset` (optional) - Skip reports (default: 0)
- `status` (optional) - Filter by status
- `country` (optional) - Filter by country
- `network` (optional) - Filter by network
- `provider` (optional) - Filter by provider

### Network Information

#### Get Network Coverage
- **GET** `/api/sms-aggregator/coverage/`
- **Description:** Get supported networks and countries
- **Authentication:** None required

**Response:**
```json
{
  "success": true,
  "data": {
    "countries": ["Tanzania", "Kenya", "Uganda", "Rwanda"],
    "networks": {
      "Tanzania": ["vodacom", "airtel", "tiGo", "halotel", "zantel"],
      "Kenya": ["safaricom", "airtel", "telkom"],
      "Uganda": ["mtn", "airtel", "utl"],
      "Rwanda": ["mtn", "airtel"]
    },
    "providers": ["beem_africa", "africas_talking", "twilio"],
    "total_networks": 12
  },
  "message": "Network coverage information retrieved successfully"
}
```

## 🌍 Supported Networks

### **Tanzania**
- **Vodacom**: 25561, 25562, 25563, 25564, 25565, 25566, 25567, 25568, 25569
- **Airtel**: 25571, 25572, 25573, 25574, 25575, 25576, 25577, 25578
- **tiGo**: 25565, 25566, 25567, 25568, 25569
- **Halotel**: 25568, 25569
- **Zantel**: 25577, 25578

### **Kenya**
- **Safaricom**: 25470, 25471, 25472, 25473, 25474, 25475, 25476, 25477, 25478, 25479
- **Airtel**: 25470, 25471, 25472, 25473, 25474, 25475, 25476, 25477, 25478, 25479
- **Telkom**: 25470, 25471, 25472, 25473, 25474, 25475, 25476, 25477, 25478, 25479

### **Uganda**
- **MTN**: 25670, 25671, 25672, 25673, 25674, 25675, 25676, 25677, 25678, 25679
- **Airtel**: 25670, 25671, 25672, 25673, 25674, 25675, 25676, 25677, 25678, 25679
- **UTL**: 25670, 25671, 25672, 25673, 25674, 25675, 25676, 25677, 25678, 25679

### **Rwanda**
- **MTN**: 25070, 25071, 25072, 25073, 25074, 25075, 25076, 25077, 25078, 25079
- **Airtel**: 25070, 25071, 25072, 25073, 25074, 25075, 25076, 25077, 25078, 25079

## 🔧 SMS Providers

### **Primary Provider: Beem Africa**
- **Reliability**: 95%
- **Coverage**: Tanzania, Kenya, Uganda, Rwanda
- **Cost**: $0.025 per SMS
- **Features**: Real-time delivery reports, high reliability

### **Fallback Provider: Africa's Talking**
- **Reliability**: 92%
- **Coverage**: Tanzania, Kenya, Uganda, Rwanda
- **Cost**: $0.023 per SMS
- **Features**: Good coverage, competitive pricing

### **Premium Provider: Twilio**
- **Reliability**: 98%
- **Coverage**: Tanzania, Kenya, Uganda, Rwanda
- **Cost**: $0.030 per SMS
- **Features**: Highest reliability, global infrastructure

## 📊 Compliance & Regulations

### **Tanzania Compliance**
- Maximum message length: 160 characters
- Prohibited content: spam, promotion keywords
- Sender ID registration required
- Delivery reports mandatory

### **Kenya Compliance**
- Maximum message length: 140 characters
- Opt-in required for marketing messages
- Sender ID registration required
- Delivery reports mandatory

### **Uganda Compliance**
- Maximum message length: 160 characters
- Content filtering for inappropriate material
- Sender ID registration required
- Delivery reports mandatory

### **Rwanda Compliance**
- Maximum message length: 160 characters
- Government approval for certain content
- Sender ID registration required
- Delivery reports mandatory

## ⚠️ Error Codes

| Code | Description |
|------|-------------|
| `MISSING_FIELD` | Required field missing |
| `INVALID_AUTH_HEADER` | Invalid Authorization header format |
| `INVALID_API_KEY` | Invalid or expired API key |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded |
| `COMPLIANCE_VIOLATION` | Message violates country regulations |
| `ROUTING_FAILED` | SMS routing failed |
| `UNKNOWN_PROVIDER` | Provider not recognized |
| `PROVIDER_ERROR` | Provider-specific error |
| `MESSAGE_NOT_FOUND` | Message ID not found |
| `EMAIL_EXISTS` | Email already registered |
| `REGISTRATION_ERROR` | Registration failed |
| `INTERNAL_ERROR` | Internal server error |

## 🔧 Integration Examples

### JavaScript/Node.js

```javascript
const API_BASE_URL = 'https://your-domain.com/api/sms-aggregator';
const API_KEY = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

// Send SMS through aggregator
async function sendAggregatedSMS(to, message) {
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
  
  const result = await response.json();
  
  if (result.success) {
    console.log('SMS routed successfully!');
    console.log('Network:', result.data.network_info.network);
    console.log('Provider:', result.data.provider);
    console.log('Routing time:', result.data.routing_time_ms + 'ms');
  }
  
  return result;
}

// Get network coverage
async function getNetworkCoverage() {
  const response = await fetch(`${API_BASE_URL}/coverage/`);
  const result = await response.json();
  
  if (result.success) {
    console.log('Supported countries:', result.data.countries);
    console.log('Total networks:', result.data.total_networks);
  }
  
  return result;
}

// Usage
sendAggregatedSMS('255757347857', 'Hello from African SMS Aggregator!')
  .then(result => {
    if (result.success) {
      console.log('Message ID:', result.data.message_id);
      console.log('Network detected:', result.data.network_info.country);
    }
  });
```

### Python

```python
import requests
import time

API_BASE_URL = 'https://your-domain.com/api/sms-aggregator'
API_KEY = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def send_aggregated_sms(to, message):
    """Send SMS through aggregator with network detection."""
    data = {
        'to': to,
        'message': message,
        'sender_id': 'Taarifa-SMS'
    }
    
    response = requests.post(f'{API_BASE_URL}/send/', json=data, headers=headers)
    result = response.json()
    
    if result['success']:
        print(f"SMS routed successfully!")
        print(f"Network: {result['data']['network_info']['network']}")
        print(f"Provider: {result['data']['provider']}")
        print(f"Routing time: {result['data']['routing_time_ms']}ms")
    
    return result

def get_network_coverage():
    """Get supported networks and countries."""
    response = requests.get(f'{API_BASE_URL}/coverage/')
    result = response.json()
    
    if result['success']:
        print(f"Supported countries: {result['data']['countries']}")
        print(f"Total networks: {result['data']['total_networks']}")
    
    return result

def get_message_status(message_id):
    """Get message delivery status."""
    response = requests.get(f'{API_BASE_URL}/status/{message_id}/', headers=headers)
    return response.json()

# Usage
result = send_aggregated_sms('255757347857', 'Hello from African SMS Aggregator!')
if result['success']:
    message_id = result['data']['message_id']
    
    # Check status after delay
    time.sleep(5)
    status = get_message_status(message_id)
    print(f"Delivery status: {status['data']['delivery_status']}")
```

### PHP

```php
<?php
$apiBaseUrl = 'https://your-domain.com/api/sms-aggregator';
$apiKey = 'mif_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

function sendAggregatedSMS($to, $message) {
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
    
    $result = json_decode($response, true);
    
    if ($result['success']) {
        echo "SMS routed successfully!\n";
        echo "Network: " . $result['data']['network_info']['network'] . "\n";
        echo "Provider: " . $result['data']['provider'] . "\n";
        echo "Routing time: " . $result['data']['routing_time_ms'] . "ms\n";
    }
    
    return $result;
}

function getNetworkCoverage() {
    global $apiBaseUrl;
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $apiBaseUrl . '/coverage/');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    $result = json_decode($response, true);
    
    if ($result['success']) {
        echo "Supported countries: " . implode(', ', $result['data']['countries']) . "\n";
        echo "Total networks: " . $result['data']['total_networks'] . "\n";
    }
    
    return $result;
}

// Usage
$result = sendAggregatedSMS('255757347857', 'Hello from African SMS Aggregator!');
if ($result['success']) {
    $messageId = $result['data']['message_id'];
    
    // Check status after delay
    sleep(5);
    $status = getMessageStatus($messageId);
    echo "Delivery status: " . $status['data']['delivery_status'] . "\n";
}
?>
```

## 🚀 Getting Started

1. **Register** your company as an SMS aggregator
2. **Get API credentials** (API key + User ID)
3. **Check network coverage** for your target countries
4. **Start sending SMS** with automatic network detection
5. **Monitor delivery** using status and reports endpoints
6. **Scale up** with higher rate limits for aggregators

## 📞 Support

For technical support or questions about the SMS Aggregator API, please contact:
- Email: aggregator-support@mifumo.com
- Documentation: https://docs.mifumo.com/sms-aggregator-api

---

**Version:** 1.0.0  
**Last Updated:** January 2024  
**Coverage:** Tanzania, Kenya, Uganda, Rwanda  
**Providers:** Beem Africa, Africa's Talking, Twilio




