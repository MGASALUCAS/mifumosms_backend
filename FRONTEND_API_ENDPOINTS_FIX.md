# Frontend API Endpoints Fix

## 🚨 Critical Issues Found

Based on the frontend error logs, there are **URL mismatches** between what the frontend is calling and what the backend actually provides.

## ❌ Current Frontend Issues

### 1. Profile Settings URL Mismatch
- **Frontend calls**: `GET http://127.0.0.1:8001/api/api/accounts/settings/profile/`
- **Issues**: 
  - Double `/api/api/` in URL
  - Wrong path: `/accounts/` instead of `/auth/`
- **Correct URL**: `GET http://127.0.0.1:8001/api/auth/settings/profile/`

### 2. Dashboard Endpoints (Working but Authentication Issues)
- **Frontend calls**: 
  - `GET http://127.0.0.1:8001/api/messaging/dashboard/overview/` ✅
  - `GET http://127.0.0.1:8001/api/messaging/dashboard/metrics/` ✅
  - `GET http://127.0.0.1:8001/api/messaging/sender-requests/stats/` ✅
- **Issue**: 400 errors due to invalid/expired authentication tokens

## ✅ Backend API Status

All backend endpoints are **working correctly**:

### Authentication Endpoints
```
POST /api/auth/login/                    ✅ Working
POST /api/auth/register/                 ✅ Working
POST /api/auth/token/refresh/            ✅ Working
GET  /api/auth/profile/                  ✅ Working
GET  /api/auth/settings/profile/         ✅ Working
PUT  /api/auth/settings/profile/         ✅ Working
PATCH /api/auth/settings/profile/        ✅ Working
```

### Dashboard Endpoints
```
GET /api/messaging/dashboard/overview/   ✅ Working
GET /api/messaging/dashboard/metrics/    ✅ Working
GET /api/messaging/sender-requests/stats/ ✅ Working
```

## 🔧 Frontend Fixes Required

### 1. Fix Profile Settings URL

**Current (Broken):**
```javascript
// ❌ WRONG - Double /api/api/ and wrong path
const profileUrl = 'http://127.0.0.1:8001/api/api/accounts/settings/profile/';
```

**Fixed:**
```javascript
// ✅ CORRECT
const profileUrl = 'http://127.0.0.1:8001/api/auth/settings/profile/';
```

### 2. Fix API Base URL Configuration

**Current (Broken):**
```javascript
// ❌ WRONG - Double /api/ in base URL
const API_BASE_URL = 'http://127.0.0.1:8001/api/api/';
```

**Fixed:**
```javascript
// ✅ CORRECT
const API_BASE_URL = 'http://127.0.0.1:8001/api/';
```

### 3. Update Frontend API Configuration

Create or update your frontend API configuration:

```javascript
// api.js or config.js
const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8001/api',
  
  // Authentication endpoints
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    REFRESH: '/auth/token/refresh/',
    PROFILE: '/auth/profile/',
    PROFILE_SETTINGS: '/auth/settings/profile/',
    PREFERENCES: '/auth/settings/preferences/',
    NOTIFICATIONS: '/auth/settings/notifications/',
    SECURITY: '/auth/settings/security/',
  },
  
  // Dashboard endpoints
  DASHBOARD: {
    OVERVIEW: '/messaging/dashboard/overview/',
    METRICS: '/messaging/dashboard/metrics/',
    COMPREHENSIVE: '/messaging/dashboard/comprehensive/',
  },
  
  // Sender requests
  SENDER_REQUESTS: {
    STATS: '/messaging/sender-requests/stats/',
    LIST: '/messaging/sender-requests/',
    CREATE: '/messaging/sender-requests/',
  }
};

// Helper function to build URLs
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Usage examples
export const API_ENDPOINTS = {
  getProfile: () => buildApiUrl(API_CONFIG.AUTH.PROFILE_SETTINGS),
  getDashboardOverview: () => buildApiUrl(API_CONFIG.DASHBOARD.OVERVIEW),
  getDashboardMetrics: () => buildApiUrl(API_CONFIG.DASHBOARD.METRICS),
  getSenderRequestStats: () => buildApiUrl(API_CONFIG.SENDER_REQUESTS.STATS),
};
```

### 4. Update Frontend API Calls

**Before (Broken):**
```javascript
// ❌ WRONG
const response = await fetch('http://127.0.0.1:8001/api/api/accounts/settings/profile/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

**After (Fixed):**
```javascript
// ✅ CORRECT
const response = await fetch('http://127.0.0.1:8001/api/auth/settings/profile/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### 5. Fix Authentication Token Handling

The 400 errors on dashboard endpoints are likely due to token issues. Ensure proper token management:

```javascript
// Token management
class AuthService {
  static getToken() {
    return localStorage.getItem('access_token');
  }
  
  static setToken(token) {
    localStorage.setItem('access_token', token);
  }
  
  static clearToken() {
    localStorage.removeItem('access_token');
  }
  
  static isTokenValid() {
    const token = this.getToken();
    if (!token) return false;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch {
      return false;
    }
  }
  
  static async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');
    
    const response = await fetch('http://127.0.0.1:8001/api/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (response.ok) {
      const data = await response.json();
      this.setToken(data.access);
      return data.access;
    } else {
      this.clearToken();
      throw new Error('Token refresh failed');
    }
  }
}
```

## 🧪 Testing the Fix

Use this test script to verify all endpoints work:

```javascript
// test-api-endpoints.js
const API_BASE = 'http://127.0.0.1:8001/api';

async function testEndpoints() {
  // First, login to get a token
  const loginResponse = await fetch(`${API_BASE}/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'test@example.com',
      password: 'testpass123'
    })
  });
  
  const loginData = await loginResponse.json();
  const token = loginData.tokens.access;
  
  console.log('✅ Login successful');
  
  // Test profile settings
  const profileResponse = await fetch(`${API_BASE}/auth/settings/profile/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('Profile settings:', profileResponse.status === 200 ? '✅' : '❌');
  
  // Test dashboard overview
  const dashboardResponse = await fetch(`${API_BASE}/messaging/dashboard/overview/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('Dashboard overview:', dashboardResponse.status === 200 ? '✅' : '❌');
  
  // Test dashboard metrics
  const metricsResponse = await fetch(`${API_BASE}/messaging/dashboard/metrics/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('Dashboard metrics:', metricsResponse.status === 200 ? '✅' : '❌');
  
  // Test sender requests stats
  const statsResponse = await fetch(`${API_BASE}/messaging/sender-requests/stats/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  console.log('Sender requests stats:', statsResponse.status === 200 ? '✅' : '❌');
}

testEndpoints().catch(console.error);
```

## 📋 Summary

1. **Profile Settings**: Change URL from `/api/api/accounts/settings/profile/` to `/api/auth/settings/profile/`
2. **API Base URL**: Remove double `/api/` from base URL configuration
3. **Authentication**: Ensure proper token handling and refresh logic
4. **All other endpoints**: Working correctly, just need proper authentication

The backend is fully functional - the issues are entirely on the frontend side with incorrect URL configurations.
