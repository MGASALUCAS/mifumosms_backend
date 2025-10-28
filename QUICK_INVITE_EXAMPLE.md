# Quick Team Member Invitation Guide

## Yes, Email is Required! ✅

When inviting a team member, you **MUST** include the `email` field in your request.

## Minimum Request

```json
{
  "email": "someone@company.com"
}
```

This will create an invitation with:
- Role: `agent` (default)
- Status: `pending`

## Complete Request

```json
{
  "email": "someone@company.com",
  "role": "admin"
}
```

## Example API Call

```javascript
// Minimum - just email
fetch('/api/tenants/{tenant_id}/team/invite/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'someone@company.com'
  })
});

// Complete - with role
fetch('/api/tenants/{tenant_id}/team/invite/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'someone@company.com',
    role: 'admin'
  })
});
```

## What Happens with Email

1. **System receives** email address
2. **Checks** if user with that email exists
   - If exists: Uses existing user
   - If new: Creates new user account
3. **Creates** membership with status: `pending`
4. **Sends** invitation email (if configured)
5. **Returns** membership data

## Without Email Field

If you don't include email, you'll get:

```json
{
  "email": ["This field is required."]
}
```

**Status**: 400 Bad Request

## Summary

✅ **Required**: `email` field  
✅ **Optional**: `role` field (defaults to 'agent')  
✅ **Optional**: Email SMTP configuration (invitations still work)

The `email` field is **mandatory** because:
- It identifies who to invite
- System uses it to create/link user accounts
- Invitation is sent to this address

