# Frontend Update Instructions

## Backend Changes Made

The backend has been updated to remove the `business_justification` field requirement. Here are the changes you need to make in your frontend:

## 1. Update API Call for Sender ID Request Submission

### OLD Code (causing 400 error):
```javascript
// In your api.ts file
const submitSenderRequest = async (data) => {
  const response = await fetch('/api/messaging/sender-requests/submit/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      requested_sender_id: data.senderId,
      sample_content: data.sampleContent,
      business_justification: data.businessJustification // ❌ REMOVE THIS
    })
  });
  return response.json();
};
```

### NEW Code (working version):
```javascript
// In your api.ts file
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
      // ✅ business_justification field removed
    })
  });
  return response.json();
};
```

## 2. Update Form Component

### Remove Business Justification Field

In your `SenderNames.tsx` or similar component:

```jsx
// OLD Form (remove business justification field)
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
  
  {/* ❌ REMOVE THIS FIELD */}
  <textarea
    placeholder="Business justification (required)"
    value={businessJustification}
    onChange={(e) => setBusinessJustification(e.target.value)}
    required
  />
  
  <button type="submit">Submit Request</button>
</form>

// NEW Form (simplified)
<form onSubmit={handleRequestSenderName}>
  <input
    type="text"
    placeholder="Sender ID (max 11 characters)"
    value={senderId}
    onChange={(e) => setSenderId(e.target.value)}
    maxLength={11}
    required
  />
  
  <textarea
    placeholder="Sample message content (max 170 characters)"
    value={sampleContent}
    onChange={(e) => setSampleContent(e.target.value)}
    maxLength={170}
    required
  />
  
  <button type="submit">Submit Request</button>
</form>
```

## 3. Update State Management

### Remove Business Justification State

```javascript
// OLD State (remove business justification)
const [senderId, setSenderId] = useState('');
const [sampleContent, setSampleContent] = useState('');
const [businessJustification, setBusinessJustification] = useState(''); // ❌ REMOVE

// NEW State (simplified)
const [senderId, setSenderId] = useState('');
const [sampleContent, setSampleContent] = useState('');
```

## 4. Update Form Validation

### Remove Business Justification Validation

```javascript
// OLD Validation (remove business justification check)
const validateForm = () => {
  if (!senderId.trim()) {
    setError('Sender ID is required');
    return false;
  }
  if (!sampleContent.trim()) {
    setError('Sample content is required');
    return false;
  }
  if (!businessJustification.trim()) { // ❌ REMOVE THIS
    setError('Business justification is required');
    return false;
  }
  return true;
};

// NEW Validation (simplified)
const validateForm = () => {
  if (!senderId.trim()) {
    setError('Sender ID is required');
    return false;
  }
  if (!sampleContent.trim()) {
    setError('Sample content is required');
    return false;
  }
  return true;
};
```

## 5. Update Form Submission Handler

```javascript
// OLD Handler (remove business justification)
const handleRequestSenderName = async (e) => {
  e.preventDefault();
  
  if (!validateForm()) return;
  
  setLoading(true);
  setError(null);
  
  try {
    const result = await submitSenderRequest({
      senderId: senderId.trim(),
      sampleContent: sampleContent.trim(),
      businessJustification: businessJustification.trim() // ❌ REMOVE
    });
    
    if (result.success) {
      // Handle success
      setSenderId('');
      setSampleContent('');
      setBusinessJustification(''); // ❌ REMOVE
    } else {
      setError(result.message || 'Failed to submit request');
    }
  } catch (error) {
    setError('Network error: ' + error.message);
  } finally {
    setLoading(false);
  }
};

// NEW Handler (simplified)
const handleRequestSenderName = async (e) => {
  e.preventDefault();
  
  if (!validateForm()) return;
  
  setLoading(true);
  setError(null);
  
  try {
    const result = await submitSenderRequest({
      senderId: senderId.trim(),
      sampleContent: sampleContent.trim()
    });
    
    if (result.success) {
      // Handle success
      setSenderId('');
      setSampleContent('');
    } else {
      setError(result.message || 'Failed to submit request');
    }
  } catch (error) {
    setError('Network error: ' + error.message);
  } finally {
    setLoading(false);
  }
};
```

## 6. API Endpoints Status

### ✅ Working Endpoints:
- `POST /api/messaging/sender-requests/submit/` - Submit new request
- `GET /api/messaging/sender-requests/stats/` - Get statistics
- `GET /api/messaging/sender-requests/` - List all requests

### Required Data Format:
```json
{
  "requested_sender_id": "YOUR-SENDER-ID",
  "sample_content": "Your sample message content"
}
```

## 7. Test Your Changes

After making these changes, test with:

```javascript
// Test data
const testData = {
  requested_sender_id: "TEST-SMS",
  sample_content: "This is a test message for validation."
};

// Should return 201 status with success: true
```

## 8. Error Handling

The backend now returns proper error messages:

```javascript
// Success response
{
  "success": true,
  "message": "Sender ID request submitted successfully",
  "data": {
    "id": "uuid",
    "requested_sender_id": "TEST-SMS",
    "status": "pending",
    "created_at": "2025-10-19T18:05:59.057125Z"
  }
}

// Error response
{
  "success": false,
  "message": "Invalid request data",
  "errors": {
    "requested_sender_id": ["This field is required."],
    "sample_content": ["This field is required."]
  }
}
```

## Summary of Changes

1. **Remove** `business_justification` field from form
2. **Remove** `business_justification` from API call
3. **Remove** `business_justification` from state management
4. **Remove** `business_justification` from validation
5. **Keep** only `requested_sender_id` and `sample_content`

## Backend Status

✅ **All endpoints are working correctly**
✅ **Data is being saved to database**
✅ **Admin interface shows all requests**
✅ **No more business_justification field required**

Your frontend should now work perfectly with the updated backend!

