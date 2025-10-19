# 🏢 Tenant Management API Documentation

## Overview

The Tenant Management API provides comprehensive multi-tenant functionality for the Mifumo WMS platform. It allows users to create, manage, and switch between different business organizations (tenants), manage team members, and configure custom domains.

## 🔐 Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

## 🏢 Multi-Tenant Architecture

The system uses a multi-tenant architecture where:
- Each user can belong to multiple tenants
- Each tenant has its own isolated data
- Users can switch between tenants they have access to
- All billing, messaging, and other data is tenant-scoped

## 📋 API Endpoints

### 1. Tenant Management

#### Get User's Tenants
```http
GET /api/tenants/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "John Doe's Organization",
      "subdomain": "johndoe",
      "timezone": "UTC",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "business_name": "John Doe's Company",
      "business_type": "Technology",
      "phone_number": "+255712345678",
      "email": "john@example.com",
      "address": "123 Main St, Dar es Salaam",
      "wa_phone_number_id": "",
      "wa_phone_number": "",
      "wa_verified": false,
      "is_active": true,
      "trial_ends_at": "2024-02-01T00:00:00Z",
      "is_trial_active": true
    }
  ]
}
```

#### Create New Tenant
```http
POST /api/tenants/
```

**Request Body:**
```json
{
  "name": "My New Company",
  "subdomain": "mynewcompany",
  "timezone": "Africa/Dar_es_Salaam",
  "business_name": "My New Company Ltd",
  "business_type": "Technology",
  "phone_number": "+255712345678",
  "email": "contact@mynewcompany.com",
  "address": "456 Business Ave, Dar es Salaam"
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My New Company",
  "subdomain": "mynewcompany",
  "timezone": "Africa/Dar_es_Salaam",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "business_name": "My New Company Ltd",
  "business_type": "Technology",
  "phone_number": "+255712345678",
  "email": "contact@mynewcompany.com",
  "address": "456 Business Ave, Dar es Salaam",
  "wa_phone_number_id": "",
  "wa_phone_number": "",
  "wa_verified": false,
  "is_active": true,
  "trial_ends_at": "2024-02-01T00:00:00Z",
  "is_trial_active": true
}
```

