# Forgot Password SMS Endpoint Fix

## Problem

The `/api/auth/sms/forgot-password/` endpoint was returning a generic 400 error without details about what was wrong.

## Root Cause

The endpoint was not using proper serializer validation, so when the request failed, it returned a generic error message without indicating what fields were missing or invalid.

## Solution

Updated the endpoint to:
1. Use proper DRF serializer validation
2. Return detailed error messages with field-level errors
3. Add logging for debugging request issues
4. Catch and handle parsing errors gracefully

## Changes Made

### Before:
```python
phone_number = request.data.get('phone_number')

if not phone_number:
    return Response({
        'success': False,
        'error': 'Phone number is required.'
    }, status=status.HTTP_400_BAD_REQUEST)
```

### After:
```python
from .serializers import SendVerificationCodeSerializer

# Validate request data
serializer = SendVerificationCodeSerializer(data=request.data)
if not serializer.is_valid():
    return Response({
        'success': False,
        'error': 'Invalid request data.',
        'errors': serializer.errors  # ← Detailed validation errors
    }, status=status.HTTP_400_BAD_REQUEST)

phone_number = serializer.validated_data['phone_number']
```

## Expected Error Responses

Now when validation fails, you'll get detailed errors:

### Missing Phone Number:
```json
{
  "success": false,
  "error": "Invalid request data.",
  "errors": {
    "phone_number": ["This field is required."]
  }
}
```

### Invalid Phone Format:
```json
{
  "success": false,
  "error": "Invalid request data.",
  "errors": {
    "phone_number": ["Invalid phone number format."]
  }
}
```

### Parsing Error:
```json
{
  "success": false,
  "error": "Request parsing error: ...",
  "received_data": "..."
}
```

## How to Debug

1. Check server logs - the endpoint now logs:
   - Request method
   - Content type
   - Request data type
   - Actual request data
   - Serializer errors

2. Look for these log messages:
   ```
   INFO: Request method: POST
   INFO: Request content type: application/json
   INFO: Request data: {'phone_number': '...'}
   ERROR: Serializer errors: {'phone_number': ['This field is required.']}
   ```

## Testing

Test the endpoint with curl:

```bash
# Correct request
curl -X POST http://127.0.0.1:8000/api/auth/sms/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+255689726060"}'

# Missing phone_number - will show detailed error
curl -X POST http://127.0.0.1:8000/api/auth/sms/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Invalid format - will show validation error
curl -X POST http://127.0.0.1:8000/api/auth/sms/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "123"}'
```

## Next Steps

1. Restart the Django server to pick up changes
2. Try the endpoint again
3. Check logs to see what data is being sent
4. Error responses will now be detailed and helpful

