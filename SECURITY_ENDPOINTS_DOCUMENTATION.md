# Security Settings API Endpoints & JSON Responses

## 🔐 **Base URL**
```
http://127.0.0.1:8001/api/auth/security/
```

## 📋 **Authentication Required**
All endpoints require JWT authentication:
```http
Authorization: Bearer <your_jwt_token>
```

---

## 1. **Security Summary**
```http
GET /api/auth/security/summary/
```

### **Response:**
```json
{
  "success": true,
  "data": {
    "two_factor_enabled": false,
    "active_sessions": 1,
    "recent_events_count": 5,
    "last_password_change": "2025-10-23T10:30:00.000Z",
    "security_score": 75
  }
}
```

---

## 2. **Change Password**
```http
POST /api/auth/security/change-password/
```

### **Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

### **Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### **Error Response:**
```json
{
  "success": false,
  "errors": {
    "current_password": ["Current password is incorrect."],
    "new_password": ["This password is too common."]
  }
}
```

---

## 3. **Two-Factor Authentication Status**
```http
GET /api/auth/security/2fa/status/
```

### **Response (2FA Disabled):**
```json
{
  "success": true,
  "data": {
    "id": "2fa-uuid-here",
    "is_enabled": false,
    "created_at": "2025-10-23T10:30:00.000Z",
    "updated_at": "2025-10-23T10:30:00.000Z",
    "qr_code_data": {
      "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
      "secret_key": "JBSWY3DPEHPK3PXP",
      "manual_entry_key": "JBSWY3DPEHPK3PXP"
    },
    "backup_codes": null
  }
}
```

### **Response (2FA Enabled):**
```json
{
  "success": true,
  "data": {
    "id": "2fa-uuid-here",
    "is_enabled": true,
    "created_at": "2025-10-23T10:30:00.000Z",
    "updated_at": "2025-10-23T10:35:00.000Z",
    "qr_code_data": null,
    "backup_codes": null
  }
}
```

---

## 4. **Enable Two-Factor Authentication**
```http
POST /api/auth/security/2fa/enable/
```

### **Request Body:**
```json
{
  "totp_code": "123456"
}
```

### **Response:**
```json
{
  "success": true,
  "message": "Two-factor authentication enabled successfully",
  "backup_codes": [
    "A1B2C3D4",
    "E5F6G7H8",
    "I9J0K1L2",
    "M3N4O5P6",
    "Q7R8S9T0",
    "U1V2W3X4",
    "Y5Z6A7B8",
    "C9D0E1F2",
    "G3H4I5J6",
    "K7L8M9N0"
  ],
  "warning": "Please save these backup codes in a secure location. They will not be shown again."
}
```

### **Error Response:**
```json
{
  "success": false,
  "errors": {
    "totp_code": ["Invalid TOTP code. Please try again."]
  }
}
```

---

## 5. **Disable Two-Factor Authentication**
```http
POST /api/auth/security/2fa/disable/
```

### **Request Body:**
```json
{
  "password": "userpassword123",
  "totp_code": "123456"
}
```

### **Response:**
```json
{
  "success": true,
  "message": "Two-factor authentication disabled successfully"
}
```

### **Error Response:**
```json
{
  "success": false,
  "errors": {
    "password": ["Password is incorrect."],
    "totp_code": ["Invalid TOTP code."]
  }
}
```

---

## 6. **Verify Two-Factor Authentication**
```http
POST /api/auth/security/2fa/verify/
```

### **Request Body (TOTP Code):**
```json
{
  "totp_code": "123456"
}
```

### **Request Body (Backup Code):**
```json
{
  "backup_code": "A1B2C3D4"
}
```

### **Response:**
```json
{
  "success": true,
  "message": "2FA verification successful"
}
```

### **Error Response:**
```json
{
  "success": false,
  "error": "Invalid 2FA code"
}
```

---

## 7. **List Active Sessions**
```http
GET /api/auth/security/sessions/
```

