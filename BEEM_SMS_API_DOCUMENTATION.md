# 📱 Beem SMS API Documentation

## 🎯 Overview

The Beem SMS integration provides comprehensive SMS messaging capabilities for the Mifumo WMS platform using Beem Africa as the primary SMS provider. This integration offers reliable SMS delivery across African countries with competitive pricing and excellent delivery rates.

## 🔗 Base URL

```
https://your-domain.com/api/messaging/sms/sms/beem/
```

**Note**: The URL structure includes double `sms` due to the URL configuration. This is the correct path for all Beem SMS endpoints.

## 🔐 Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer your-jwt-token
```

## ⚙️ Environment Configuration

Add the following variables to your `.env` file:

```env
# Beem Africa SMS Configuration
BEEM_API_KEY=your-beem-api-key
BEEM_SECRET_KEY=your-beem-secret-key
BEEM_DEFAULT_SENDER_ID=MIFUMO
BEEM_API_TIMEOUT=30
BEEM_API_BASE_URL=https://apisms.beem.africa/v1
BEEM_SEND_URL=https://apisms.beem.africa/v1/send
BEEM_BALANCE_URL=https://apisms.beem.africa/public/v1/vendors/balance
BEEM_DELIVERY_URL=https://dlrapi.beem.africa/public/v1/delivery-reports
BEEM_SENDER_URL=https://apisms.beem.africa/public/v1/sender-names
BEEM_TEMPLATE_URL=https://apisms.beem.africa/public/v1/sms-templates
```

## 📋 API Endpoints

### 1. Send Single SMS

Send a single SMS message via Beem Africa.

**Endpoint:** `POST /api/messaging/sms/sms/beem/send/`

**Request Body:**
```json
{
    "message": "Hello from Mifumo WMS! This is a test message.",
    "recipients": ["255700000001", "255700000002"],
    "sender_id": "MIFUMO",
    "template_id": "uuid-optional",
    "schedule_time": "2024-01-01T10:00:00Z",
    "encoding": 0
}
```

**Parameters:**
- `message` (string, **required**): SMS message content (max 160 characters)
- `recipients` (array, **required**): List of recipient phone numbers in international format
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
        "message_id": "123e4567-e89b-12d3-a456-426614174000",
        "base_message_id": "123e4567-e89b-12d3-a456-426614174001",
        "provider": "beem",
        "recipient_count": 2,
        "cost_estimate": 0.10,
        "status": "sent",
        "beem_response": {
            "success": true,
            "provider": "beem",
            "response": {
                "request_id": "req_123456",
                "valid": 2,
                "invalid": 0,
                "duplicates": 0
            },
            "message_count": 2,
            "cost_estimate": 0.10
        }
    }
}
```

**Postman Example:**
```http
POST {{base_url}}/api/messaging/sms/beem/send/
Authorization: Bearer {{jwt_token}}
Content-Type: application/json

{
    "message": "Hello from Mifumo WMS! This is a test message.",
    "recipients": ["255700000001", "255700000002"],
    "sender_id": "MIFUMO",
    "encoding": 0
}
```

### 2. Send Bulk SMS

Send multiple SMS messages in a single request.

**Endpoint:** `POST /api/messaging/sms/sms/beem/send-bulk/`

**Request Body:**
```json
{
    "messages": [
        {
            "message": "Hello from Mifumo WMS! This is message 1.",
            "recipients": ["255700000001", "255700000002"],
            "sender_id": "MIFUMO",
            "encoding": 0
        },
        {
            "message": "Hello from Mifumo WMS! This is message 2.",
            "recipients": ["255700000003"],
            "sender_id": "MIFUMO",
            "encoding": 0
        }
    ],
    "schedule_time": "2024-01-01T10:00:00Z"
}
```

**Parameters:**
- `messages` (array, **required**): List of SMS messages to send (max 100 messages)
- `schedule_time` (datetime, optional): When to send all messages (ISO format)

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
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "recipient_count": 2,
                "status": "sent",
                "cost": 0.10
            },
            {
                "message_id": "123e4567-e89b-12d3-a456-426614174001",
                "recipient_count": 1,
                "status": "sent",
                "cost": 0.05
            }
        ]
    }
}
```

**Postman Example:**
```http
POST {{base_url}}/api/messaging/sms/beem/send-bulk/
Authorization: Bearer {{jwt_token}}
Content-Type: application/json

