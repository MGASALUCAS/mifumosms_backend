# API Endpoints - JSON Responses

## 🔗 Base URL
```
http://127.0.0.1:8000/api
```

## 📡 Authentication
All endpoints require JWT token in header:
```json
{
  "Authorization": "Bearer your_jwt_token_here"
}
```

---

## 🆕 New Endpoints

### 1. **Create Sender ID Request**
**POST** `/messaging/sender-requests/requests/`

**Request Body:**
```json
{
  "request_type": "default",
  "requested_sender_id": "Taarifa-SMS",
  "sample_content": "A test use case for the sender name purposely used for information transfer.",
  "business_justification": "I need this sender ID for my business SMS communications."
}
```

**Success Response (201):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "request_type": "default",
  "requested_sender_id": "Taarifa-SMS",
  "sample_content": "A test use case for the sender name purposely used for information transfer.",
  "business_justification": "I need this sender ID for my business SMS communications.",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Response (400):**
```json
{
  "business_justification": ["This field is required."]
}
```

---

### 2. **Get Sender ID Requests**
**GET** `/messaging/sender-requests/requests/`

**Success Response (200):**
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "requested_sender_id": "Taarifa-SMS",
    "status": "pending",
    "created_at": "2024-01-01T12:00:00Z"
  },
  {
    "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "requested_sender_id": "Taarifa-SMS",
    "status": "approved",
    "created_at": "2024-01-01T11:00:00Z"
  }
]
```

---

### 3. **Get Sender ID Request Details**
**GET** `/messaging/sender-requests/requests/{id}/`

**Success Response (200):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "request_type": "default",
  "requested_sender_id": "Taarifa-SMS",
  "sample_content": "A test use case for the sender name purposely used for information transfer.",
  "business_justification": "I need this sender ID for my business SMS communications.",
  "status": "pending",
  "admin_notes": "",
  "rejection_reason": "",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

---

### 4. **Update Sender ID Request**
**PUT** `/messaging/sender-requests/requests/{id}/`

**Request Body:**
```json
{
  "sample_content": "Updated sample content for testing",
  "business_justification": "Updated business justification"
}
```

**Success Response (200):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "request_type": "default",
  "requested_sender_id": "Taarifa-SMS",
  "sample_content": "Updated sample content for testing",
  "business_justification": "Updated business justification",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:30:00Z"
}
```

---

### 5. **Approve Sender ID Request (Admin)**
**POST** `/messaging/sender-requests/requests/{id}/review/`

**Request Body:**
```json
{
  "status": "approved",
  "admin_notes": "Approved for business use"
}
```

**Success Response (200):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "requested_sender_id": "Taarifa-SMS",
  "status": "approved",
  "admin_notes": "Approved for business use",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

---

### 6. **Reject Sender ID Request (Admin)**
**POST** `/messaging/sender-requests/requests/{id}/review/`

**Request Body:**
```json
{
  "status": "rejected",
  "rejection_reason": "Insufficient business justification provided"
}
```

**Success Response (200):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "requested_sender_id": "Taarifa-SMS",
  "status": "rejected",
  "rejection_reason": "Insufficient business justification provided",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

---

### 7. **Get Sender ID Status & SMS Balance**
**GET** `/messaging/sender-requests/status/`

**Success Response (200):**
```json
{
  "sms_balance": {
    "credits": 100,
    "total_purchased": 500,
    "total_used": 400,
    "can_request_sender_id": true
  },
  "sender_id_requests": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "requested_sender_id": "Taarifa-SMS",
      "status": "approved",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

## 🔄 Updated Endpoints

### 8. **Update User Profile (Fixed)**
**PUT** `/auth/profile/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+255700000000",
  "timezone": "UTC",
  "bio": "User bio information",
  "email_notifications": true,
  "sms_notifications": false
}
```

**Success Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone_number": "+255700000000",
  "timezone": "UTC",
  "bio": "User bio information",
  "email_notifications": true,
  "sms_notifications": false,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Validation Error Response (400):**
```json
{
  "email": ["A user with this email already exists."],
  "first_name": ["This field may not be blank."],
  "last_name": ["This field may not be blank."],
  "email_notifications": ["Must be a boolean value."],
  "sms_notifications": ["Must be a boolean value."]
}
```

---

## 📊 Status Values

### **Sender ID Request Status:**
- `pending` - Waiting for admin approval
- `approved` - Approved by admin
- `rejected` - Rejected by admin

### **Request Types:**
- `default` - Default sender ID request (Taarifa-SMS)

---

## 🔐 Error Responses

### **401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### **404 Not Found:**
```json
{
  "detail": "Not found."
}
```

### **500 Internal Server Error:**
```json
{
  "detail": "A server error occurred."
}
```

---

## 📝 Example Usage

### **JavaScript Fetch Example:**
```javascript
// Create sender ID request
const createRequest = async () => {
  const response = await fetch('/api/messaging/sender-requests/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      request_type: 'default',
      requested_sender_id: 'Taarifa-SMS',
      sample_content: 'A test use case for the sender name...',
      business_justification: 'I need this for my business'
    })
  });
  
  const data = await response.json();
  console.log(data);
};

// Check status
const checkStatus = async () => {
  const response = await fetch('/api/messaging/sender-requests/status/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  console.log('SMS Credits:', data.sms_balance.credits);
  console.log('Sender ID Status:', data.sender_id_requests[0]?.status);
};
```

---

## ✅ Summary

**New Endpoints Added:**
- `POST /messaging/sender-requests/` - Create request
- `GET /messaging/sender-requests/` - List requests
- `GET /messaging/sender-requests/{id}/` - Get request details
- `PUT /messaging/sender-requests/{id}/` - Update request
- `POST /messaging/sender-requests/{id}/approve/` - Approve (Admin)
- `POST /messaging/sender-requests/{id}/reject/` - Reject (Admin)
- `GET /messaging/sender-requests/status/` - Get status & balance

**Fixed Endpoints:**
- `PUT /auth/profile/` - Profile update with better validation

**All endpoints return JSON responses with proper error handling.**
