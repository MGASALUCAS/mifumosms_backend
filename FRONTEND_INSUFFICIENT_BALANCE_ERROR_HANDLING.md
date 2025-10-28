# Frontend Error Handling for Insufficient Balance

## Overview

When the SMS service returns an "Insufficient balance" error, the frontend should show a user-friendly message directing users to contact admin.

## Error Response Format

The backend now returns detailed error information:

```json
{
  "success": false,
  "error": "Insufficient balance",
  "error_code": 102,
  "details": {
    "success": false,
    "error": "Insufficient balance",
    "error_code": 102,
    "response": {
      "code": 102,
      "message": "Insufficient balance"
    }
  }
}
```

## Frontend Implementation

### Option 1: Using React with Async/Await

```jsx
import React, { useState } from 'react';
import { toast, notification } from 'antd'; // or use your UI library

const ForgotPasswordForm = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('/api/auth/sms/forgot-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone_number: phoneNumber
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        // Handle insufficient balance error
        if (data.error === 'Insufficient balance' || data.error_code === 102) {
          notification.error({
            message: 'Service Temporarily Unavailable',
            description: 'SMS service is currently unavailable. Please contact the administrator for assistance.',
            duration: 10,
            placement: 'topRight',
          });
        } 
        // Handle other errors
        else {
          notification.error({
            message: 'Error',
            description: data.error || 'Failed to send password reset code. Please try again.',
            duration: 5,
          });
        }
        return;
      }

      // Success
      notification.success({
        message: 'Code Sent Successfully',
        description: 'A password reset code has been sent to your phone number.',
      });

    } catch (error) {
      console.error('Error:', error);
      notification.error({
        message: 'Error',
        description: 'Network error. Please check your connection and try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleForgotPassword}>
      <input
        type="tel"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
        placeholder="Enter phone number"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Reset Code'}
      </button>
    </form>
  );
};

export default ForgotPasswordForm;
```

### Option 2: Using Error Boundary Component

```jsx
import React from 'react';
import { Modal, Button } from 'antd';

const ErrorHandler = {
  handleAPIError: (error, data) => {
    // Insufficient balance error
    if (data?.error === 'Insufficient balance' || data?.error_code === 102) {
      Modal.error({
        title: 'Service Temporarily Unavailable',
        content: (
          <div>
            <p>SMS service is currently unavailable due to insufficient balance.</p>
            <p><strong>Please contact the administrator:</strong></p>
            <ul>
              <li>Email: admin@mifumosms.com</li>
              <li>Phone: +255 XXX XXX XXX</li>
              <li>Support Hours: Mon-Fri, 9AM-5PM</li>
            </ul>
          </div>
        ),
        width: 500,
        okText: 'I Understand',
      });
      return true; // Error handled
    }

    // Other errors
    Modal.error({
      title: 'Error',
      content: data?.error || 'An error occurred. Please try again.',
      okText: 'OK',
    });
    return true;
  }
};

export default ErrorHandler;
```

### Option 3: Custom Hook for Error Handling

```jsx
import { useState } from 'react';
import { message } from 'antd';

const useForgotPassword = () => {
  const [loading, setLoading] = useState(false);

  const sendResetCode = async (phoneNumber) => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/auth/sms/forgot-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone_number: phoneNumber })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        // Handle insufficient balance
        if (data.error_code === 102 || data.error?.includes('balance')) {
          message.error({
            content: 'SMS service unavailable. Please contact admin for assistance.',
            duration: 8,
          });
          
          // Optionally show detailed modal
          setTimeout(() => {
            message.info({
              content: 'Contact: admin@mifumosms.com or +255 XXX XXX XXX',
              duration: 10,
            });
          }, 2000);
          
          throw new Error('SMS_UNAVAILABLE');
        }

        // Handle other errors
        throw new Error(data.error || 'Failed to send code');
      }

      message.success('Password reset code sent to your phone!');
      return data;
      
    } catch (error) {
      if (error.message === 'SMS_UNAVAILABLE') {
        // Already handled, just rethrow
        throw error;
      }
      
      console.error('Error:', error);
      message.error('Failed to send reset code. Please try again.');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { sendResetCode, loading };
};

export default useForgotPassword;
```

