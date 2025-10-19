# Simple API Endpoints Guide

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints require JWT token in the Authorization header:
```
Authorization: Bearer your_jwt_token_here
```

---

## 📱 SMS Endpoints

### Send SMS
**POST** `/messaging/sms/send/`

**Request Body:**
```json
{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["255757347863"],
  "sender_id": "Taarifa-SMS"
}
```

**Response:**
```json
{
  "success": true,
  "message": "SMS sent successfully via Beem",
  "data": {
    "message_id": "uuid",
    "provider": "beem",
    "recipient_count": 1,
    "cost_estimate": 0.05,
    "status": "sent"
  }
}
```

### Get SMS Balance
**GET** `/messaging/sms/balance/`

**Response:**
```json
{
  "success": true,
  "data": {
    "provider": "beem",
    "balance": "N/A",
    "currency": "USD"
  }
}
```

---

## 👥 Contact Management

### Get Contacts
**GET** `/messaging/contacts/`

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)
- `search` - Search in name, phone, or email

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "John Doe",
    "phone_e164": "+255700000001",
    "email": "john@example.com",
    "is_active": true,
    "is_opted_in": true,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Create Contact
**POST** `/messaging/contacts/`

**Request Body:**
```json
{
  "name": "Jane Smith",
  "phone_e164": "+255700000002",
  "email": "jane@example.com",
  "attributes": {
    "company": "ABC Corp",
    "department": "Sales"
  },
  "tags": ["vip", "customer"]
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Jane Smith",
  "phone_e164": "+255700000002",
  "email": "jane@example.com",
  "is_active": true,
  "is_opted_in": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Update Contact
**PUT** `/messaging/contacts/{id}/`

### Delete Contact
**DELETE** `/messaging/contacts/{id}/`

---

## 🏷️ Sender ID Management

### Get Sender IDs
**GET** `/messaging/sender-ids/`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "sender_id": "Taarifa-SMS",
      "sample_content": "Test content",
      "status": "active",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### Get Sender ID Requests
**GET** `/messaging/sender-requests/`

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Response:**
```json
[
  {
    "id": "uuid",
    "requested_sender_id": "MyCompany",
    "request_type": "custom",
    "status": "approved",
    "sample_content": "Test content",
    "business_justification": "For business communications",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

### Create Sender ID Request
**POST** `/messaging/sender-requests/`

**Request Body:**
```json
{
  "request_type": "custom",
  "requested_sender_id": "MyCompany",
  "sample_content": "This is a test message from MyCompany",
  "business_justification": "We need this sender ID for our business communications"
}
```

**Response:**
```json
{
  "id": "uuid",
  "requested_sender_id": "MyCompany",
  "request_type": "custom",
  "status": "pending",
  "sample_content": "This is a test message from MyCompany",
  "business_justification": "We need this sender ID for our business communications",
  "created_at": "2024-01-01T12:00:00Z"
}
```

---

## 💰 Billing Endpoints

### Get SMS Balance
**GET** `/billing/sms/balance/`

**Response:**
```json
{
  "success": true,
  "data": {
    "credits": 1000,
    "total_purchased": 1000,
    "total_used": 0,
    "currency": "TZS"
  }
}
```

### Get SMS Packages
**GET** `/billing/sms/packages/`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Starter Package",
    "credits": 100,
    "price": 5000,
    "unit_price": 50,
    "is_popular": false,
    "is_active": true
  }
]
```

### Get Purchase History
**GET** `/billing/sms/purchases/`

**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page
- `status` - Filter by status (pending, completed, failed)

---

## 🏢 Tenant Management

### Get Tenant Profile
**GET** `/tenants/profile/`

**Response:**
```json
{
  "id": "uuid",
  "name": "My Company",
  "subdomain": "mycompany",
  "business_name": "My Company Ltd",
  "email": "admin@mycompany.com",
  "phone_number": "+255700000000",
  "is_active": true
}
```

---

## 📊 Analytics

### Get Dashboard Overview
**GET** `/messaging/dashboard/overview/`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_contacts": 150,
    "total_messages_sent": 500,
    "total_sender_ids": 2,
    "sms_balance": 1000,
    "recent_activity": [...]
  }
}
```

---

## 🔧 Utility Endpoints

### Validate Phone Number
**POST** `/messaging/sms/validate-phone/`

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

### Test SMS Connection
**GET** `/messaging/sms/test-connection/`

**Response:**
```json
{
  "success": true,
  "message": "Connection test successful",
  "data": {
    "provider": "beem",
    "api_key_configured": true,
    "connection_status": "success"
  }
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message",
  "errors": {
    "field_name": ["Field-specific error message"]
  }
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
