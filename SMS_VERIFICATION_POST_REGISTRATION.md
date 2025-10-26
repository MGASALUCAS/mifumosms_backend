# SMS Verification After Registration - Complete Guide

## Overview

When a user registers with a phone number, they automatically receive an SMS verification code. This guide explains how to verify the account using that code.

## Registration Flow

### 1. Register User
**Endpoint:** `POST /api/auth/register/`

**Request:**
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

**Response:**
```json
{
  "message": "User created successfully. Please check your phone for SMS verification code.",
  "user": {
    "id": 82,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+255700000001",
    "is_verified": false,
    ...
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "sms_verification_sent": true
}
```

**Important:** Save the `access` token for verification.

---

## Verification Methods

### Method 1: Confirm Account (Recommended)

**Endpoint:** `POST /api/auth/sms/confirm-account/`

**Authentication:** Required (use the access token from registration)

**Request Body:**
```json
{
  "verification_code": "123456"
}
```

**Headers:**
```javascript
{
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  'Content-Type': 'application/json'
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Account confirmed successfully",
  "is_verified": true,
  "phone_verified": true
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Invalid verification code. Please try again.",
  "attempts_remaining": 4
}
```

---

### Method 2: Verify Phone Code (Alternative)

**Endpoint:** `POST /api/auth/sms/verify-code/`

**Authentication:** Optional (uses phone number lookup if not authenticated)

**Request Body:**
```json
{
  "phone_number": "+255700000001",
  "verification_code": "123456"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Phone number verified successfully",
  "phone_verified": true
}
```

---

## Resend Verification Code

If the user didn't receive the code or it expired, you can resend it.

**Endpoint:** `POST /api/auth/sms/send-code/`

**Request Body:**
```json
{
  "phone_number": "+255700000001",
  "message_type": "account_confirmation"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+255700000001"
}
```

---

## Frontend Integration Example

### Complete Registration and Verification Flow

```javascript
// 1. Register the user
const handleRegistration = async (userData) => {
  try {
    const response = await fetch('http://127.0.0.1:8001/api/auth/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });
    
    const result = await response.json();
    
    if (result.sms_verification_sent) {
      // Save tokens
      localStorage.setItem('accessToken', result.tokens.access);
      localStorage.setItem('refreshToken', result.tokens.refresh);
      
      // Show verification form
      showVerificationModal();
      
      return result;
    } else {
      throw new Error('Failed to send verification SMS');
    }
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

// 2. Verify the account
const handleVerification = async (verificationCode) => {
  try {
    const accessToken = localStorage.getItem('accessToken');
    
    const response = await fetch('http://127.0.0.1:8001/api/auth/sms/confirm-account/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        verification_code: verificationCode
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Account verified successfully
      // Redirect to dashboard or show success message
      window.location.href = '/dashboard';
      return result;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Verification error:', error);
    throw error;
  }
};

// 3. Resend verification code if needed
const handleResendCode = async (phoneNumber) => {
  try {
    const response = await fetch('http://127.0.0.1:8001/api/auth/sms/send-code/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone_number: phoneNumber,
        message_type: 'account_confirmation'
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      alert('Verification code has been resent to your phone');
    }
    
    return result;
  } catch (error) {
    console.error('Resend code error:', error);
    throw error;
  }
};
```

---

## React Component Example

```jsx
import React, { useState } from 'react';

const RegistrationFlow = () => {
  const [step, setStep] = useState('register');
  const [registrationData, setRegistrationData] = useState({});
  const [verificationCode, setVerificationCode] = useState('');
  const [message, setMessage] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://127.0.0.1:8001/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registrationData)
      });
      
      const result = await response.json();
      
      if (result.sms_verification_sent) {
        localStorage.setItem('accessToken', result.tokens.access);
        setStep('verify');
        setMessage(`Verification code sent to ${result.user.phone_number}`);
      }
    } catch (error) {
      setMessage('Registration failed: ' + error.message);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    try {
      const accessToken = localStorage.getItem('accessToken');
      
      const response = await fetch('http://127.0.0.1:8001/api/auth/sms/confirm-account/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ verification_code: verificationCode })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMessage('Account verified successfully! Redirecting...');
        setTimeout(() => window.location.href = '/dashboard', 2000);
      } else {
        setMessage(`Error: ${result.error} (${result.attempts_remaining} attempts remaining)`);
      }
    } catch (error) {
      setMessage('Verification failed: ' + error.message);
    }
  };

  return (
    <div>
      {step === 'register' && (
        <form onSubmit={handleRegister}>
          <input
            type="email"
            placeholder="Email"
            onChange={(e) => setRegistrationData({...registrationData, email: e.target.value})}
          />
          <input
            type="text"
            placeholder="Phone (+255700000001)"
            onChange={(e) => setRegistrationData({...registrationData, phone_number: e.target.value})}
          />
          <input
            type="password"
            placeholder="Password"
            onChange={(e) => setRegistrationData({...registrationData, password: e.target.value})}
          />
          <input
            type="password"
            placeholder="Confirm Password"
            onChange={(e) => setRegistrationData({...registrationData, password_confirm: e.target.value})}
          />
          <button type="submit">Register</button>
        </form>
      )}
      
      {step === 'verify' && (
        <form onSubmit={handleVerify}>
          <input
            type="text"
            placeholder="Enter 6-digit code"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
          />
          <button type="submit">Verify</button>
        </form>
      )}
      
      <p>{message}</p>
    </div>
  );
};

export default RegistrationFlow;
```

---

## Security Features

### Rate Limiting
- **Maximum Attempts:** 5 failed attempts
- **Lockout Period:** 30 minutes after reaching max attempts
- **Attempt Tracking:** Shows `attempts_remaining` in error responses

### Code Expiration
- **Valid For:** 10 minutes
- **Format:** 6-digit numeric code
- **Auto-clear:** Cleared after successful verification

### Error Handling
```javascript
// Handle different error cases
if (response.status === 400) {
  const error = await response.json();
  
  if (error.error.includes('expired')) {
    // Code has expired, offer to resend
    showResendButton();
  } else if (error.error.includes('locked')) {
    // Phone is temporarily locked
    showLockoutMessage(error.locked_until);
  } else if (error.attempts_remaining !== undefined) {
    // Show attempts remaining
    showAttemptsRemaining(error.attempts_remaining);
  }
}
```

---

## Testing

### Using cURL

```bash
# 1. Register user
curl -X POST http://127.0.0.1:8001/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+255700000001",
    "password": "password123",
    "password_confirm": "password123",
    "timezone": "UTC"
  }'

# 2. Verify account (use access token from step 1)
curl -X POST http://127.0.0.1:8001/api/auth/sms/confirm-account/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "verification_code": "123456"
  }'
```

---

## Base URL

**Development:** `http://127.0.0.1:8001/api/auth/`

**Production:** `https://your-domain.com/api/auth/`

---

## Summary

1. **Register** → User gets SMS code and JWT tokens
2. **Verify** → Use `/api/auth/sms/confirm-account/` with code and access token
3. **Done** → Account is verified and `is_verified` flag is set to `true`

