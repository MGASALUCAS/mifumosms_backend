# 📱 SMS API Response Documentation

## Overview

This document provides comprehensive examples of all SMS API responses for the Mifumo WMS platform. Use this as a reference for frontend integration and error handling.

## 🔗 Base URL

```
http://127.0.0.1:8000/api/messaging/sms/
```

## 🔐 Authentication

All endpoints require JWT authentication:

```http
Authorization: Bearer your-jwt-token
```

---

## 1. Send SMS Endpoint

### `POST /api/messaging/sms/send/`

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

### ✅ Success Response (200)

```json
{
  "success": true,
  "message": "SMS sent successfully",
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "provider": "beem",
    "recipients": [
      {
        "phone": "255700000001",
        "status": "sent",
        "provider_message_id": "beem_12345"
      },
      {
        "phone": "255700000002",
        "status": "sent",
        "provider_message_id": "beem_12346"
      }
    ],
    "total_recipients": 2,
    "successful_sends": 2,
    "failed_sends": 0,
    "cost": 0.02,
    "currency": "USD",
    "scheduled_time": null,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### ❌ Error Responses

#### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "message": ["This field is required."],
    "recipients": ["This field is required."],
    "sender_id": ["This field is required."]
  }
}
```

#### Invalid Phone Number (400)
```json
{
  "success": false,
  "message": "Invalid phone number format",
  "errors": {
    "recipients": ["Phone number must be in international format (e.g., 255700000001)"]
  }
}
```

#### Sender ID Not Registered (400)
```json
{
  "success": false,
  "message": "Sender ID not registered or inactive",
  "errors": {
    "sender_id": ["Sender ID 'INVALID' is not registered with Beem Africa"]
  }
}
```

#### Provider Error (500)
```json
{
  "success": false,
  "message": "SMS provider error",
  "error": "Beem Africa API returned error: Insufficient balance"
}
```

---

## 2. Get SMS Balance Endpoint

### `GET /api/messaging/sms/balance/`

### ✅ Success Response (200)

```json
{
  "success": true,
  "data": {
    "provider": "beem",
    "balance": 150.75,
    "currency": "USD",
    "last_updated": "2024-01-01T10:00:00Z",
    "account_status": "active"
  }
}
```

### ❌ Error Response (500)

```json
{
  "success": false,
  "message": "Failed to fetch balance",
  "error": "Beem Africa API error: Invalid credentials"
}
```

---

## 3. Get SMS Statistics Endpoint

### `GET /api/messaging/sms/stats/`

### ✅ Success Response (200)

```json
{
  "success": true,
  "data": {
    "total_sent": 1250,
    "total_delivered": 1180,
    "total_failed": 70,
    "delivery_rate": 94.4,
    "total_cost": 25.00,
    "currency": "USD",
    "period": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-31T23:59:59Z"
    },
    "by_status": {
      "sent": 1250,
      "delivered": 1180,
      "failed": 70,
      "pending": 0
    },
    "by_provider": {
      "beem": 1250
    }
  }
}
```

---

## 4. Test Connection Endpoint

### `GET /api/messaging/sms/test-connection/`

### ✅ Success Response (200)

```json
{
  "success": true,
  "message": "SMS provider connection successful",
  "data": {
    "provider": "beem",
    "status": "connected",
    "response_time": 0.25,
    "api_version": "v1",
    "last_checked": "2024-01-01T10:00:00Z"
  }
}
```

### ❌ Error Response (500)

```json
{
  "success": false,
  "message": "SMS provider connection failed",
  "error": "Beem Africa API error: Invalid API key"
}
```

---

## 5. Validate Phone Number Endpoint

### `POST /api/messaging/sms/validate-phone/`

**Request Body:**
```json
{
  "phone": "255700000001"
}
```

### ✅ Success Response (200)

```json
{
  "success": true,
  "message": "Phone number is valid",
  "data": {
    "phone": "255700000001",
    "is_valid": true,
    "formatted": "+255700000001",
    "country_code": "255",
    "national_number": "700000001",
    "country": "Tanzania",
    "carrier": "Vodacom"
  }
}
```

### ❌ Error Response (400)

```json
{
  "success": false,
  "message": "Phone number is invalid",
  "errors": {
    "phone": ["Invalid phone number format. Use international format (e.g., 255700000001)"]
  }
}
```

---

## 6. Get SMS Delivery Status Endpoint

### `GET /api/messaging/sms/{message_id}/status/`

### ✅ Success Response (200)

```json
{
  "success": true,
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "delivered",
    "provider": "beem",
    "provider_message_id": "beem_12345",
    "delivery_time": "2024-01-01T10:01:30Z",
    "cost": 0.01,
    "currency": "USD",
    "recipients": [
      {
        "phone": "255700000001",
        "status": "delivered",
        "delivery_time": "2024-01-01T10:01:30Z",
        "error_code": null,
        "error_message": null
      }
    ]
  }
}
```

