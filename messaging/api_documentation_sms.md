# SMS API Documentation - Beem Integration

## Overview

The Mifumo WMS SMS API provides comprehensive SMS messaging capabilities using Beem Africa as the primary SMS provider. This integration offers reliable SMS delivery across African countries with competitive pricing and excellent delivery rates.

## Base URL
```
https://your-domain.com/api/messaging/sms/beem/
```

## Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer your-jwt-token
```

## Environment Configuration

Add the following variables to your `.env` file:

```env
# Beem Africa SMS Configuration
BEEM_API_KEY=your-beem-api-key
BEEM_SECRET_KEY=your-beem-secret-key
BEEM_DEFAULT_SENDER_ID=MIFUMO
BEEM_API_TIMEOUT=30
```

## API Endpoints

### 1. Send Single SMS

Send a single SMS message via Beem Africa.

**Endpoint:** `POST /api/messaging/sms/beem/send/`

**Request Body:**
```json
{
    "message": "Hello from Mifumo WMS!",
    "recipients": ["255700000001", "255700000002"],
    "sender_id": "MIFUMO",
    "template_id": "uuid-optional",
    "schedule_time": "2024-01-01T10:00:00Z",
    "encoding": 0
}
```

**Parameters:**
- `message` (string, required): SMS message content (max 160 characters)
- `recipients` (array, required): List of recipient phone numbers in international format
- `sender_id` (string, **required**): Sender ID (max 11 characters) - Must be registered and active
- `template_id` (UUID, optional): SMS template ID to use
- `schedule_time` (datetime, optional): When to send the message (ISO format)
- `encoding` (integer, optional): Message encoding (0=GSM7, 1=UCS2)

**Response:**
```json
{
    "success": true,
    "message": "SMS sent successfully via Beem",
    "data": {
        "message_id": "uuid",
        "base_message_id": "uuid",
        "provider": "beem",
        "recipient_count": 2,
        "cost_estimate": 0.10,
        "status": "sent",
        "beem_response": {
            "success": true,
            "provider": "beem",
            "response": {...},
            "message_count": 2,
            "cost_estimate": 0.10
        }
    }
}
```

**Example cURL:**
```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/send/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from Mifumo WMS!",
    "recipients": ["255700000001", "255700000002"],
    "sender_id": "MIFUMO"
  }'
```

### 2. Send Bulk SMS

Send multiple SMS messages in a single API call.

**Endpoint:** `POST /api/messaging/sms/beem/send-bulk/`

**Request Body:**
```json
{
    "messages": [
        {
            "message": "Hello from Mifumo WMS!",
            "recipients": ["255700000001", "255700000002"],
            "sender_id": "MIFUMO"
        },
        {
            "message": "Another message",
            "recipients": ["255700000003"],
            "sender_id": "MIFUMO"
        }
    ],
    "schedule_time": "2024-01-01T10:00:00Z"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Bulk SMS sent successfully via Beem",
    "data": {
        "total_messages": 2,
        "total_recipients": 3,
        "total_cost": 0.15,
        "provider": "beem",
        "results": [
            {
                "message_id": "uuid",
                "recipient_count": 2,
                "status": "sent",
                "cost": 0.10
            },
            {
                "message_id": "uuid",
                "recipient_count": 1,
                "status": "sent",
                "cost": 0.05
            }
        ]
    }
}
```

### 3. Test Beem Connection

Test the connection to Beem SMS API.

**Endpoint:** `GET /api/messaging/sms/beem/test-connection/`

**Response:**
```json
{
    "success": true,
    "message": "Connection test successful",
    "data": {
        "provider": "beem",
        "api_key_configured": true,
        "secret_key_configured": true,
        "connection_status": "success"
    }
}
```

### 4. Get Beem Account Balance

Get account balance information from Beem.

**Endpoint:** `GET /api/messaging/sms/beem/balance/`

**Response:**
```json
{
    "success": true,
    "data": {
        "provider": "beem",
        "balance": "N/A",
        "currency": "USD",
        "message": "Balance check not available via API. Check Beem dashboard."
    }
}
```

### 5. Validate Phone Number

Validate phone number format for Beem SMS.

**Endpoint:** `POST /api/messaging/sms/beem/validate-phone/`

**Request Body:**
```json
{
    "phone_number": "255700000001"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "phone_number": "255700000001",
        "formatted": "255700000001",
        "is_valid": true,
        "provider": "beem"
    }
}
```

### 6. Get SMS Delivery Status

Get delivery status for a sent SMS message.

**Endpoint:** `GET /api/messaging/sms/beem/{message_id}/status/`

**Response:**
```json
{
    "success": true,
    "data": {
        "message_id": "uuid",
        "base_message_id": "uuid",
        "status": "delivered",
        "provider": "beem",
        "sent_at": "2024-01-01T10:00:00Z",
        "delivered_at": "2024-01-01T10:00:05Z",
        "cost": 0.05,
        "beem_status": {
            "success": true,
            "message_id": "uuid",
            "status": "delivered",
            "provider": "beem"
        }
    }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error message"]
    }
}
```

**Common HTTP Status Codes:**
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Phone Number Format

Beem SMS requires phone numbers in international format without the `+` sign:

**Valid formats:**
- `255700000001` (Tanzania)
- `254700000001` (Kenya)
- `2347000000001` (Nigeria)
- `27123456789` (South Africa)

**Invalid formats:**
- `+255700000001` (contains +)
- `0700000001` (missing country code)
- `255-700-000-001` (contains dashes)

## Message Encoding

- `0` (GSM7): Standard GSM 7-bit encoding (default)
- `1` (UCS2): Unicode encoding for special characters

## Cost Estimation

The API provides cost estimates based on:
- Number of recipients
- Message length (160 characters per SMS part)
- Beem's current pricing

**Example cost calculation:**
- 1 recipient, 80 characters = $0.05
- 1 recipient, 200 characters = $0.10 (2 SMS parts)
- 10 recipients, 80 characters = $0.50

## Rate Limits

- Maximum 1000 recipients per single SMS call
- Maximum 100 messages per bulk SMS call
- Maximum 10,000 total recipients per bulk operation
- API timeout: 30 seconds (configurable)

## Webhooks (Future Implementation)

Delivery status updates will be available via webhooks:

**Webhook URL:** `https://your-domain.com/webhooks/sms/beem/`