#### Get Tenant Details
```http
GET /api/tenants/{tenant_id}/
```

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe's Organization",
  "subdomain": "johndoe",
  "timezone": "UTC",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "business_name": "John Doe's Company",
  "business_type": "Technology",
  "phone_number": "+255712345678",
  "email": "john@example.com",
  "address": "123 Main St, Dar es Salaam",
  "wa_phone_number_id": "",
  "wa_phone_number": "",
  "wa_verified": false,
  "is_active": true,
  "trial_ends_at": "2024-02-01T00:00:00Z",
  "is_trial_active": true
}
```

#### Update Tenant
```http
PUT /api/tenants/{tenant_id}/
PATCH /api/tenants/{tenant_id}/
```

**Request Body:**
```json
{
  "name": "Updated Company Name",
  "business_name": "Updated Business Name",
  "phone_number": "+255712345679",
  "email": "newemail@example.com",
  "address": "New Address, City"
}
```

#### Delete Tenant
```http
DELETE /api/tenants/{tenant_id}/
```

**Response:**
```json
{
  "message": "Tenant deleted successfully"
}
```

### 2. Tenant Switching

#### Switch Current Tenant
```http
POST /api/tenants/switch/
```

**Request Body:**
```json
{
  "tenant_id": "uuid"
}
```

**Response:**
```json
{
  "message": "Successfully switched to tenant",
  "tenant": {
    "id": "uuid",
    "name": "John Doe's Organization",
    "subdomain": "johndoe"
  }
}
```

### 3. Domain Management

#### Get Tenant Domains
```http
GET /api/tenants/{tenant_id}/domains/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "domain": "johndoe.mifumo.local",
      "is_primary": true,
      "verified": true,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "domain": "mycompany.com",
      "is_primary": false,
      "verified": false,
      "created_at": "2024-01-01T00:01:00Z"
    }
  ]
}
```

#### Add Custom Domain
```http
POST /api/tenants/{tenant_id}/domains/
```

**Request Body:**
```json
{
  "domain": "mycompany.com",
  "is_primary": false
}
```

**Response:**
```json
{
  "id": "uuid",
  "domain": "mycompany.com",
  "is_primary": false,
  "verified": false,
  "created_at": "2024-01-01T00:01:00Z"
}
```

#### Update Domain
```http
PUT /api/tenants/{tenant_id}/domains/{domain_id}/
PATCH /api/tenants/{tenant_id}/domains/{domain_id}/
```

**Request Body:**
```json
{
  "is_primary": true,
  "verified": true
}
```

#### Delete Domain
```http
DELETE /api/tenants/{tenant_id}/domains/{domain_id}/
```

**Response:**
```json
{
  "message": "Domain deleted successfully"
}
```

### 4. Membership Management

#### Get Tenant Members
```http
GET /api/tenants/{tenant_id}/members/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "user": "uuid",
      "user_email": "john@example.com",
      "user_name": "John Doe",
      "role": "owner",
      "status": "active",
      "invited_by": null,
      "invited_by_email": null,
      "invited_at": "2024-01-01T00:00:00Z",
      "joined_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "user": "uuid",
      "user_email": "jane@example.com",
      "user_name": "Jane Smith",
      "role": "admin",
      "status": "pending",
      "invited_by": "uuid",
      "invited_by_email": "john@example.com",
      "invited_at": "2024-01-01T00:01:00Z",
      "joined_at": null
    }
  ]
}
```

#### Invite New Member
```http
POST /api/tenants/{tenant_id}/members/
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "role": "agent"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user": "uuid",
  "user_email": "newuser@example.com",
  "user_name": "",
  "role": "agent",
  "status": "pending",
  "invited_by": "uuid",
  "invited_by_email": "john@example.com",
  "invited_at": "2024-01-01T00:02:00Z",
  "joined_at": null
}
```

#### Update Member Role/Status
```http
PUT /api/tenants/{tenant_id}/members/{membership_id}/
PATCH /api/tenants/{tenant_id}/members/{membership_id}/
```

**Request Body:**
```json
{
  "role": "admin",
  "status": "active"
}
```

#### Remove Member
```http
DELETE /api/tenants/{tenant_id}/members/{membership_id}/
```

**Response:**
```json
{
  "message": "Member removed successfully"
}
```

### 5. Invitation Management

#### Accept Invitation
```http
GET /api/tenants/invite/{token}/
```

**Response:**
```json
{
  "message": "Invitation accepted successfully",
  "tenant": {
    "id": "uuid",
    "name": "John Doe's Organization",
    "subdomain": "johndoe"
  },
  "membership": {
    "id": "uuid",
    "role": "agent",
    "status": "active"
  }
}
```

## 🔧 Data Models

### Tenant
```json
{
  "id": "uuid",
  "name": "string",
  "subdomain": "string (unique)",
  "timezone": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "business_name": "string",
  "business_type": "string",
  "phone_number": "string",
  "email": "email",
  "address": "text",
  "wa_phone_number_id": "string",
  "wa_phone_number": "string",
  "wa_verified": "boolean",
  "is_active": "boolean",
  "trial_ends_at": "datetime|null",
  "is_trial_active": "boolean (computed)"
}
```

### Domain
```json
{
  "id": "uuid",
  "domain": "string",
  "is_primary": "boolean",
  "verified": "boolean",
  "created_at": "datetime"
}
```

### Membership
```json
{
  "id": "uuid",
  "user": "uuid",
  "role": "owner|admin|agent",
  "status": "active|pending|suspended",
  "invited_by": "uuid|null",
  "invited_at": "datetime",
  "joined_at": "datetime|null"
}
```

## 🔐 Permissions

### Role-Based Access Control

#### Owner
- Full access to all tenant operations
- Can manage all members and their roles
- Can delete the tenant
- Can manage domains and settings

#### Admin
- Can manage members (except other owners)
- Can manage domains and settings
- Cannot delete the tenant
- Cannot change owner roles

#### Agent
- Read-only access to tenant information
- Can view members list
- Cannot manage members or settings

### Permission Classes
- `IsAuthenticated`: User must be logged in
- `IsTenantMember`: User must be a member of the tenant
- `IsTenantAdmin`: User must be admin or owner
- `IsTenantOwner`: User must be the owner

## 📝 Validation Rules

### Subdomain Validation
- **Uniqueness**: Must be unique across all tenants
- **Characters**: Only letters, numbers, hyphens, and underscores
- **Length**: 3-100 characters
- **Format**: Cannot start or end with hyphen

### Business Information
- **Email**: Valid email format
- **Phone**: International format recommended
- **Timezone**: Must be valid timezone identifier

### Member Invitations
- **Email**: Must be valid email format
- **Role**: Must be one of: owner, admin, agent
- **Uniqueness**: User cannot be invited twice to same tenant

## 🔄 Workflow

### 1. Tenant Creation
1. User creates tenant via `POST /api/tenants/`
2. System automatically creates owner membership
3. Default domain is created (subdomain.mifumo.local)
4. Trial period starts (30 days)

### 2. Member Invitation
1. Admin/owner invites member via `POST /api/tenants/{id}/members/`
2. System sends invitation email with token
3. User clicks link to accept invitation
4. Membership status changes to active

### 3. Tenant Switching
1. User calls `POST /api/tenants/switch/` with tenant ID
2. System validates user has access to tenant
3. Current tenant context is updated
4. All subsequent requests are scoped to new tenant

### 4. Domain Management
1. Admin adds custom domain via `POST /api/tenants/{id}/domains/`
2. Domain verification process begins
3. Once verified, domain can be set as primary
4. Old primary domain becomes secondary

## 🔧 Error Handling

### Error Response Format
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

### Common Validation Errors
- `"This subdomain is already taken"` - Subdomain already exists
- `"Subdomain can only contain letters, numbers, hyphens, and underscores"` - Invalid characters
- `"Subdomain cannot start or end with a hyphen"` - Invalid format
- `"User is already a member of this tenant"` - Duplicate membership
- `"You don't have access to this tenant"` - Insufficient permissions
- `"User not found"` - Email doesn't exist in system

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## 🚀 Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per hour per user for tenant operations
- 50 requests per hour per user for member management
- 20 requests per hour per user for domain management
- Burst allowance: 10 requests per second

## 📝 Notes

1. **Automatic Tenant Creation**: New users automatically get a tenant created
2. **Trial Period**: All new tenants get 30-day trial period
3. **Domain Verification**: Custom domains require verification before use
4. **Member Limits**: Free tier has member limits, paid tiers have higher limits
5. **Data Isolation**: All tenant data is completely isolated
6. **Owner Transfer**: Owners can transfer ownership to other members
7. **Soft Delete**: Deleted tenants are soft-deleted and can be restored
8. **Audit Trail**: All tenant operations are logged for compliance

## 🔗 Integration with Other APIs

### Billing Integration
- Each tenant has its own billing account
- SMS credits are tenant-scoped
- Payment transactions are isolated by tenant

### Messaging Integration
- Sender IDs are tenant-scoped
- SMS campaigns are isolated by tenant
- Contact lists are tenant-specific

### User Management
- Users can belong to multiple tenants
- Each tenant membership has its own role
- User permissions are context-aware