### **Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "session-uuid-here",
      "session_key": "abc123def456",
      "ip_address": "127.0.0.1",
      "device_name": "Chrome on Windows",
      "location": "Tanzania",
      "is_active": true,
      "created_at": "2025-10-23T10:30:00.000Z",
      "last_activity": "2025-10-23T10:45:00.000Z",
      "expires_at": "2025-10-24T10:30:00.000Z",
      "is_current": true,
      "device_info": {
        "browser": "Chrome",
        "os": "Windows",
        "device_type": "Desktop"
      },
      "time_ago": "5 minutes ago"
    },
    {
      "id": "session-uuid-2",
      "session_key": "xyz789uvw012",
      "ip_address": "192.168.1.100",
      "device_name": "Safari on iPhone",
      "location": "Tanzania",
      "is_active": true,
      "created_at": "2025-10-23T09:15:00.000Z",
      "last_activity": "2025-10-23T10:30:00.000Z",
      "expires_at": "2025-10-24T09:15:00.000Z",
      "is_current": false,
      "device_info": {
        "browser": "Safari",
        "os": "iOS",
        "device_type": "Mobile"
      },
      "time_ago": "20 minutes ago"
    }
  ],
  "total_count": 2
}
```

---

## 8. **Terminate Specific Session**
```http
POST /api/auth/security/sessions/{session_id}/terminate/
```

### **Response:**
```json
{
  "success": true,
  "message": "Session terminated successfully"
}
```

### **Error Response:**
```json
{
  "success": false,
  "error": "Cannot terminate current session"
}
```

---

## 9. **Terminate All Other Sessions**
```http
POST /api/auth/security/sessions/terminate-all-others/
```

### **Response:**
```json
{
  "success": true,
  "message": "Terminated 3 other sessions",
  "terminated_count": 3
}
```

---

## 10. **List Security Events**
```http
GET /api/auth/security/events/
```

### **Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "event-uuid-here",
      "event_type": "password_change",
      "event_type_display": "Password Changed",
      "description": "Password changed successfully",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "metadata": {
        "changed_at": "2025-10-23T10:30:00.000Z"
      },
      "created_at": "2025-10-23T10:30:00.000Z",
      "time_ago": "15 minutes ago"
    },
    {
      "id": "event-uuid-2",
      "event_type": "login",
      "event_type_display": "Login",
      "description": "User logged in successfully",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "metadata": {},
      "created_at": "2025-10-23T10:15:00.000Z",
      "time_ago": "30 minutes ago"
    },
    {
      "id": "event-uuid-3",
      "event_type": "2fa_enabled",
      "event_type_display": "2FA Enabled",
      "description": "Two-factor authentication enabled",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "metadata": {
        "enabled_at": "2025-10-23T10:00:00.000Z"
      },
      "created_at": "2025-10-23T10:00:00.000Z",
      "time_ago": "45 minutes ago"
    }
  ],
  "total_count": 3
}
```

---

## 📱 **Frontend Integration Examples**

### **Security Settings Page:**
```javascript
// Get security summary
const getSecuritySummary = async () => {
  const response = await fetch('/api/auth/security/summary/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  const data = await response.json();
  
  if (data.success) {
    console.log('Security Score:', data.data.security_score);
    console.log('2FA Enabled:', data.data.two_factor_enabled);
    console.log('Active Sessions:', data.data.active_sessions);
  }
};

// Change password
const changePassword = async (currentPassword, newPassword, confirmPassword) => {
  const response = await fetch('/api/auth/security/change-password/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  });
  
  const data = await response.json();
  return data;
};

// Enable 2FA
const enable2FA = async (totpCode) => {
  const response = await fetch('/api/auth/security/2fa/enable/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      totp_code: totpCode
    })
  });
  
  const data = await response.json();
  return data;
};

// Get active sessions
const getActiveSessions = async () => {
  const response = await fetch('/api/auth/security/sessions/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  return data;
};

// Terminate session
const terminateSession = async (sessionId) => {
  const response = await fetch(`/api/auth/security/sessions/${sessionId}/terminate/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  return data;
};
```

### **2FA Setup Flow:**
```javascript
// Step 1: Get 2FA status and QR code
const setup2FA = async () => {
  const response = await fetch('/api/auth/security/2fa/status/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  
  if (data.success && data.data.qr_code_data) {
    // Display QR code
    document.getElementById('qr-code').src = data.data.qr_code_data.qr_code;
    document.getElementById('secret-key').textContent = data.data.qr_code_data.manual_entry_key;
  }
};

// Step 2: Enable 2FA with TOTP code
const enable2FA = async (totpCode) => {
  const response = await fetch('/api/auth/security/2fa/enable/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      totp_code: totpCode
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Display backup codes
    console.log('Backup codes:', data.backup_codes);
    alert('2FA enabled! Save these backup codes: ' + data.backup_codes.join(', '));
  }
  
  return data;
};
```

---

## 🔧 **Error Responses**

### **Authentication Error:**
```json
{
  "success": false,
  "error": "Authentication credentials were not provided."
}
```

### **Validation Error:**
```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### **Server Error:**
```json
{
  "success": false,
  "error": "Failed to process request"
}
```

---

## 📊 **Security Score Calculation**

The security score (0-100) is calculated based on:
- **2FA Enabled**: +30 points
- **Active Sessions**: 
  - 1 session: +20 points
  - 2-3 sessions: +15 points
  - 4-5 sessions: +10 points
  - 6+ sessions: +5 points
- **Recent Activity** (last 30 days):
  - 1-5 events: +20 points
  - 6-10 events: +15 points
  - 11-20 events: +10 points
  - 21+ events: +5 points

---

**All security endpoints are fully functional and ready for frontend integration!** 🚀