**Webhook Payload:**
```json
{
    "message_id": "uuid",
    "status": "delivered",
    "delivered_at": "2024-01-01T10:00:05Z",
    "error_code": null,
    "error_message": null
}
```

## Testing

### Test Connection
```bash
curl -X GET "https://your-domain.com/api/messaging/sms/beem/test-connection/" \
  -H "Authorization: Bearer your-jwt-token"
```

### Send Test SMS
```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/send/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message from Mifumo WMS",
    "recipients": ["255700000001"],
    "sender_id": "TEST"
  }'
```

### Validate Phone Number
```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/validate-phone/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "255700000001"
  }'
```

## Integration Examples

### Python
```python
import requests

# Send SMS
url = "https://your-domain.com/api/messaging/sms/beem/send/"
headers = {
    "Authorization": "Bearer your-jwt-token",
    "Content-Type": "application/json"
}
data = {
    "message": "Hello from Python!",
    "recipients": ["255700000001"],
    "sender_id": "MIFUMO"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### JavaScript
```javascript
// Send SMS
const sendSMS = async () => {
  const response = await fetch('https://your-domain.com/api/messaging/sms/beem/send/', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer your-jwt-token',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: 'Hello from JavaScript!',
      recipients: ['255700000001'],
      sender_id: 'MIFUMO'
    })
  });
  
  const data = await response.json();
  console.log(data);
};
```

### PHP
```php
<?php
// Send SMS
$url = 'https://your-domain.com/api/messaging/sms/beem/send/';
$data = [
    'message' => 'Hello from PHP!',
    'recipients' => ['255700000001'],
    'sender_id' => 'MIFUMO'
];

$options = [
    'http' => [
        'header' => [
            'Authorization: Bearer your-jwt-token',
            'Content-Type: application/json'
        ],
        'method' => 'POST',
        'content' => json_encode($data)
    ]
];

$context = stream_context_create($options);
$result = file_get_contents($url, false, $context);
echo $result;
?>
```

## Support

For technical support or questions about the SMS API:

- **Documentation**: [docs.mifumo.com](https://docs.mifumo.com)
- **Support Email**: [support@mifumo.com](mailto:support@mifumo.com)
- **Beem Documentation**: [login.beem.africa](https://login.beem.africa)

## Changelog

### Version 1.0.0
- Initial release with Beem Africa integration
- Support for single and bulk SMS sending
- Phone number validation
- Cost estimation
- Delivery status tracking
- Connection testing
