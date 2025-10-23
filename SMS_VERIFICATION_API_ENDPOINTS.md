# SMS Verification API Endpoints

## Overview

This document provides comprehensive API endpoints for SMS-based verification, password reset, and account confirmation using Taarifa-SMS service.

## Base URL
```
http://127.0.0.1:8001/api/auth/
```

## Authentication
Most endpoints require JWT authentication:
```javascript
headers: {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
}
```

---

## 1. User Registration with SMS Verification

**Endpoint:** `POST /api/auth/register/`

**Purpose:** Register a new user and automatically send SMS verification code

### Request Body:
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+255700000001",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "timezone": "UTC"
}
```

### JSON Response (Success):
```json
{
  "message": "User created successfully. Please verify your account.",
  "user": {
    "id": 82,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "short_name": "John",
    "phone_number": "+255700000001",
    "timezone": "UTC",
    "avatar": null,
    "bio": "",
    "is_verified": false,
    "email_notifications": true,
    "sms_notifications": false,
    "created_at": "2025-10-23T04:13:32.480562+03:00",
    "updated_at": "2025-10-23T04:13:33.009925+03:00",
    "last_login_at": null
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "sms_verification": {
    "sent": true,
    "phone_number": "+255700000001",
    "message": "Verification code sent to your phone number."
  }
}
```

---

## 2. Send Verification Code

**Endpoint:** `POST /api/auth/sms/send-code/`

**Purpose:** Send SMS verification code to user's phone number

### Request Body:
```json
{
  "phone_number": "+255700000001",
  "message_type": "verification"
}
```

### Message Types:
- `verification` - General verification
- `password_reset` - Password reset verification
- `account_confirmation` - Account confirmation verification

### JSON Response (Success):
```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+255700000001"
}
```

### JSON Response (Error):
```json
{
  "success": false,
  "error": "Invalid api_key and/or secret_id"
}
```

---

## 3. Verify Phone Code

**Endpoint:** `POST /api/auth/sms/verify-code/`

**Purpose:** Verify SMS verification code

### Request Body:
```json
{
  "phone_number": "+255700000001",
  "verification_code": "123456"
}
```

### JSON Response (Success):
```json
{
  "success": true,
  "message": "Phone number verified successfully",
  "phone_verified": true
}
```

### JSON Response (Error):
```json
{
  "success": false,
  "error": "Invalid verification code. Please try again.",
  "attempts_remaining": 4
}
```

---

## 4. Forgot Password via SMS

**Endpoint:** `POST /api/auth/sms/forgot-password/`

**Purpose:** Send password reset code via SMS

### Request Body:
```json
{
  "phone_number": "+255700000001"
}
```

### JSON Response (Success):
```json
{
  "success": true,
  "message": "Password reset code sent to your phone number",
  "phone_number": "+255700000001"
}
```

### JSON Response (Error):
```json
{
  "success": false,
  "error": "No account found with this phone number."
}
```

---

## 5. Reset Password via SMS

**Endpoint:** `POST /api/auth/sms/reset-password/`

**Purpose:** Reset password using SMS verification code

### Request Body:
```json
{
  "phone_number": "+255700000001",
  "verification_code": "123456",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

### JSON Response (Success):
```json
{
  "success": true,
  "message": "Password reset successfully. You can now login with your new password."
}
```

### JSON Response (Error):
```json
{
  "success": false,
  "error": "Invalid verification code",
  "attempts_remaining": 3
}
```

---

## 6. Confirm Account via SMS

**Endpoint:** `POST /api/auth/sms/confirm-account/`

**Purpose:** Confirm user account using SMS verification code

**Authentication:** Required

### Request Body:
```json
{
  "verification_code": "123456"
}
```

### JSON Response (Success):
```json
{
  "success": true,
  "message": "Account confirmed successfully",
  "is_verified": true,
  "phone_verified": true
}
```

### JSON Response (Error):
```json
{
  "success": false,
  "error": "No verification code found. Please request a new code.",
  "attempts_remaining": 0
}
```

---

## SMS Verification Features

### Security Features:
- **Rate Limiting**: Maximum 5 verification attempts before temporary lockout
- **Code Expiration**: Verification codes expire after 10 minutes
- **Lockout Period**: 30-minute lockout after 5 failed attempts
- **Code Format**: 6-digit numeric codes only

### Phone Number Format:
- **Required Format**: International format with country code
- **Example**: `+255700000001` (Tanzania)
- **Validation**: Basic phone number format validation

### Verification Code Messages:
- **Account Confirmation**: "Your Mifumo WMS account confirmation code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."
- **Password Reset**: "Your Mifumo WMS password reset code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."
- **General Verification**: "Your Mifumo WMS verification code is: {code}. This code expires in 10 minutes. Do not share this code with anyone."

---

## Frontend Integration Examples

### JavaScript - Complete Registration Flow

```javascript
// 1. Register user
const registerUser = async (userData) => {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  
  const result = await response.json();
  
  if (result.sms_verification.sent) {
    // Show verification form
    showVerificationForm(result.user.phone_number);
  }
  
  return result;
};

// 2. Verify phone number
const verifyPhone = async (phoneNumber, code) => {
  const response = await fetch('/api/auth/sms/verify-code/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      phone_number: phoneNumber,
      verification_code: code
    })
  });
  
  return await response.json();
};

// 3. Confirm account
const confirmAccount = async (code, token) => {
  const response = await fetch('/api/auth/sms/confirm-account/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      verification_code: code
    })
  });
  
  return await response.json();
};
```

### JavaScript - Password Reset Flow

```javascript
// 1. Request password reset
const requestPasswordReset = async (phoneNumber) => {
  const response = await fetch('/api/auth/sms/forgot-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      phone_number: phoneNumber
    })
  });
  
  return await response.json();
};

// 2. Reset password
const resetPassword = async (phoneNumber, code, newPassword) => {
  const response = await fetch('/api/auth/sms/reset-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      phone_number: phoneNumber,
      verification_code: code,
      new_password: newPassword,
      new_password_confirm: newPassword
    })
  });
  
  return await response.json();
};
```

### JavaScript - Send Verification Code

```javascript
const sendVerificationCode = async (phoneNumber, messageType = 'verification') => {
  const response = await fetch('/api/auth/sms/send-code/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      phone_number: phoneNumber,
      message_type: messageType
    })
  });
  
  return await response.json();
};
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Phone number is required."
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "No account found with this phone number."
}
```

### 429 Too Many Requests (Rate Limited)
```json
{
  "success": false,
  "error": "Phone verification is temporarily locked. Please try again later.",
  "locked_until": "2025-10-23T04:45:00Z"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Invalid api_key and/or secret_id"
}
```

---

## Configuration Requirements

### Environment Variables
```env
# Beem Africa SMS Configuration
BEEM_API_KEY=your-beem-api-key
BEEM_SECRET_KEY=your-beem-secret-key
BEEM_DEFAULT_SENDER_ID=Taarifa-SMS
BEEM_API_TIMEOUT=30
```

### Database Migration
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

---

## Testing

### Test Script
```bash
python test_sms_verification.py
```

### Manual Testing
1. Register a user with phone number
2. Check if SMS verification code is sent
3. Verify the code
4. Test password reset flow
5. Test account confirmation

---

## Security Considerations

1. **Rate Limiting**: Prevents brute force attacks
2. **Code Expiration**: Limits window of opportunity for attacks
3. **Lockout Mechanism**: Temporary account lockout after failed attempts
4. **Secure Code Generation**: Random 6-digit codes
5. **Phone Number Validation**: Basic format validation
6. **JWT Authentication**: Secure token-based authentication

---

## Status Codes Summary

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (Registration) |
| 400 | Bad Request (Validation Error) |
| 401 | Unauthorized (Authentication Required) |
| 404 | Not Found (User/Phone Not Found) |
| 429 | Too Many Requests (Rate Limited) |
| 500 | Internal Server Error (SMS Service Error) |
