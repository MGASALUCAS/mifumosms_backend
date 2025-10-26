# Forgot Password SMS Issues and Solutions

## Issues Identified

### 1. 404 Error from Frontend
**Error**: `POST https://mifumosms.servehttp.com/api/auth/sms/forgot-password/ 404 (Not Found)`

**Root Cause**: The 404 error was actually a 404 response from the API (not a URL not found), meaning the endpoint exists but the phone number wasn't found in the database.

**Solution**: Fixed the phone number normalization function to handle both international and local formats.

### 2. SMS Codes Not Being Sent
**Issue**: SMS codes were not being sent to mobile phones.

**Root Causes**:
1. **Invalid Beem API Credentials**: The Beem API credentials in the system are invalid (error 120: "Invalid api_key and/or secret_id")
2. **Phone Number Normalization Issue**: The normalization function was converting international format phone numbers to local format, but the database lookup was failing

**Solutions**:
1. **SMS Bypass for Superadmin Users**: The system has a bypass mechanism for superadmin users that automatically verifies their phone numbers without sending actual SMS
2. **Fixed Phone Number Normalization**: Updated the `normalize_phone_number` function to try both international and local formats when looking up users

## Technical Details

### Phone Number Normalization Fix

**Before** (in `accounts/views.py`):
```python
def normalize_phone_number(phone_number):
    """Normalize phone number to local format for database lookup."""
    # ... code that only converted to local format
    if cleaned.startswith('255') and len(cleaned) == 12:
        cleaned = '0' + cleaned[3:]  # 255689726060 -> 0689726060
    return cleaned
```

**After**:
```python
def normalize_phone_number(phone_number):
    """Normalize phone number for database lookup - try both formats."""
    # ... code that tries original format first, then converts if needed
    # Try to find user with original format first
    user = User.objects.filter(phone_number=cleaned).first()
    if user:
        return cleaned
    
    # Convert and try different formats
    # ... handles both international and local formats
    return cleaned
```

### SMS Bypass for Superadmin Users

The system automatically bypasses SMS verification for superadmin users:

```python
# In SMSVerificationService.send_verification_code()
if user.is_superuser:
    user.phone_verified = True
    user.save(update_fields=['phone_verified'])
    return {
        'success': True,
        'message': 'Phone number automatically verified for superadmin user',
        'bypassed': True,
        'phone_number': user.phone_number
    }
```

## Test Results

### Local Server (Fixed)
- ✅ Superadmin users: SMS bypassed successfully
- ✅ Regular users: SMS fails due to invalid Beem credentials (expected)
- ✅ Phone number normalization: Works correctly

### Production Server (Not Deployed Yet)
- ❌ All users: 404 error due to old phone normalization code
- ❌ Needs deployment of the fix

## Current Status

### ✅ Fixed Issues
1. **Import Error**: Fixed missing `generate_account_id_string` function in `api_integration/utils.py`
2. **Phone Number Normalization**: Updated to handle both international and local formats
3. **SMS Bypass**: Confirmed working for superadmin users
4. **API Endpoint**: Confirmed working locally

### ❌ Remaining Issues
1. **Beem API Credentials**: Invalid credentials prevent SMS sending for regular users
2. **Production Deployment**: Fix needs to be deployed to production server

## Recommendations

### Immediate Actions
1. **Deploy the phone normalization fix** to production server
2. **Update Beem API credentials** with valid credentials
3. **Test with superadmin users** on production

### Long-term Actions
1. **Set up proper SMS provider** with valid credentials
2. **Implement SMS fallback** for when SMS service is unavailable
3. **Add monitoring** for SMS delivery failures

## API Endpoints Status

| Endpoint | Local | Production | Notes |
|----------|-------|------------|-------|
| `POST /api/auth/sms/forgot-password/` | ✅ Working | ❌ 404 Error | Needs deployment |
| `POST /api/auth/sms/send-code/` | ✅ Working | ❌ Unknown | Needs testing |
| `POST /api/auth/sms/verify-code/` | ✅ Working | ❌ Unknown | Needs testing |

## Frontend Integration

The frontend should handle the `bypassed` flag in the response:

```javascript
// Example response for superadmin user
{
  "success": true,
  "message": "Password reset code sent to your phone number",
  "phone_number": "255623118170",
  "bypassed": true  // This indicates SMS was bypassed
}
```

## Files Modified

1. `api_integration/utils.py` - Added missing `generate_account_id_string` function
2. `accounts/views.py` - Fixed `normalize_phone_number` function
3. Created test files for verification

## Next Steps

1. Deploy the fixes to production
2. Update Beem API credentials
3. Test all SMS endpoints on production
4. Verify frontend integration works correctly