{
    "messages": [
        {
            "message": "Hello from Mifumo WMS! This is message 1.",
            "recipients": ["255700000001", "255700000002"],
            "sender_id": "MIFUMO"
        },
        {
            "message": "Hello from Mifumo WMS! This is message 2.",
            "recipients": ["255700000003"],
            "sender_id": "MIFUMO"
        }
    ]
}
```

### 3. Test Beem Connection

Test the connection to Beem SMS API.

**Endpoint:** `GET /api/messaging/sms/sms/beem/test-connection/`

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

**Postman Example:**
```http
GET {{base_url}}/api/messaging/sms/beem/test-connection/
Authorization: Bearer {{jwt_token}}
```

### 4. Get Account Balance

Get Beem account balance information.

**Endpoint:** `GET /api/messaging/sms/sms/beem/balance/`

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

**Postman Example:**
```http
GET {{base_url}}/api/messaging/sms/beem/balance/
Authorization: Bearer {{jwt_token}}
```

### 5. Validate Phone Number

Validate phone number format for Beem SMS.

**Endpoint:** `POST /api/messaging/sms/sms/beem/validate-phone/`

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

**Postman Example:**
```http
POST {{base_url}}/api/messaging/sms/beem/validate-phone/
Authorization: Bearer {{jwt_token}}
Content-Type: application/json

{
    "phone_number": "255700000001"
}
```

### 6. Get SMS Delivery Status

Get delivery status for a sent SMS message.

**Endpoint:** `GET /api/messaging/sms/sms/beem/{message_id}/status/`

**Response:**
```json
{
    "success": true,
    "data": {
        "message_id": "123e4567-e89b-12d3-a456-426614174000",
        "base_message_id": "123e4567-e89b-12d3-a456-426614174001",
        "status": "delivered",
        "provider": "beem",
        "sent_at": "2024-01-01T10:00:00Z",
        "delivered_at": "2024-01-01T10:00:05Z",
        "cost": 0.05,
        "beem_status": {
            "success": true,
            "message_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "delivered",
            "provider": "beem"
        }
    }
}
```

**Postman Example:**
```http
GET {{base_url}}/api/messaging/sms/beem/123e4567-e89b-12d3-a456-426614174000/status/
Authorization: Bearer {{jwt_token}}
```

## 📱 Phone Number Formats

### Supported Formats

Beem SMS supports various phone number formats:

- **International format with +**: `+255700000001`
- **International format without +**: `255700000001`
- **Local format with 0**: `0700000001` (automatically converted to 255700000001)
- **Local format without 0**: `700000001` (automatically converted to 255700000001)

### Country Code Support

- **Tanzania**: +255 (default)
- **Kenya**: +254
- **Uganda**: +256
- **Rwanda**: +250
- **Burundi**: +257
- **Other African countries**: As per international standards

## 💰 Cost Calculation

### Pricing Structure

- **Base cost per SMS**: $0.05
- **Additional cost per 160 characters**: $0.01
- **Currency**: USD

### Cost Examples

| Message Length | Recipients | Cost per Recipient | Total Cost |
|----------------|------------|-------------------|------------|
| 50 characters  | 1          | $0.05             | $0.05      |
| 50 characters  | 10         | $0.05             | $0.50      |
| 200 characters | 1          | $0.06             | $0.06      |
| 200 characters | 10         | $0.06             | $0.60      |

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
    "success": false,
    "message": "Validation error",
    "errors": {
        "message": ["Message cannot be empty"],
        "recipients": ["At least one recipient is required"]
    }
}
```

#### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 400 Beem API Error
```json
{
    "success": false,
    "message": "SMS sending failed: Beem API error: 400 - Invalid sender ID",
    "provider": "beem"
}
```

#### 500 Internal Server Error
```json
{
    "success": false,
    "message": "An unexpected error occurred while sending SMS",
    "error": "Database connection failed"
}
```

## 🔧 Sender ID Management

### Registering Sender IDs