### ❌ Error Response (404)

```json
{
  "success": false,
  "message": "Message not found",
  "error": "Message with ID '550e8400-e29b-41d4-a716-446655440000' not found"
}
```

---

## 7. Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "error": "An unexpected error occurred"
}
```

---

## 8. Frontend Integration Examples

### JavaScript/TypeScript

```javascript
// Send SMS
async function sendSMS(message, recipients, senderId) {
  try {
    const response = await fetch('/api/messaging/sms/send/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        recipients: recipients,
        sender_id: senderId
      })
    });

    const data = await response.json();

    if (data.success) {
      console.log('SMS sent successfully:', data.data);
      return { success: true, data: data.data };
    } else {
      console.error('SMS send failed:', data.message, data.errors);
      return { success: false, error: data.message, errors: data.errors };
    }
  } catch (error) {
    console.error('SMS send error:', error);
    return { success: false, error: 'Network error' };
  }
}

// Get SMS Balance
async function getSMSBalance() {
  try {
    const response = await fetch('/api/messaging/sms/balance/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`
      }
    });

    const data = await response.json();

    if (data.success) {
      return { success: true, balance: data.data.balance, currency: data.data.currency };
    } else {
      return { success: false, error: data.message };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
}

// Validate Phone Number
async function validatePhoneNumber(phone) {
  try {
    const response = await fetch('/api/messaging/sms/validate-phone/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ phone: phone })
    });

    const data = await response.json();

    if (data.success) {
      return { success: true, isValid: data.data.is_valid, formatted: data.data.formatted };
    } else {
      return { success: false, error: data.message, errors: data.errors };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
}
```

### React Hook Example

```javascript
import { useState, useEffect } from 'react';

function useSMSAPI() {
  const [balance, setBalance] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendSMS = async (message, recipients, senderId) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/messaging/sms/send/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message,
          recipients,
          sender_id: senderId
        })
      });

      const data = await response.json();

      if (data.success) {
        return { success: true, data: data.data };
      } else {
        setError(data.message);
        return { success: false, error: data.message, errors: data.errors };
      }
    } catch (err) {
      setError('Network error');
      return { success: false, error: 'Network error' };
    } finally {
      setLoading(false);
    }
  };

  const fetchBalance = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/messaging/sms/balance/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      const data = await response.json();

      if (data.success) {
        setBalance(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/messaging/sms/stats/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      const data = await response.json();

      if (data.success) {
        setStats(data.data);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return {
    balance,
    stats,
    loading,
    error,
    sendSMS,
    fetchBalance,
    fetchStats
  };
}

export default useSMSAPI;
```

---

## 9. Error Handling Best Practices

### 1. Always Check Response Status
```javascript
if (response.ok) {
  const data = await response.json();
  // Handle success
} else {
  const errorData = await response.json();
  // Handle error
}
```

### 2. Handle Different Error Types
```javascript
switch (response.status) {
  case 400:
    // Validation errors
    console.error('Validation error:', errorData.errors);
    break;
  case 401:
    // Authentication error
    console.error('Authentication required');
    break;
  case 403:
    // Permission error
    console.error('Permission denied');
    break;
  case 500:
    // Server error
    console.error('Server error:', errorData.message);
    break;
  default:
    console.error('Unknown error:', errorData);
}
```

### 3. User-Friendly Error Messages
```javascript
function getErrorMessage(errorData) {
  if (errorData.errors) {
    // Validation errors
    return Object.values(errorData.errors).flat().join(', ');
  } else if (errorData.message) {
    // API error message
    return errorData.message;
  } else {
    // Generic error
    return 'An unexpected error occurred';
  }
}
```

---

## 10. Testing the API

### Using curl

```bash
# Send SMS
curl -X POST http://127.0.0.1:8000/api/messaging/sms/send/ \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message",
    "recipients": ["255700000001"],
    "sender_id": "MIFUMO"
  }'

# Get Balance
curl -X GET http://127.0.0.1:8000/api/messaging/sms/balance/ \
  -H "Authorization: Bearer your-jwt-token"

# Test Connection
curl -X GET http://127.0.0.1:8000/api/messaging/sms/test-connection/ \
  -H "Authorization: Bearer your-jwt-token"
```

### Using Postman

1. Set the base URL: `http://127.0.0.1:8000/api/messaging/sms/`
2. Add Authorization header: `Bearer your-jwt-token`
3. Set Content-Type: `application/json` for POST requests
4. Use the request bodies provided in this documentation

---

## 11. Status Codes Reference

| Status Code | Meaning | When It Occurs |
|-------------|---------|----------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Validation errors, invalid data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | User lacks permission |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side error |

---

## 12. Support

For additional support or questions about the SMS API:

- Check the API documentation at `/swagger/`
- Review the error messages in the response
- Ensure your JWT token is valid and not expired
- Verify the request format matches the examples above

---

**Last Updated:** January 2024
**Version:** 1.0.0
