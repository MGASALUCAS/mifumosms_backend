# Quick Frontend Implementation Guide

## The Error Response
```json
{
  "email": "This user already has a pending invitation. You can resend the invitation instead."
}
```

## Quick Fix for Frontend

### Extract Error Message from Response
```javascript
// After fetch
const response = await fetch(url, options);
const data = await response.json();

if (!response.ok && data.email) {
  const errorMessage = data.email; // This is the user-friendly message
  console.log(errorMessage);
  // Show to user
}
```

### Show User-Friendly Message

```javascript
function showErrorMessage(response) {
  if (response.email) {
    // This is the exact error message from backend
    alert(response.email); 
    // Or show in UI:
    // setError(response.email);
  }
}

// Example usage:
const response = await fetch('/api/tenants/{id}/team/invite/', {...});
const data = await response.json();

if (!response.ok) {
  showErrorMessage(data);
}
```

### Handle Specific Error Types

```javascript
function handleInviteError(error) {
  const message = error.email || error.message;

  if (message.includes('pending invitation')) {
    // Show button to resend invitation
    return {
      type: 'pending',
      message: message,
      action: 'resend'
    };
  } else if (message.includes('already an active member')) {
    // Just inform user
    return {
      type: 'active',
      message: message,
      action: 'info'
    };
  } else if (message.includes('suspended')) {
    // Show button to activate
    return {
      type: 'suspended',
      message: message,
      action: 'activate'
    };
  } else {
    // Generic error
    return {
      type: 'error',
      message: message,
      action: 'none'
    };
  }
}
```

## Complete Example

```tsx
const [error, setError] = useState<string | null>(null);
const [showResend, setShowResend] = useState(false);

const inviteMember = async (email: string, role: string) => {
  try {
    const response = await fetch(
      `/api/tenants/${tenantId}/team/invite/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, role })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 400 && data.email) {
        // Show the backend message directly
        setError(data.email);
        
        // If it's a pending invitation, offer to resend
        if (data.email.includes('pending invitation')) {
          setShowResend(true);
        }
      } else {
        setError('Failed to invite member');
      }
      return;
    }

    // Success
    setError(null);
    setShowResend(false);
    alert('Member invited successfully!');
    
  } catch (err) {
    setError('An error occurred');
  }
};

// In JSX:
{error && (
  <div className="error">
    {error}
    {showResend && (
      <button onClick={() => resendInvitation()}>
        Resend Invitation
      </button>
    )}
  </div>
)}
```

## Summary

✅ **Backend sends**: "This user already has a pending invitation. You can resend the invitation instead."

✅ **Frontend receives**: `{ "email": "error message" }`

✅ **Frontend displays**: The exact message from backend

✅ **Frontend can detect**: If message contains "pending invitation" → show "Resend" button

## That's It!

The backend message is already clear and user-friendly. Just:
1. Extract `response.email` from error
2. Show it to the user
3. Optionally detect specific keywords for actions