### Option 4: Simple Function with Alert

```javascript
const handleForgotPassword = async (phoneNumber) => {
  try {
    const response = await fetch('/api/auth/sms/forgot-password/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number: phoneNumber })
    });

    const data = await response.json();

    if (!data.success) {
      // Check for insufficient balance
      if (data.error_code === 102 || data.error?.includes('balance')) {
        alert(
          'SMS service is temporarily unavailable.\n\n' +
          'Please contact the administrator for assistance:\n\n' +
          'Email: admin@mifumosms.com\n' +
          'Phone: +255 XXX XXX XXX\n' +
          'Support Hours: Mon-Fri, 9AM-5PM'
        );
        return;
      }

      // Other errors
      alert(data.error || 'Failed to send reset code. Please try again.');
      return;
    }

    // Success
    alert('Password reset code has been sent to your phone number!');
    
  } catch (error) {
    console.error('Error:', error);
    alert('Network error. Please check your connection.');
  }
};
```

### Option 5: Toast Notification (React-toastify)

```jsx
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const handleForgotPassword = async (phoneNumber) => {
  try {
    const response = await fetch('/api/auth/sms/forgot-password/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number: phoneNumber })
    });

    const data = await response.json();

    if (!data.success) {
      // Insufficient balance
      if (data.error_code === 102) {
        toast.error(
          <div>
            <strong>Service Unavailable</strong>
            <p>SMS service is temporarily unavailable.</p>
            <p>Contact admin: admin@mifumosms.com</p>
          </div>,
          {
            position: 'top-right',
            autoClose: 10000,
            hideProgressBar: false,
            closeOnClick: true,
            pauseOnHover: true,
          }
        );
        return;
      }

      // Other errors
      toast.error(data.error || 'Failed to send code');
      return;
    }

    // Success
    toast.success('Reset code sent to your phone!');
    
  } catch (error) {
    toast.error('Network error. Please try again.');
  }
};
```

## Error Codes Reference

| Error Code | Description | User Action |
|------------|-------------|-------------|
| 102 | Insufficient balance | Contact admin |
| 101 | Network error | Check connection, retry |
| 103 | Invalid phone number | Check format, retry |
| 104 | Rate limit exceeded | Wait and retry |
| 105 | Service unavailable | Contact admin |

## Implementation Checklist

- [ ] Handle `error_code: 102` (Insufficient balance)
- [ ] Show user-friendly error message
- [ ] Display admin contact information
- [ ] Add retry button for other errors
- [ ] Log errors for debugging
- [ ] Test with actual API responses

## Contact Information Template

```jsx
const ContactInfo = {
  email: 'admin@mifumosms.com',
  phone: '+255 XXX XXX XXX',
  supportHours: 'Mon-Fri, 9AM-5PM EAT',
  emergencyContact: '+255 XXX XXX XXX (24/7)'
};

// Display in error message
const ErrorMessage = () => (
  <div className="error-message">
    <h3>Service Unavailable</h3>
    <p>SMS service is temporarily unavailable.</p>
    <p>Please contact support:</p>
    <ul>
      <li>Email: {ContactInfo.email}</li>
      <li>Phone: {ContactInfo.phone}</li>
      <li>Hours: {ContactInfo.supportHours}</li>
    </ul>
  </div>
);
```

## Testing

Test the error handling:

```javascript
// Simulate insufficient balance error
const mockErrorResponse = {
  success: false,
  error: 'Insufficient balance',
  error_code: 102,
  details: {
    success: false,
    error: 'Insufficient balance',
    error_code: 102
  }
};

// Trigger error handling
handleAPIError(null, mockErrorResponse);
```

## Best Practices

1. **Always show user-friendly messages** - Don't expose technical details
2. **Provide contact information** - Let users know how to get help
3. **Log errors for debugging** - Use console.error() for developers
4. **Offer alternative solutions** - Email, phone, etc.
5. **Retry mechanism** - For transient errors, not insufficient balance

## Summary

The key is to:
1. Check for `error_code === 102` or error contains "Insufficient balance"
2. Show a clear message that the service is unavailable
3. Provide admin contact information
4. Do NOT retry the request (it will keep failing)
5. Log the error for admin attention

