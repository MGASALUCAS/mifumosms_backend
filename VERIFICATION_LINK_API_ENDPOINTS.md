# Verification Link API Endpoints

## Overview
New endpoints that allow users to receive verification links via SMS instead of just verification codes. This provides an alternative verification method for users who see the "Account Verification Required" message.

## Endpoints

### 1. Send Verification Link via SMS
**POST** `/api/auth/sms/send-verification-link/`

Sends a verification link to the user's phone number via SMS.

#### Request Body
```json
{
  "phone_number": "0689726060"
}
```

#### Response (Success)
```json
{
  "success": true,
  "message": "Verification link sent to your phone number",
  "phone_number": "0689726060",
  "verification_link": "http://localhost:3000/verify-account?token=abc123&phone=0689726060"
}
```

#### Response (Superadmin Bypass)
```json
{
  "success": true,
  "message": "Account verification not required for admin users",
  "bypassed": true,
  "phone_number": "0689726060"
}
```

#### Response (Error)
```json
{
  "success": false,
  "error": "No account found with this phone number."
}
```

### 2. Verify Account Using Link
**POST** `/api/auth/sms/verify-account-link/`

Verifies the user's account using the token and phone number from the verification link.

#### Request Body
```json
{
  "token": "abc123def456",
  "phone_number": "0689726060"
}
```

#### Response (Success)
```json
{
  "success": true,
  "message": "Account verified successfully",
  "user": {
    "id": 2,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true,
    "phone_verified": true
  }
}
```

#### Response (Error)
```json
{
  "success": false,
  "error": "Invalid verification link or phone number."
}
```

### 3. Resend Verification Link
**POST** `/api/auth/sms/resend-verification-link/`

Resends a new verification link to the user's phone number.

#### Request Body
```json
{
  "phone_number": "0689726060"
}
```

#### Response (Success)
```json
{
  "success": true,
  "message": "New verification link sent to your phone number",
  "phone_number": "0689726060",
  "verification_link": "http://localhost:3000/verify-account?token=xyz789&phone=0689726060"
}
```

#### Response (Already Verified)
```json
{
  "success": true,
  "message": "Account is already verified",
  "phone_number": "0689726060"
}
```

## Features

### ✅ Superadmin Bypass
- Superadmin and staff users automatically bypass verification
- Returns `bypassed: true` in response
- No SMS is sent for admin users

### ✅ Token Expiration
- Verification tokens expire after 1 hour
- Users must request a new link if expired
- Old tokens are invalidated when new ones are generated

### ✅ Phone Number Normalization
- Automatically normalizes phone numbers to local format
- Handles various input formats (with/without +, with/without 0)
- Converts international format to local format for database lookup

### ✅ SMS Integration
- Uses the existing SMS verification service
- Sends clickable verification links via SMS
- Includes expiration warning in SMS message

## Frontend Integration

### 1. Add "Get Verification Link" Button
```javascript
// In verification required component
const VerificationRequired = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleGetVerificationLink = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/sms/send-verification-link/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        if (data.bypassed) {
          setMessage('Account verification not required for admin users');
          // Redirect to dashboard
          window.location.href = '/dashboard';
        } else {
          setMessage('Verification link sent to your phone number. Check your SMS.');
        }
      } else {
        setMessage(data.error || 'Failed to send verification link');
      }
    } catch (error) {
      setMessage('Error sending verification link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verification-required">
      <h2>Account Verification Required</h2>
      <p>Please verify your phone number to access the dashboard.</p>
      
      <div className="verification-options">
        <h3>Option 1: Get Verification Link</h3>
        <input
          type="tel"
          placeholder="Enter your phone number"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
        />
        <button 
          onClick={handleGetVerificationLink}
          disabled={loading || !phoneNumber}
        >
          {loading ? 'Sending...' : 'Get Verification Link'}
        </button>
        
        <h3>Option 2: Enter Verification Code</h3>
        {/* Existing verification code form */}
      </div>
      
      {message && <p className="message">{message}</p>}
    </div>
  );
};
```

### 2. Handle Verification Link Page
```javascript
// Verification page component
const VerifyAccountPage = () => {
  const [token, setToken] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Extract token and phone from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const tokenParam = urlParams.get('token');
    const phoneParam = urlParams.get('phone');
    
    if (tokenParam) setToken(tokenParam);
    if (phoneParam) setPhoneNumber(phoneParam);
  }, []);

  const handleVerifyAccount = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/sms/verify-account-link/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          token: token,
          phone_number: phoneNumber 
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage('Account verified successfully! Redirecting to dashboard...');
        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 2000);
      } else {
        setMessage(data.error || 'Verification failed');
      }
    } catch (error) {
      setMessage('Error verifying account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="verify-account">
      <h2>Verify Your Account</h2>
      
      <div className="verification-form">
        <input
          type="text"
          placeholder="Verification Token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
        />
        <input
          type="tel"
          placeholder="Phone Number"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
        />
        <button 
          onClick={handleVerifyAccount}
          disabled={loading || !token || !phoneNumber}
        >
          {loading ? 'Verifying...' : 'Verify Account'}
        </button>
      </div>
      
      {message && <p className="message">{message}</p>}
    </div>
  );
};
```

### 3. Add Resend Link Option
```javascript
const handleResendLink = async () => {
  setLoading(true);
  try {
    const response = await fetch('/api/auth/sms/resend-verification-link/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone_number: phoneNumber }),
    });
    
    const data = await response.json();
    
    if (data.success) {
      if (data.bypassed) {
        setMessage('Account verification not required for admin users');
        window.location.href = '/dashboard';
      } else if (data.message === 'Account is already verified') {
        setMessage('Account is already verified. Redirecting to dashboard...');
        window.location.href = '/dashboard';
      } else {
        setMessage('New verification link sent to your phone number');
      }
    } else {
      setMessage(data.error || 'Failed to resend verification link');
    }
  } catch (error) {
    setMessage('Error resending verification link');
  } finally {
    setLoading(false);
  }
};
```

## Configuration

### Environment Variables
Add to your `.env` file:
```env
FRONTEND_URL=http://localhost:3000
```

### Django Settings
The verification links use the `FRONTEND_URL` setting to generate the verification links. If not set, it defaults to `http://localhost:3000`.

## Security Features

### ✅ Token Security
- 32-character random tokens
- Tokens are single-use (invalidated after verification)
- Tokens expire after 1 hour

### ✅ Phone Number Validation
- Validates phone number exists in database
- Normalizes phone number format
- Prevents verification for non-existent users

### ✅ Rate Limiting
- Uses existing SMS rate limiting
- Prevents spam verification requests
- Respects SMS verification attempt limits

## Testing

### Test Cases
1. **Normal User**: Should receive verification link via SMS
2. **Superadmin User**: Should bypass verification
3. **Invalid Phone**: Should return error
4. **Expired Token**: Should return error
5. **Already Verified**: Should return success message
6. **Resend Link**: Should generate new token and send new link

### Test Data
```javascript
// Test phone numbers
const testPhones = [
  '0689726060',  // Admin phone (should bypass)
  '0689726061',  // Normal user phone
  '255689726060', // International format
  '+255689726060' // International format with +
];
```

## Summary

These new endpoints provide an alternative verification method for users who see the "Account Verification Required" message. Users can now:

1. **Get a verification link via SMS** instead of entering a code
2. **Click the link to verify their account** automatically
3. **Resend the link** if needed
4. **Bypass verification** if they're admin users

This improves the user experience by providing multiple verification options and making the process more convenient for users who prefer clicking links over entering codes.
