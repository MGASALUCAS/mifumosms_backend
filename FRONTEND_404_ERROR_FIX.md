# Frontend 404 Error Fix for SenderNames Component

## 🚨 Problem Analysis

The 404 error in the SenderNames component is **NOT** a backend issue. The backend endpoint `/api/messaging/sender-requests/stats/` is working correctly and returns 401 (authentication required) as expected.

### Root Causes of 404 Error

1. **Authentication Issues**
   - Missing JWT token in request headers
   - Invalid or expired token
   - Token not properly stored in localStorage

2. **Network Connectivity**
   - Frontend can't reach the server
   - CORS issues blocking the request
   - Server temporarily unavailable

3. **Frontend Code Issues**
   - Incorrect API endpoint URL
   - Missing error handling
   - Race conditions in component mounting

---

## ✅ Backend Status (Confirmed Working)

```bash
# Test results show backend is working correctly:
Status Code: 401 (Authentication required)
Response: {"detail":"Authentication credentials were not provided."}
```

**The endpoint exists and is accessible - it's just requiring authentication.**

---

## 🔧 Frontend Fixes Required

### 1. Fix Authentication Issues

#### Check Token Storage
```javascript
// Add this to your SenderNames component
const checkAuthToken = () => {
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('No authentication token found');
    return false;
  }
  
  // Check if token is expired
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const now = Date.now() / 1000;
    if (payload.exp < now) {
      console.error('Token has expired');
      localStorage.removeItem('token');
      return false;
    }
  } catch (e) {
    console.error('Invalid token format');
    localStorage.removeItem('token');
    return false;
  }
  
  return true;
};
```

#### Updated SenderNames Component
```javascript
import React, { useState, useEffect } from 'react';

const SenderNames = () => {
  const [senderRequests, setSenderRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [authError, setAuthError] = useState(false);

  useEffect(() => {
    // Check authentication first
    if (!checkAuthToken()) {
      setAuthError(true);
      setError('Authentication required. Please log in.');
      setLoading(false);
      return;
    }
    
    fetchSenderRequests();
  }, []);

  const checkAuthToken = () => {
    const token = localStorage.getItem('token');
    if (!token) {
      return false;
    }
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp > now;
    } catch (e) {
      return false;
    }
  };

  const fetchSenderRequests = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch('/api/messaging/sender-requests/stats/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      
      if (response.status === 404) {
        throw new Error('API endpoint not found. Please check the URL.');
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setSenderRequests(data.data.recent_requests || []);
      } else {
        throw new Error(data.message || 'Failed to fetch sender requests');
      }
    } catch (err) {
      console.error('Error fetching sender requests:', err);
      setError(err.message);
      
      // If it's an auth error, mark for redirect
      if (err.message.includes('Authentication') || err.message.includes('401')) {
        setAuthError(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    if (authError) {
      // Redirect to login
      window.location.href = '/login';
    } else {
      fetchSenderRequests();
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading sender requests...</p>
      </div>
    );
  }

  if (authError) {
    return (
      <div className="auth-error-container">
        <h2>Authentication Required</h2>
        <p>Please log in to view sender requests.</p>
        <button onClick={handleRetry} className="btn-primary">
          Go to Login
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error Loading Sender Requests</h2>
        <p><strong>Error:</strong> {error}</p>
        <div className="error-actions">
          <button onClick={handleRetry} className="btn-primary">
            {authError ? 'Go to Login' : 'Retry'}
          </button>
          <button onClick={() => window.location.reload()} className="btn-secondary">
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="sender-requests-container">
      <h2>Sender ID Requests</h2>
      {senderRequests.length === 0 ? (
        <div className="empty-state">
          <p>No sender requests found.</p>
          <button onClick={() => window.location.href = '/sender-requests/new'} className="btn-primary">
            Create New Request
          </button>
        </div>
      ) : (
        <div className="requests-list">
          {senderRequests.map(request => (
            <div key={request.id} className="request-item">
              <div className="request-header">
                <h3>{request.requested_sender_id}</h3>
                <span className={`status status-${request.status}`}>
                  {request.status}
                </span>
              </div>
              <div className="request-details">
                <p><strong>Type:</strong> {request.request_type}</p>
                <p><strong>Created:</strong> {new Date(request.created_at).toLocaleDateString()}</p>
                {request.sample_content && (
                  <p><strong>Sample:</strong> {request.sample_content}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SenderNames;
```

### 2. Add CSS for Error States

```css
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.auth-error-container,
.error-container {
  text-align: center;
  padding: 2rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin: 1rem 0;
}

.error-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.sender-requests-container {
  padding: 1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.requests-list {
  display: grid;
  gap: 1rem;
}

.request-item {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
}

.request-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-approved {
  background: #d4edda;
  color: #155724;
}

.status-rejected {
  background: #f8d7da;
  color: #721c24;
}

.request-details p {
  margin: 0.25rem 0;
  font-size: 0.875rem;
  color: #6c757d;
}
```

### 3. Add Network Error Handling

```javascript
// Add this utility function for better error handling
const handleApiError = (error, response) => {
  console.error('API Error:', error);
  console.error('Response:', response);
  
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return 'Network error. Please check your internet connection.';
  }
  
  if (response?.status === 401) {
    return 'Authentication failed. Please log in again.';
  }
  
  if (response?.status === 404) {
    return 'API endpoint not found. Please contact support.';
  }
  
  if (response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  
  return error.message || 'An unexpected error occurred.';
};
```

### 4. Add Debugging Information

```javascript
// Add this to help debug the issue
const debugApiCall = async (url, options) => {
  console.log('API Call Debug:');
  console.log('URL:', url);
  console.log('Options:', options);
  console.log('Token present:', !!localStorage.getItem('token'));
  
  try {
    const response = await fetch(url, options);
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
    
    const text = await response.text();
    console.log('Response body:', text);
    
    return {
      ok: response.ok,
      status: response.status,
      data: text
    };
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};
```

---

## 🧪 Testing the Fix

### 1. Test Authentication
```javascript
// Add this to your browser console to test
const testAuth = async () => {
  const token = localStorage.getItem('token');
  console.log('Token:', token);
  
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      console.log('Token payload:', payload);
      console.log('Expires:', new Date(payload.exp * 1000));
      console.log('Valid:', payload.exp > Date.now() / 1000);
    } catch (e) {
      console.error('Invalid token:', e);
    }
  }
};

testAuth();
```

### 2. Test API Call
```javascript
// Test the API call directly
const testApiCall = async () => {
  const token = localStorage.getItem('token');
  
  try {
    const response = await fetch('/api/messaging/sender-requests/stats/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Status:', response.status);
    console.log('Response:', await response.text());
  } catch (error) {
    console.error('Error:', error);
  }
};

testApiCall();
```

---

## 📋 Summary

### ✅ Backend Status
- Endpoint `/api/messaging/sender-requests/stats/` is working correctly
- Returns 401 (authentication required) as expected
- No 404 errors from backend

### 🔧 Frontend Fixes Required
1. **Add proper authentication checks** - Verify token exists and is valid
2. **Improve error handling** - Handle 401, 404, and network errors properly
3. **Add debugging information** - Log API calls and responses
4. **Add retry functionality** - Allow users to retry failed requests
5. **Add loading states** - Show proper loading indicators

### 🎯 Expected Behavior After Fix
- Component shows loading state while fetching data
- Proper error messages for authentication issues
- Retry button for failed requests
- Redirect to login for authentication errors
- Success display of sender requests data

The 404 error should be resolved once proper authentication and error handling are implemented in the frontend.

