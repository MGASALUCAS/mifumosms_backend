# 📱 Sender ID Management API Documentation

## Overview

The Sender ID Management API allows users to request, manage, and use SMS sender IDs for their messaging campaigns. Users can request both default and custom sender IDs, with approval workflows for custom requests.

## 🔐 Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

## 🏢 Multi-Tenant Support

The API is designed for multi-tenant architecture where each user belongs to a tenant. All sender ID data is automatically isolated by tenant.

## 📋 API Endpoints

### 1. Sender ID Request Management

#### Get Sender ID Requests
```http
GET /api/messaging/sender-id-requests/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "tenant": "uuid",
      "user": "uuid",
      "request_type": "custom",
      "requested_sender_id": "MYCOMPANY",
      "sample_content": "Hello from MyCompany! This is a test message.",
      "business_justification": "We need this sender ID for our customer communications.",
      "status": "pending",
      "reviewed_by": null,
      "reviewed_at": null,
      "rejection_reason": "",
      "sms_package": "uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "user_email": "user@example.com",
      "tenant_name": "John Doe's Organization",
      "reviewed_by_email": null,
      "sms_package_name": "Lite Package"
    }
  ]
}
```

#### Create Sender ID Request
```http
POST /api/messaging/sender-id-requests/
```

**Request Body:**
```json
{
  "request_type": "custom",
  "requested_sender_id": "MYCOMPANY",
  "sample_content": "Hello from MyCompany! This is a test message.",
  "business_justification": "We need this sender ID for our customer communications.",
  "sms_package": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "tenant": "uuid",
  "user": "uuid",
  "request_type": "custom",
  "requested_sender_id": "MYCOMPANY",
  "sample_content": "Hello from MyCompany! This is a test message.",
  "business_justification": "We need this sender ID for our customer communications.",
  "status": "pending",
  "reviewed_by": null,
  "reviewed_at": null,
  "rejection_reason": "",
  "sms_package": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "user_email": "user@example.com",
  "tenant_name": "John Doe's Organization",
  "reviewed_by_email": null,
  "sms_package_name": "Lite Package"
}
```

#### Get Sender ID Request Details
```http
GET /api/messaging/sender-id-requests/{request_id}/
```

**Response:**
```json
{
  "id": "uuid",
  "tenant": "uuid",
  "user": "uuid",
  "request_type": "custom",
  "requested_sender_id": "MYCOMPANY",
  "sample_content": "Hello from MyCompany! This is a test message.",
  "business_justification": "We need this sender ID for our customer communications.",
  "status": "approved",
  "reviewed_by": "uuid",
  "reviewed_at": "2024-01-01T00:05:00Z",
  "rejection_reason": "",
  "sms_package": "uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:05:00Z",
  "user_email": "user@example.com",
  "tenant_name": "John Doe's Organization",
  "reviewed_by_email": "admin@example.com",
  "sms_package_name": "Lite Package"
}
```

#### Update Sender ID Request
```http
PUT /api/messaging/sender-id-requests/{request_id}/
PATCH /api/messaging/sender-id-requests/{request_id}/
```

**Request Body:**
```json
{
  "request_type": "custom",
  "requested_sender_id": "MYCOMPANY",
  "sample_content": "Updated sample message content.",
  "business_justification": "Updated business justification.",
  "sms_package": "uuid"
}
```

#### Delete Sender ID Request
```http
DELETE /api/messaging/sender-id-requests/{request_id}/
```

**Response:**
```json
{
  "message": "Sender ID request deleted successfully"
}
```

### 2. Sender ID Request Review (Admin Only)

#### Review Sender ID Request
```http
PUT /api/messaging/sender-id-requests/{request_id}/review/
PATCH /api/messaging/sender-id-requests/{request_id}/review/
```

**Request Body (Approve):**
```json
{
  "status": "approved"
}
```

**Request Body (Reject):**
```json
{
  "status": "rejected",
  "rejection_reason": "Sender ID already exists or violates naming guidelines"
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "approved",
  "reviewed_by": "uuid",
  "reviewed_at": "2024-01-01T00:05:00Z",
  "rejection_reason": ""
}
```

### 3. Default Sender ID Request

#### Request Default Sender ID
```http
POST /api/messaging/sender-id-requests/default/
```

