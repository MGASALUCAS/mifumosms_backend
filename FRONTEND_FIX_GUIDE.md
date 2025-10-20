# Frontend Integration Fix Guide

## Issues Fixed

### 1. ✅ Missing Stats Endpoint
- **Problem**: `GET /api/messaging/sender-requests/stats/` returned 404
- **Solution**: Added the endpoint in `messaging/urls_sender_requests.py` and `messaging/views_sender_requests.py`
- **Status**: ✅ WORKING

### 2. ❌ Submit Endpoint 400 Error
- **Problem**: `POST /api/messaging/sender-requests/submit/` returns 400 Bad Request
- **Root Cause**: Frontend is missing required `business_justification` field
- **Solution**: Update frontend to send all required fields

## Required Frontend Changes

### Update the submitSenderRequest function in api.ts:

```javascript
// OLD (causing 400 error):
const submitSenderRequest = async (data) => {
  const response = await fetch('/api/messaging/sender-requests/submit/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      requested_sender_id: data.senderId,
      sample_content: data.sampleContent
      // Missing business_justification field!
    })
  });
  return response.json();
};

// NEW (working version):
const submitSenderRequest = async (data) => {
  const response = await fetch('/api/messaging/sender-requests/submit/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      request_type: 'custom', // or 'default'
      requested_sender_id: data.senderId,
      sample_content: data.sampleContent,
      business_justification: data.businessJustification || 'Default business justification for SMS sender ID request.'
    })
  });
  return response.json();
};
```

### Update the form in SenderNames.tsx:

```jsx
// Add business justification field to your form:
<form onSubmit={handleRequestSenderName}>
  <input
    type="text"
    placeholder="Sender ID (max 11 characters)"
    value={senderId}
    onChange={(e) => setSenderId(e.target.value)}
    maxLength={11}
  />
  
  <textarea
    placeholder="Sample message content (max 170 characters)"
    value={sampleContent}
    onChange={(e) => setSampleContent(e.target.value)}
    maxLength={170}
  />
  
  {/* ADD THIS FIELD: */}
  <textarea
    placeholder="Business justification (required)"
    value={businessJustification}
    onChange={(e) => setBusinessJustification(e.target.value)}
    required
  />
  
  <button type="submit">Submit Request</button>
</form>
```

### Add state for business justification:

```jsx
const [businessJustification, setBusinessJustification] = useState('');
```

## API Endpoints Status

### ✅ Working Endpoints:
- `GET /api/messaging/sender-requests/stats/` - Returns statistics
- `GET /api/messaging/sender-requests/` - Lists requests
- `POST /api/messaging/sender-requests/submit/` - Creates request (with correct data)

### Required Fields for Submit:
```json
{
  "request_type": "custom", // or "default"
  "requested_sender_id": "YOUR-SENDER-ID",
  "sample_content": "Your sample message content",
  "business_justification": "Why you need this sender ID"
}
```

## Test Results

✅ **Backend is working correctly** - All endpoints tested and functional
❌ **Frontend needs update** - Missing required field in form submission

## Quick Test

You can test the API directly with curl:

```bash
curl -X POST http://127.0.0.1:8000/api/messaging/sender-requests/submit/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "request_type": "custom",
    "requested_sender_id": "TEST-SMS",
    "sample_content": "This is a test message",
    "business_justification": "Testing our SMS functionality"
  }'
```

This should return a 201 status with the created request data.