Before sending SMS, you must register sender IDs with Beem:

1. **Via Beem Dashboard**: Register through Beem Africa's web interface
2. **Via API**: Use the sender ID management endpoints

### Sender ID Requirements

- **Length**: 3-11 characters
- **Characters**: Alphanumeric only (A-Z, 0-9)
- **Status**: Must be active and approved
- **Sample Content**: Required for registration

## 📊 Message Status Tracking

### Status Values

- **queued**: Message queued for sending
- **sent**: Message sent to provider
- **delivered**: Message delivered to recipient
- **failed**: Message failed to send
- **expired**: Message expired (for scheduled messages)

### Delivery Reports

Delivery reports are available via webhooks or by querying the status endpoint.

## 🕐 Scheduling Messages

### Schedule Time Format

Use ISO 8601 format for scheduling:

```json
{
    "schedule_time": "2024-01-01T10:00:00Z"
}
```

### Scheduling Rules

- **Minimum delay**: 1 minute from current time
- **Maximum delay**: 1 year from current time
- **Timezone**: UTC (GMT+0)
- **Format**: ISO 8601 datetime string

## 🔄 Rate Limiting

### Limits

- **Messages per minute**: 60
- **API calls per minute**: 1000
- **Bulk messages per request**: 100
- **Total recipients per bulk**: 10,000

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 📝 Postman Collection

### Environment Variables

Create a Postman environment with these variables:

```json
{
    "base_url": "https://your-domain.com",
    "jwt_token": "your-jwt-token",
    "sender_id": "MIFUMO",
    "test_phone": "255700000001"
}
```

### Collection Structure

```
📁 Beem SMS API
├── 📁 Authentication
│   └── 🔐 Login
├── 📁 SMS Operations
│   ├── 📤 Send Single SMS
│   ├── 📤 Send Bulk SMS
│   ├── 🔍 Get Delivery Status
│   └── 📊 Get Account Balance
├── 📁 Utilities
│   ├── 🔧 Test Connection
│   ├── 📱 Validate Phone Number
│   └── 📋 Get Sender IDs
└── 📁 Error Handling
    ├── ❌ Validation Errors
    ├── ❌ Authentication Errors
    └── ❌ API Errors
```

## 🧪 Testing Examples

### Test Single SMS

```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/send/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message from Mifumo WMS",
    "recipients": ["255700000001"],
    "sender_id": "MIFUMO"
  }'
```

### Test Bulk SMS

```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/send-bulk/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "message": "Bulk test message 1",
        "recipients": ["255700000001"],
        "sender_id": "MIFUMO"
      },
      {
        "message": "Bulk test message 2",
        "recipients": ["255700000002"],
        "sender_id": "MIFUMO"
      }
    ]
  }'
```

### Test Connection

```bash
curl -X GET "https://your-domain.com/api/messaging/sms/beem/test-connection/" \
  -H "Authorization: Bearer your-jwt-token"
```

## 🔍 Troubleshooting

### Common Issues

1. **Invalid Sender ID**
   - Ensure sender ID is registered and active
   - Check sender ID format (3-11 alphanumeric characters)

2. **Invalid Phone Numbers**
   - Use international format (e.g., 255700000001)
   - Ensure country code is included

3. **Authentication Errors**
   - Verify JWT token is valid and not expired
   - Check Authorization header format

4. **API Configuration**
   - Verify Beem API credentials in environment variables
   - Test connection using the test endpoint

### Debug Steps

1. **Test Connection**: Use `/test-connection/` endpoint
2. **Validate Phone**: Use `/validate-phone/` endpoint
3. **Check Logs**: Review application logs for detailed error messages
4. **Verify Credentials**: Ensure Beem API credentials are correct

## 📞 Support

For technical support:

- **Email**: support@mifumo.com
- **Documentation**: [Mifumo WMS Docs](https://docs.mifumo.com)
- **Beem Support**: [Beem Africa Support](https://login.beem.africa)

## 🔄 Updates

This documentation is regularly updated. Check the changelog for the latest changes.

---

**📱 Ready to send SMS?** Start with the test connection endpoint to verify your setup, then send your first SMS using the single SMS endpoint!