**Response:**
```json
{
  "message": "Default sender ID request approved and created successfully",
  "sender_id_request": {
    "id": "uuid",
    "request_type": "default",
    "requested_sender_id": "Taarifa-SMS",
    "sample_content": "A test use case for the sender name purposely used for information transfer.",
    "business_justification": "Requesting to use the default sender ID for SMS messaging.",
    "status": "approved",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 4. Available Sender IDs

#### Get Available Sender IDs
```http
GET /api/messaging/sender-id-requests/available/
```

**Response:**
```json
{
  "available_sender_ids": [
    {
      "id": "uuid",
      "requested_sender_id": "Taarifa-SMS",
      "sample_content": "A test use case for the sender name purposely used for information transfer."
    },
    {
      "id": "uuid",
      "requested_sender_id": "MYCOMPANY",
      "sample_content": "Hello from MyCompany! This is a test message."
    }
  ]
}
```

### 5. Sender ID Request Status

#### Get Sender ID Request Status
```http
GET /api/messaging/sender-id-requests/status/
```

**Response:**
```json
{
  "sms_balance": {
    "credits": 5000,
    "total_purchased": 10000,
    "can_request_sender_id": true
  },
  "sender_id_requests": [
    {
      "id": "uuid",
      "request_type": "default",
      "requested_sender_id": "Taarifa-SMS",
      "status": "approved",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "request_type": "custom",
      "requested_sender_id": "MYCOMPANY",
      "status": "pending",
      "created_at": "2024-01-01T00:01:00Z"
    }
  ]
}
```

### 6. Sender ID Usage Management

#### Get Sender ID Usage
```http
GET /api/messaging/sender-id-usage/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "sender_id_request": "uuid",
      "sms_package": "uuid",
      "is_active": true,
      "attached_at": "2024-01-01T00:00:00Z",
      "detached_at": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "sender_id": "MYCOMPANY",
      "sms_package_name": "Lite Package"
    }
  ]
}
```

#### Attach Sender ID to SMS Package
```http
POST /api/messaging/sender-id-usage/
```

**Request Body:**
```json
{
  "sender_id_request": "uuid",
  "sms_package": "uuid"
}
```

**Response:**
```json
{
  "id": "uuid",
  "sender_id_request": "uuid",
  "sms_package": "uuid",
  "is_active": true,
  "attached_at": "2024-01-01T00:00:00Z",
  "detached_at": null,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "sender_id": "MYCOMPANY",
  "sms_package_name": "Lite Package"
}
```

#### Detach Sender ID from SMS Package
```http
POST /api/messaging/sender-id-usage/{usage_id}/detach/
```

**Response:**
```json
{
  "message": "Sender ID detached from SMS package successfully"
}
```

## 🔧 Data Models

### Sender ID Request
```json
{
  "id": "uuid",
  "tenant": "uuid",
  "user": "uuid",
  "request_type": "default|custom",
  "requested_sender_id": "string (max 11 chars)",
  "sample_content": "string (max 170 chars)",
  "business_justification": "string",
  "status": "pending|approved|rejected|cancelled",
  "reviewed_by": "uuid|null",
  "reviewed_at": "datetime|null",
  "rejection_reason": "string",
  "sms_package": "uuid|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Sender ID Usage
```json
{
  "id": "uuid",
  "sender_id_request": "uuid",
  "sms_package": "uuid",
  "is_active": "boolean",
  "attached_at": "datetime",
  "detached_at": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 📝 Validation Rules

### Sender ID Validation
- **Length**: Maximum 11 characters
- **Characters**: Only letters, numbers, spaces, and hyphens
- **Case**: Automatically converted to uppercase
- **Uniqueness**: Must be unique within tenant

### Sample Content Validation
- **Length**: Maximum 170 characters
- **Required**: Must be provided for all requests
- **Purpose**: Used to demonstrate proper usage of the sender ID

### Business Justification
- **Required**: Must be provided for custom sender ID requests
- **Purpose**: Explains why the sender ID is needed
- **Length**: No specific limit, but should be descriptive

## 🔄 Workflow

### 1. Default Sender ID Request
1. User calls `/api/messaging/sender-id-requests/default/`
2. System automatically approves and creates the request
3. Sender ID "Taarifa-SMS" becomes available immediately

### 2. Custom Sender ID Request
1. User calls `POST /api/messaging/sender-id-requests/` with custom details
2. Request is created with status "pending"
3. Admin reviews the request via `/api/messaging/sender-id-requests/{id}/review/`
4. If approved, sender ID becomes available for use
5. If rejected, user can create a new request with modifications

### 3. Sender ID Usage
1. User attaches approved sender ID to SMS package via `/api/messaging/sender-id-usage/`
2. Sender ID can be used for sending SMS messages
3. User can detach sender ID from package when no longer needed

## 🔧 Error Handling

### Error Response Format
```json
{
  "field_name": ["Error message"],
  "non_field_errors": ["General error message"]
}
```

### Common Validation Errors
- `"Sender ID is required"` - Sender ID field is empty
- `"Sender ID cannot exceed 11 characters"` - Sender ID too long
- `"Sender ID can only contain letters, numbers, spaces, and hyphens"` - Invalid characters
- `"A request for this sender ID already exists"` - Duplicate sender ID request
- `"Sample content is required"` - Sample content field is empty
- `"Sample content cannot exceed 170 characters"` - Sample content too long
- `"Sender ID request must be approved before it can be used"` - Trying to use unapproved sender ID
- `"This sender ID is already attached to this SMS package"` - Duplicate usage

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
- 100 requests per hour per user for sender ID requests
- 50 requests per hour per user for usage management
- Burst allowance: 10 requests per second

## 📝 Notes

1. **Default Sender ID**: "Taarifa-SMS" is automatically approved for all users
2. **Custom Sender IDs**: Require admin approval before use
3. **SMS Package Association**: Optional but recommended for better tracking
4. **Tenant Isolation**: All sender IDs are isolated by tenant
5. **Auto-Approval**: Admin users can have their custom sender IDs auto-approved
6. **Usage Tracking**: System tracks which sender IDs are attached to which SMS packages
7. **Character Limits**: Sender IDs follow SMS provider requirements (max 11 chars)
8. **Sample Content**: Used for compliance and demonstration purposes

## 🔗 Integration with SMS Sending

Once a sender ID is approved and attached to an SMS package, it can be used in SMS sending:

```json
{
  "message": "Hello from MyCompany!",
  "recipients": ["255712345678"],
  "sender_id": "MYCOMPANY"
}
```

The system will validate that:
- The sender ID is approved for the tenant
- The sender ID is attached to an active SMS package
- The user has sufficient SMS credits
