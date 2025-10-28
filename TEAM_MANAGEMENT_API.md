# Team Management API Endpoints

Complete team management system for tenant organizations with role-based access control.

## 📋 Overview

The team management system allows tenant owners and admins to:
- View team members and their roles
- Invite new members via email
- Manage member roles and status
- Handle invitations (accept/reject)
- Transfer ownership
- Suspend/activate members

## 🔐 Permissions

### Role Hierarchy
- **Owner**: Full access, can manage all members including other owners
- **Admin**: Can manage members (except owners), cannot assign owner role
- **Agent**: Read-only access to team information

### Permission Classes
- `IsAuthenticated`: User must be logged in
- `IsTenantMember`: User must be a member of the tenant
- `IsTenantAdmin`: User must be admin or owner
- `IsTenantOwner`: User must be the owner

## 🚀 API Endpoints

### 1. List Team Members
**GET** `/api/tenants/{tenant_id}/team/`

List all team members for the current tenant.

**Permissions**: `IsAuthenticated`, `IsTenantMember`

**Response**:
```json
[
  {
    "id": "uuid",
    "user": "uuid",
    "user_email": "john@company.com",
    "user_name": "John Doe",
    "user_first_name": "John",
    "user_last_name": "Doe",
    "user_avatar": "url",
    "role": "admin",
    "role_display": "Admin",
    "status": "active",
    "status_display": "Active",
    "invited_by": "uuid",
    "invited_by_email": "owner@company.com",
    "invited_by_name": "Owner Name",
    "invited_at": "2024-01-01T00:00:00Z",
    "joined_at": "2024-01-01T00:00:00Z"
  }
]
```

### 2. Invite Team Member
**POST** `/api/tenants/{tenant_id}/team/invite/`

Invite a new team member via email.

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Request Body**:
```json
{
  "email": "newmember@company.com",
  "role": "agent"
}
```

**Response**:
```json
{
  "id": "uuid",
  "user": "uuid",
  "user_email": "newmember@company.com",
  "user_name": "",
  "role": "agent",
  "status": "pending",
  "invited_at": "2024-01-01T00:00:00Z"
}
```

### 3. Get Team Statistics
**GET** `/api/tenants/{tenant_id}/team/stats/`

Get team statistics and member counts.

**Permissions**: `IsAuthenticated`, `IsTenantMember`

**Response**:
```json
{
  "total_members": 10,
  "active_members": 8,
  "pending_members": 2,
  "suspended_members": 0,
  "owners": 1,
  "admins": 3,
  "agents": 4
}
```

### 4. Get Team Member Details
**GET** `/api/tenants/{tenant_id}/team/{member_id}/`

Get detailed information about a specific team member.

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Response**: Same as team member object in list response.

### 5. Update Team Member
**PUT/PATCH** `/api/tenants/{tenant_id}/team/{member_id}/`

Update team member role or status.

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Request Body**:
```json
{
  "role": "admin",
  "status": "active"
}
```

**Response**: Updated team member object.

### 6. Remove Team Member
**DELETE** `/api/tenants/{tenant_id}/team/{member_id}/`

Remove a team member from the tenant.

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Response**:
```json
{
  "message": "Team member removed successfully"
}
```

### 7. Suspend Team Member
**POST** `/api/tenants/{tenant_id}/team/{member_id}/suspend/`

Suspend a team member (cannot be used on owners).

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Response**:
```json
{
  "message": "John Doe has been suspended"
}
```

### 8. Activate Team Member
**POST** `/api/tenants/{tenant_id}/team/{member_id}/activate/`

Activate a suspended team member.

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Response**:
```json
{
  "message": "John Doe has been activated"
}
```

### 9. Resend Invitation
**POST** `/api/tenants/{tenant_id}/team/{member_id}/resend-invitation/`

Resend invitation email to a pending member.

**Permissions**: `IsAuthenticated`, `IsTenantAdmin`

**Response**:
```json
{
  "message": "Invitation resent successfully"
}
```

### 10. Transfer Ownership
**POST** `/api/tenants/{tenant_id}/team/{member_id}/transfer-ownership/`

Transfer ownership to another active member.

**Permissions**: `IsAuthenticated`, `IsTenantOwner`

**Response**:
```json
{
  "message": "Ownership transferred to John Doe"
}
```

### 11. Accept Invitation
**POST** `/api/invite/{token}/accept/`

Accept a tenant invitation using the invitation token.

**Permissions**: `IsAuthenticated`

**Response**:
```json
{
  "message": "Successfully joined Company Name",
  "tenant": {
    "id": "uuid",
    "name": "Company Name",
    "subdomain": "company"
  },
  "role": "agent"
}
```

### 12. Reject Invitation
**POST** `/api/invite/{token}/reject/`

Reject a tenant invitation using the invitation token.

**Permissions**: `IsAuthenticated`

**Response**:
```json
{
  "message": "Invitation rejected successfully"
}
```

## 📝 Validation Rules

### Role Assignment
- Only owners can assign owner role
- Admins can assign admin and agent roles
- Agents cannot assign any roles

### Status Management
- Owners cannot be suspended
- Only active members can be suspended
- Only suspended members can be activated

### Ownership Transfer
- Only owners can transfer ownership
- Cannot transfer to suspended members
- Previous owner becomes admin after transfer

### Invitation Management
- Invitation tokens expire after 7 days
- Users can only accept invitations meant for their account
- Duplicate invitations are prevented

## 🔄 Error Handling

### Common Error Responses

**400 Bad Request**:
```json
{
  "error": "User is already a member of this tenant"
}
```

**403 Forbidden**:
```json
{
  "error": "Only owners can assign owner role"
}
```

**404 Not Found**:
```json
{
  "error": "Membership not found"
}
```

## 📧 Email Templates

### Invitation Email
```
Subject: You're invited to join {tenant_name} on Mifumo

Hi there,

{inviter_name} has invited you to join {tenant_name} on Mifumo WMS.

Your role will be: {role_display}

Click the link below to accept the invitation:
{invitation_url}

If you don't have an account yet, you'll be able to create one after clicking the link.

Best regards,
The Mifumo Team
```

## 🔧 Frontend Integration

### Example: List Team Members
```javascript
const response = await fetch('/api/tenants/{tenant_id}/team/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const teamMembers = await response.json();
```

### Example: Invite Member
```javascript
const response = await fetch('/api/tenants/{tenant_id}/team/invite/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'newmember@company.com',
    role: 'agent'
  })
});
```

### Example: Accept Invitation
```javascript
const response = await fetch(`/api/invite/${token}/accept/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

## 🚨 Security Considerations

1. **Token Security**: Invitation tokens are randomly generated and expire
2. **Role Validation**: Server-side validation prevents privilege escalation
3. **Email Verification**: Invitations are sent to verified email addresses
4. **Audit Trail**: All membership changes are logged with timestamps
5. **Permission Checks**: Every action is validated against user permissions

## 📊 Database Schema

### Membership Model
```python
class Membership(models.Model):
    id = models.UUIDField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(choices=['owner', 'admin', 'agent'])
    status = models.CharField(choices=['active', 'pending', 'suspended'])
    invited_by = models.ForeignKey(User, null=True, blank=True)
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    invitation_token = models.CharField(max_length=32, blank=True, null=True)
```

This comprehensive team management system provides all the functionality needed for managing team members in a multi-tenant application with proper security and role-based access control.
