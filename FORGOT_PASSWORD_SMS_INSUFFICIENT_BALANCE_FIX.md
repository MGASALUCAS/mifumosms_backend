# Forgot Password SMS - Insufficient Balance Issue

## Issue Found

The `/api/auth/sms/forgot-password/` endpoint was returning a 400 error without clear details. After adding detailed logging, we discovered the actual issue:

**The endpoint is working correctly, but there's insufficient SMS balance to send the verification code.**

## Root Cause

```
INFO 2025-10-28 18:04:35,281 views 17492 16132 SMS result: {
    'success': False, 
    'error': 'Insufficient balance', 
    'error_code': 102
}
```

The SMS service provider is returning an error because the account doesn't have enough balance to send SMS messages.

## Solution

Updated the endpoint to return detailed error information including:

1. **Error message**: Clear description of what went wrong
2. **Error code**: Numerical code from SMS provider (102 = Insufficient balance)
3. **Error details**: Full details from the SMS service

### Error Response Example

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

## Frontend Handling

The frontend should handle this error appropriately:

### Option 1: Show Error Message
```javascript
try {
    const response = await fetch('/api/auth/sms/forgot-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber })
    });
    
    const data = await response.json();
    
    if (!data.success) {
        // Show user-friendly error message
        if (data.error === 'Insufficient balance') {
            alert('Sorry, the system is temporarily unable to send SMS messages. Please try again later or contact support.');
        } else {
            alert(data.error);
        }
    }
} catch (error) {
    console.error('Error:', error);
    alert('An error occurred. Please try again.');
}
```

### Option 2: Handle Specific Error Codes
```javascript
if (!data.success) {
    switch (data.error_code) {
        case 102:
            // Insufficient balance
            showError('Service temporarily unavailable. Please try again later.');
            break;
        case 101:
            // Network error
            showError('Network error. Please check your connection.');
            break;
        default:
            showError(data.error || 'An error occurred.');
    }
}
```

## How to Add SMS Balance

To fix the "Insufficient balance" error, you need to:

1. **Check current balance**:
   - Log into the SMS provider dashboard (Beem Africa, etc.)
   - Check account balance

2. **Top up account**:
   - Navigate to billing/payments section
   - Add funds to the SMS provider account

3. **Verify balance**:
   ```python
   from messaging.services.sms_service import SMSService
   
   sms_service = SMSService()
   balance = sms_service.check_balance()
   print(f"Current balance: {balance}")
   ```

## Testing

After adding balance, test the endpoint:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/sms/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+255614853618"}'
```

Expected response (success):
```json
{
    "success": true,
    "message": "Password reset code sent to your phone number",
    "phone_number": "255614853618"
}
```

Expected response (still insufficient balance):
```json
{
    "success": false,
    "error": "Insufficient balance",
    "error_code": 102,
    "details": {...}
}
```

## Summary

- ✅ Endpoint is working correctly
- ✅ User lookup successful
- ✅ Detailed error logging added
- ❌ SMS balance insufficient - needs top-up
- 📋 Frontend now receives detailed error information

The issue is **NOT** with the backend endpoint or frontend code - it's simply that the SMS provider account needs to be topped up with balance.

