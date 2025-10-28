# Team Invitation Guide

## What's Needed to Invite Team Members

### 1. Authentication & Authorization

#### Required Headers
```javascript
{
  "Authorization": "Bearer YOUR_JWT_TOKEN",
  "Content-Type": "application/json"
}
```

#### User Requirements
- ✅ Must be logged in (authenticated)
- ✅ Must be a member of the tenant
- ✅ Must have **Admin** or **Owner** role
  - Owner: Can invite anyone with any role
  - Admin: Can invite with 'admin' or 'agent' roles only
  - Agent: Cannot invite (read-only)

### 2. Request Body

The endpoint expects:
```json
{
  "email": "newmember@example.com",
  "role": "agent"  // Optional: 'owner', 'admin', or 'agent'
}
```

#### Field Details:
- `email` (required): Email address of the person to invite
- `role` (optional, default: 'agent'): Role to assign
  - `'owner'`: Full access to all features and settings
  - `'admin'`: Can manage members (except owners) and settings
  - `'agent'`: Read-only access, cannot manage team

### 3. Role Permissions

| Action | Owner | Admin | Agent |
|--------|-------|-------|-------|
| View Team | ✅ | ✅ | ✅ |
| Invite Members | ✅ | ✅ | ❌ |
| Change Roles | ✅ | Limited | ❌ |
| Remove Members | ✅ | ✅ | ❌ |
| Transfer Ownership | ✅ | ❌ | ❌ |
| Suspend Members | ✅ | ✅ | ❌ |

### 4. What Happens When You Invite

1. **User Check**: System checks if the email exists
   - If exists: Uses existing account
   - If new: Creates a new user account

2. **Membership Created**: Creates a pending membership with:
   - Status: `pending`
   - Invitation token generated
   - Invited by timestamp
   - Role assigned

3. **Email Sent**: Sends invitation email with:
   - Invitation link
   - Tenant name
   - Assigned role
   - Inviter's name

4. **Response**: Returns the membership data including:
   - Member ID
   - User email
   - Role
   - Status (pending)
   - Invitation link

## Example Request

### cURL
```bash
curl -X POST http://localhost:8000/api/tenants/e745958e-282d-45b8-9f3c-630509d28928/team/invite/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newteam@company.com",
    "role": "admin"
  }'
```

### JavaScript (Fetch)
```javascript
const response = await fetch('/api/tenants/e745958e-282d-45b8-9f3c-630509d28928/team/invite/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'newteam@company.com',
    role: 'admin'
  })
});

const result = await response.json();
console.log(result);
```

### Response
```json
{
  "id": "uuid",
  "user": "uuid",
  "user_email": "newteam@company.com",
  "user_name": "",
  "role": "admin",
  "role_display": "Admin",
  "status": "pending",
  "status_display": "Pending",
  "invited_by": "uuid",
  "invited_by_email": "owner@company.com",
  "invited_by_name": "John Doe",
  "invited_at": "2025-10-28T19:00:00Z",
  "joined_at": null
}
```

## Error Handling

### Common Errors

#### 400 Bad Request
```json
{
  "email": ["This field is required."]
}
```
**Fix**: Include the email field in request body

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Fix**: User needs Admin or Owner role

#### 400 Already a Member
```json
{
  "email": ["User is already a member of this tenant."]
}
```
**Fix**: User is already invited or is a member

#### 500 Server Error
```json
{
  "error": "Failed to send invitation email"
}
```
**Fix**: Email sending failed but member was created. Check email configuration.

## Frontend Implementation

### React Example
```jsx
import { useState } from 'react';

function InviteTeamMember({ tenantId, token }) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('agent');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleInvite = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

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
        throw new Error(data.email?.[0] || data.detail || 'Failed to invite member');
      }

      setSuccess(true);
      setEmail('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleInvite}>
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label>Role:</label>
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="agent">Agent (View Only)</option>
          <option value="admin">Admin (Manage Team)</option>
        </select>
      </div>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">Member invited successfully!</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Inviting...' : 'Invite Member'}
      </button>
    </form>
  );
}
```

## Testing the Endpoint

### Test with Postman
1. Method: `POST`
2. URL: `http://localhost:8000/api/tenants/{tenant_id}/team/invite/`
3. Headers:
   - Key: `Authorization`, Value: `Bearer YOUR_TOKEN`
   - Key: `Content-Type`, Value: `application/json`
4. Body (raw JSON):
```json
{
  "email": "test@example.com",
  "role": "agent"
}
```

### Verify Your User Has Permissions
```javascript
// Check if you're an admin/owner
const checkPermissions = async (tenantId) => {
  const response = await fetch(`/api/tenants/${tenantId}/team/stats/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (response.ok) {
    console.log('You have permission to view team stats');
    return true;
  }
  return false;
};
```

## Summary Checklist

Before inviting:
- [ ] User is logged in
- [ ] Valid JWT token in Authorization header
- [ ] User is Admin or Owner of the tenant
- [ ] Email address is valid format
- [ ] Role is appropriate for user's permissions
- [ ] Email configuration is set up (optional, invitations still work)

## Minimal Requirements

**Absolute minimum to make this work:**
1. JWT token in Authorization header
2. Valid email in request body
3. Admin/Owner permissions

**Optional:**
- Role field (defaults to 'agent')
- Email configuration (member still created, just no email sent)
