# Fix for "Failed to send invitation" Error

## The Problem

Frontend shows:
```
"Failed to send invitation"
"Request failed"
```

But backend sends:
```json
{
  "email": "This user already has a pending invitation. You can resend the invitation instead."
}
```

## The Fix

### In Frontend Error Handler

```javascript
// BEFORE (shows generic message)
catch (error) {
  setError('Failed to send invitation');
  // WRONG - shows generic message
}

// AFTER (shows backend message)
catch (error) {
  // Get the actual backend error message
  const errorData = await error.response.json();
  
  if (errorData.email) {
    // Use the backend's user-friendly message
    setError(errorData.email);
  } else {
    // Fallback for other errors
    setError('Failed to send invitation');
  }
}
```

### Complete Example

```javascript
const inviteMember = async (email, role) => {
  try {
    const response = await fetch(`/api/tenants/${tenantId}/team/invite/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, role })
    });

    const data = await response.json();

    if (!response.ok) {
      // Check for backend error message
      if (data.email) {
        // Backend sends specific message in "email" field
        setError(data.email);
      } else {
        // Generic error
        setError(data.detail || 'Failed to invite member');
      }
      return;
    }

    // Success
    setError(null);
    alert('Member invited successfully!');
    
  } catch (error) {
    // Network or other errors
    setError('An error occurred. Please try again.');
  }
};
```

## What's Happening

Backend returns:
```json
HTTP 400
{
  "email": "This user already has a pending invitation. You can resend the invitation instead."
}
```

Frontend should extract and display: **`data.email`**

## Quick Fix Steps

1. **Find your invite function** in the frontend
2. **Look for error handling** like `setError('Failed...')`
3. **Replace with** `setError(data.email || 'Failed...')`

That's it!

