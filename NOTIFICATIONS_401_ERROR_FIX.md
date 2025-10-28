# Notifications 401 Error Fix

## Error Summary
```
GET https://mifumosms.servehttp.com/api/notifications/recent/ 401 (Unauthorized)
Error fetching recent notifications: Error: Failed to get recent notifications
```

## Root Cause

The `/api/notifications/recent/` endpoint requires authentication (`@permission_classes([IsAuthenticated])`), but the frontend is not sending a valid authentication token with the request.

## Issues Identified

### 1. Missing Authentication Token ❌
The frontend is not including the JWT token in the request headers.

### 2. CORS Issue (Sometimes) ❌
Some requests are being blocked by CORS policy.

## Solution

### Fix 1: Send Authentication Token with Requests

The frontend must include the JWT token in the Authorization header:

**BEFORE (Missing Token):**
```javascript
const response = await fetch('/api/notifications/recent/', {
  method: 'GET'
});
```

**AFTER (With Token):**
```javascript
// Get token from localStorage or auth context
const token = localStorage.getItem('access_token'); // or from your auth context

const response = await fetch('/api/notifications/recent/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Fix 2: Handle 401 Errors Gracefully

```javascript
async function getRecentNotifications() {
  try {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      // User not logged in
      return [];
    }
    
    const response = await fetch('/api/notifications/recent/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      // Redirect to login
      window.location.href = '/login';
      return [];
    }
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.notifications || [];
    
  } catch (error) {
    console.error('Error fetching notifications:', error);
    return [];
  }
}
```

### Fix 3: Refresh Token When Expired

```javascript
async function getRecentNotifications() {
  const token = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  
  // Try with current token
  let response = await fetch('/api/notifications/recent/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  // If 401, try to refresh token
  if (response.status === 401 && refreshToken) {
    const refreshResponse = await fetch('/api/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (refreshResponse.ok) {
      const { access } = await refreshResponse.json();
      localStorage.setItem('access_token', access);
      
      // Retry with new token
      response = await fetch('/api/notifications/recent/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${access}`,
          'Content-Type': 'application/json'
        }
      });
    }
  }
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data.notifications || [];
}
```

## Backend Endpoint Details

**Endpoint:** `GET /api/notifications/recent/`  
**Authentication:** Required (`IsAuthenticated`)  
**Expected Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": "...",
      "title": "...",
      "message": "...",
      "status": "unread",
      "created_at": "..."
    }
  ],
  "unread_count": 5
}
```

## Test the Backend Endpoint

```bash
# Get access token first
curl -X POST https://mifumosms.servehttp.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token to get notifications
curl -X GET https://mifumosms.servehttp.com/api/notifications/recent/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Quick Fix for Frontend

If you're using Axios or a similar HTTP client, configure it globally:

```javascript
// axios.config.js
import axios from 'axios';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Summary

✅ **Backend**: Endpoint exists and works correctly  
❌ **Frontend**: Not sending authentication token  
🔧 **Action Required**: 
1. Add `Authorization: Bearer ${token}` header to API requests
2. Handle 401 errors by refreshing token or redirecting to login
3. Set up axios interceptors to automatically add token

The backend is working fine - you just need to authenticate the requests from the frontend!

