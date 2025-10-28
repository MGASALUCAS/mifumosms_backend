# Frontend API 404 Error Fix

## Problem
Frontend is getting 404 error when calling:
```
POST http://localhost:8080/api/auth/sms/verify-code/ 404 (Not Found)
```

## Root Cause
The frontend is trying to call the API on its own port (8080), but the backend API is running on a different port (8001).

## Solution Options

### Option 1: Configure Frontend to Call Correct Backend URL

Update the frontend API configuration to point to the backend:

**Development:**
```javascript
// In your frontend config (e.g., config.js or .env)
const API_BASE_URL = 'http://127.0.0.1:8001';
// or
const API_BASE_URL = 'http://localhost:8001';
```

**Production:**
```javascript
const API_BASE_URL = 'https://mifumosms.servehttp.com';
```

### Option 2: Set Up Proxy in Frontend (React/Vite/Next.js)

**For Vite (vite.config.js):**
```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        secure: false
      }
    }
  }
}
```

**For Next.js (next.config.js):**
```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8001/api/:path*'
      }
    ]
  }
}
```

## Backend Endpoint Status

✅ **Backend endpoint exists** at:
- Route: `accounts/urls.py` line 33: `path('sms/verify-code/', ...)`
- Full URL: `http://127.0.0.1:8001/api/auth/sms/verify-code/`
- Function: `accounts/views.py` line 591: `verify_phone_code()`
- Request Body:
  ```json
  {
    "phone_number": "+255700000001",
    "verification_code": "123456"
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "message": "Phone number verified successfully",
    "phone_verified": true
  }
  ```

## Test the Backend Endpoint Directly

```bash
# Test from command line
curl -X POST http://127.0.0.1:8001/api/auth/sms/verify-code/ \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+255700000001",
    "verification_code": "123456"
  }'
```

## Quick Fix for Development

Update your frontend code to use the correct base URL:

**Before:**
```typescript
const response = await fetch('/api/auth/sms/verify-code/', {
  method: 'POST',
  body: JSON.stringify({ phone_number, verification_code })
});
```

**After:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';
// or for production:
// const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://mifumosms.servehttp.com';

const response = await fetch(`${API_BASE_URL}/api/auth/sms/verify-code/`, {
  method: 'POST',
  body: JSON.stringify({ phone_number, verification_code })
});
```

## Summary

✅ Backend endpoint exists and is working  
❌ Frontend is calling wrong URL (localhost:8080 instead of localhost:8001)  
🔧 Action Required: Configure frontend to point to correct backend API URL

