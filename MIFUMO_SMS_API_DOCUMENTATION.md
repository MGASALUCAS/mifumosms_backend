# Mifumo SMS API Integration Guide – SMS Messaging Platform
## Secure SMS Messaging Integration for Tanzania

---

## **SMS API Endpoints**

### **Send SMS**
**URL:** `http://127.0.0.1:8001/api/integration/v1/sms/send/`  
**Method:** `POST`

#### **Authentication**
Include your API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```
**Note:** Replace `YOUR_API_KEY` with the key provided by Mifumo SMS.

#### **Request Body**
Submit the following JSON payload:
```json
{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789", "+255987654321"],
  "sender_id": "MIFUMO",
  "schedule_time": "2024-01-01T10:00:00Z"
}
```

#### **Parameter Descriptions**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | ✅ | SMS text content (max 160 characters) |
| `recipients` | array | ✅ | List of phone numbers in E.164 format |
| `sender_id` | string | ❌ | Custom sender ID (default: "MIFUMO") |
| `schedule_time` | string | ❌ | ISO 8601 datetime for scheduled sending |

#### **Sample cURL Request**
```bash
curl -X POST "http://127.0.0.1:8001/api/integration/v1/sms/send/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_API_KEY" \
-d '{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789"],
  "sender_id": "MIFUMO"
}'
```

#### **Successful Response**
```json
{
  "success": true,
  "message": "SMS sent successfully",
  "data": {
    "message_id": "msg_123456789",
    "recipients": ["+255123456789"],
    "status": "sent",
    "cost": 10.0,
    "currency": "TZS"
  },
  "error_code": null,
  "details": null
}
```

#### **Error Response**
```json
{
  "success": false,
  "message": "Invalid API Key or request payload",
  "data": null,
  "error_code": "INVALID_CREDENTIALS",
  "details": "The provided API key is invalid or expired"
}
```

---

### **Get Message Status**
**URL:** `http://127.0.0.1:8001/api/integration/v1/sms/status/{message_id}/`  
**Method:** `GET`

#### **Sample Request**
```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/status/msg_123456789/" \
-H "Authorization: Bearer YOUR_API_KEY"
```

#### **Sample Response**
```json
{
  "success": true,
  "message": "Message status retrieved successfully",
  "data": {
    "message_id": "msg_123456789",
    "status": "delivered",
    "delivery_time": "2024-01-01T10:05:00Z",
    "recipients": [
      {
        "phone": "+255123456789",
        "status": "delivered",
        "delivery_time": "2024-01-01T10:05:00Z"
      }
    ]
  }
}
```

---

### **Get Delivery Reports**
**URL:** `http://127.0.0.1:8001/api/integration/v1/sms/delivery-reports/`  
**Method:** `GET`

#### **Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | ❌ | Start date (ISO 8601 format) |
| `end_date` | string | ❌ | End date (ISO 8601 format) |
| `status` | string | ❌ | Filter by status (sent, delivered, failed) |
| `page` | integer | ❌ | Page number (default: 1) |
| `per_page` | integer | ❌ | Items per page (default: 50) |

#### **Sample Request**
```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/delivery-reports/?start_date=2024-01-01T00:00:00Z&status=delivered" \
-H "Authorization: Bearer YOUR_API_KEY"
```

---

### **Get Account Balance**
**URL:** `http://127.0.0.1:8001/api/integration/v1/sms/balance/`  
**Method:** `GET`

#### **Sample Request**
```bash
curl -X GET "http://127.0.0.1:8001/api/integration/v1/sms/balance/" \
-H "Authorization: Bearer YOUR_API_KEY"
```

#### **Sample Response**
```json
{
  "success": true,
  "message": "Balance retrieved successfully",
  "data": {
    "balance": 5000.0,
    "currency": "TZS",
    "last_updated": "2024-01-01T10:00:00Z"
  }
}
```

---

## **Contacts API Endpoints**

### **Create Contact**
**URL:** `http://127.0.0.1:8001/api/integration/v1/contacts/create/`  
**Method:** `POST`

#### **Request Body**
```json
{
  "name": "John Doe",
  "phone_number": "+255123456789",
  "email": "john@example.com",
  "tags": ["customer", "vip"],
  "is_active": true
}
```

#### **Parameter Descriptions**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ | Contact's full name |
| `phone_number` | string | ✅ | Phone number in E.164 format |
| `email` | string | ❌ | Email address |
| `tags` | array | ❌ | List of tags for categorization |
| `is_active` | boolean | ❌ | Whether contact is active (default: true) |

---

### **Search Contacts**
**URL:** `http://127.0.0.1:8001/api/integration/v1/contacts/search/`  
**Method:** `GET`

#### **Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | ❌ | Search query (name, phone, email) |
| `limit` | integer | ❌ | Maximum results (default: 20) |
| `offset` | integer | ❌ | Results offset (default: 0) |
| `segment_id` | string | ❌ | Filter by segment ID |

---

## **Segments API Endpoints**

### **Create Segment**
**URL:** `http://127.0.0.1:8001/api/integration/v1/contacts/segments/create/`  
**Method:** `POST`

#### **Request Body**
```json
{
  "name": "VIP Customers",
  "description": "High-value customers",
  "criteria": {
    "tags": ["vip", "premium"],
    "is_active": true,
    "created_after": "2024-01-01"
  }
}
```

---

## **Webhook Notifications**

Mifumo SMS can send automatic notifications to your server when SMS status changes.

### **Webhook Setup**
Include the `webhook_url` parameter in your SMS request to receive status updates:
```json
{
  "message": "Hello from Mifumo SMS!",
  "recipients": ["+255123456789"],
  "sender_id": "MIFUMO",
  "webhook_url": "https://your-domain.com/sms-webhook"
}
```

### **Webhook Authentication**
Mifumo SMS will send the `Authorization: Bearer YOUR_API_KEY` in the request header when calling your webhook URL. Verify this key to ensure the request is legitimate.

### **Webhook Payload Example**
```json
{
  "message_id": "msg_123456789",
  "status": "delivered",
  "recipients": [
    {
      "phone": "+255123456789",
      "status": "delivered",
      "delivery_time": "2024-01-01T10:05:00Z"
    }
  ],
  "metadata": {
    "sender_id": "MIFUMO",
    "cost": 10.0,
    "currency": "TZS"
  }
}
```

**Note:** Webhooks are triggered when SMS status changes to `delivered`, `failed`, or `sent`.

---

## **API Key Management**

### **Dashboard Access**
**URL:** `http://127.0.0.1:8001/api/integration/dashboard/`

Access your API dashboard to:
- Generate new API keys
- View usage statistics
- Manage webhooks
- Monitor account activity

### **API Key Permissions**
- `read`: View data and reports
- `write`: Send SMS and manage contacts
- `admin`: Full account management

---

## **Error Codes**

| Code | Description |
|------|-------------|
| `INVALID_CREDENTIALS` | Invalid or expired API key |
| `INVALID_PHONE` | Invalid phone number format |
| `INSUFFICIENT_BALANCE` | Account balance too low |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INVALID_SENDER_ID` | Sender ID not approved |
| `MESSAGE_TOO_LONG` | SMS exceeds character limit |

---

## **Rate Limits**

- **SMS Sending**: 100 messages per minute
- **API Calls**: 1000 requests per hour
- **Contact Management**: 500 operations per hour

---

## **Support**

For assistance, contact:
- **Email**: support@mifumosms.com
- **Website**: http://127.0.0.1:8001
- **Documentation**: http://127.0.0.1:8001/api/integration/documentation/

---

**Mifumo SMS Team**  
*Simplifying SMS Communication in Tanzania*
