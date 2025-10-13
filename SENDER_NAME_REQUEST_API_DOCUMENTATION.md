# 📱 Sender Name Request API Documentation

## 🎯 Overview

The Sender Name Request API allows users to submit requests for new SMS sender IDs through a comprehensive form system. This includes file uploads for supporting documents, validation, and admin management capabilities.

## 🔗 Base URL

```
http://localhost:8000/api/messaging/sender-requests/
```

## 🔐 Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer your-jwt-token
```

## 📋 API Endpoints

### 1. Submit Sender Name Request

Submit a new sender name request with optional file uploads.

**Endpoint:** `POST /api/messaging/sender-requests/submit/`

**Content-Type:** `multipart/form-data`

**Request Body:**
```
sender_name: "MYCOMPANY" (required, max 11 alphanumeric characters)
use_case: "We will use this sender name for customer notifications..." (required, 10-1000 characters)
supporting_documents: [file1, file2, ...] (optional, max 5 files, PDF/JPEG/PNG, max 5MB each)
```

**Validation Rules:**
- `sender_name`: Must be alphanumeric only, max 11 characters
- `use_case`: Must be 10-1000 characters describing intended use
- `supporting_documents`: Optional files (PDF, JPEG, PNG), max 5MB each, max 5 files total

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Sender name request submitted successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sender_name": "MYCOMPANY",
        "use_case": "We will use this sender name for customer notifications...",
        "supporting_documents": [
            "sender_requests/550e8400-e29b-41d4-a716-446655440001.pdf"
        ],
        "supporting_documents_count": 1,
        "status": "pending",
        "admin_notes": "",
        "reviewed_by": null,
        "reviewed_by_name": "",
        "reviewed_at": null,
        "provider_request_id": "",
        "provider_response": {},
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z",
        "created_by": "550e8400-e29b-41d4-a716-446655440002",
        "created_by_name": "John Doe"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "sender_name": ["Sender name must contain only alphanumeric characters"],
        "use_case": ["Use case description must be at least 10 characters long"]
    }
}
```

### 2. List Sender Name Requests

Get a paginated list of sender name requests for the current tenant.

**Endpoint:** `GET /api/messaging/sender-requests/`

**Query Parameters:**
- `status` (optional): Filter by status (`pending`, `approved`, `rejected`, `requires_changes`)
- `search` (optional): Search in sender_name and use_case fields
- `page` (optional): Page number for pagination (default: 1)
- `page_size` (optional): Number of items per page (default: 20, max: 100)

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "results": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "sender_name": "MYCOMPANY",
                "use_case": "We will use this sender name for customer notifications...",
                "supporting_documents": [
                    "sender_requests/550e8400-e29b-41d4-a716-446655440001.pdf"
                ],
                "supporting_documents_count": 1,
                "status": "pending",
                "admin_notes": "",
                "reviewed_by": null,
                "reviewed_by_name": "",
                "reviewed_at": null,
                "provider_request_id": "",
                "provider_response": {},
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z",
                "created_by": "550e8400-e29b-41d4-a716-446655440002",
                "created_by_name": "John Doe"
            }
        ],
        "count": 10,
        "next": "http://localhost:8000/api/messaging/sender-requests/?page=2",
        "previous": null
    }
}
```

### 3. Get Sender Name Request Details

Get details of a specific sender name request.

**Endpoint:** `GET /api/messaging/sender-requests/{request_id}/`

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sender_name": "MYCOMPANY",
        "use_case": "We will use this sender name for customer notifications...",
        "supporting_documents": [
            "sender_requests/550e8400-e29b-41d4-a716-446655440001.pdf"
        ],
        "supporting_documents_count": 1,
        "status": "pending",
        "admin_notes": "",
        "reviewed_by": null,
        "reviewed_by_name": "",
        "reviewed_at": null,
        "provider_request_id": "",
        "provider_response": {},
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z",
        "created_by": "550e8400-e29b-41d4-a716-446655440002",
        "created_by_name": "John Doe"
    }
}
```

**Error Response (404 Not Found):**
```json
{
    "success": false,
    "message": "Sender name request not found"
}
```

### 4. Update Sender Name Request (Admin Only)

Update the status and admin notes of a sender name request.

**Endpoint:** `PUT /api/messaging/sender-requests/{request_id}/update/`

**Permission:** Admin only

**Request Body:**
```json
{
    "status": "approved",
    "admin_notes": "Request approved after review of supporting documents"
}
```

**Status Options:**
- `pending`: Pending Review
- `approved`: Approved
- `rejected`: Rejected
- `requires_changes`: Requires Changes

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Request updated successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sender_name": "MYCOMPANY",
        "use_case": "We will use this sender name for customer notifications...",
        "supporting_documents": [
            "sender_requests/550e8400-e29b-41d4-a716-446655440001.pdf"
        ],
        "supporting_documents_count": 1,
        "status": "approved",
        "admin_notes": "Request approved after review of supporting documents",
        "reviewed_by": "550e8400-e29b-41d4-a716-446655440003",
        "reviewed_by_name": "Admin User",
        "reviewed_at": "2024-01-01T11:00:00Z",
        "provider_request_id": "",
        "provider_response": {},
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T11:00:00Z",
        "created_by": "550e8400-e29b-41d4-a716-446655440002",
        "created_by_name": "John Doe"
    }
}
```

### 5. Delete Sender Name Request

Delete a sender name request and its associated files.

**Endpoint:** `DELETE /api/messaging/sender-requests/{request_id}/`

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Request deleted successfully"
}
```

### 6. Get Sender Name Request Statistics

Get statistics about sender name requests for the current tenant.

**Endpoint:** `GET /api/messaging/sender-requests/stats/`

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "total_requests": 10,
        "pending_requests": 5,
        "approved_requests": 3,
        "rejected_requests": 2,
        "requires_changes_requests": 0,
        "my_requests": 8,
        "my_pending_requests": 4
    }
}
```

## 🔧 Frontend Integration

### Form Submission Example (JavaScript)

```javascript
const submitSenderNameRequest = async (formData) => {
    const response = await fetch('/api/messaging/sender-requests/submit/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData // FormData object with files
    });

    const result = await response.json();

    if (result.success) {
        console.log('Request submitted:', result.data);
        // Handle success
    } else {
        console.error('Error:', result.message);
        // Handle validation errors
    }
};

// Example usage
const formData = new FormData();
formData.append('sender_name', 'MYCOMPANY');
formData.append('use_case', 'We will use this sender name for customer notifications...');
formData.append('supporting_documents', fileInput.files[0]); // Optional file

submitSenderNameRequest(formData);
```

### Form Validation (Frontend)

```javascript
const validateSenderName = (senderName) => {
    if (!senderName) {
        return 'Sender name is required';
    }
    if (senderName.length > 11) {
        return 'Sender name cannot exceed 11 characters';
    }
    if (!/^[a-zA-Z0-9]+$/.test(senderName)) {
        return 'Sender name must contain only alphanumeric characters';
    }
    return null;
};

const validateUseCase = (useCase) => {
    if (!useCase || useCase.trim().length < 10) {
        return 'Use case description must be at least 10 characters long';
    }
    if (useCase.length > 1000) {
        return 'Use case description cannot exceed 1000 characters';
    }
    return null;
};

const validateFiles = (files) => {
    if (files.length > 5) {
        return 'Maximum 5 supporting documents allowed';
    }

    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    const maxSize = 5 * 1024 * 1024; // 5MB

    for (let file of files) {
        if (!allowedTypes.includes(file.type)) {
            return `File ${file.name} has unsupported format. Allowed: PDF, JPEG, PNG`;
        }
        if (file.size > maxSize) {
            return `File ${file.name} exceeds 5MB size limit`;
        }
    }

    return null;
};
```

## 📊 Status Workflow

1. **Pending Review** - Initial status when request is submitted
2. **Approved** - Request approved by admin, sender name can be used
3. **Rejected** - Request rejected by admin
4. **Requires Changes** - Request needs modifications before approval

## 🔒 Permissions

- **Users**: Can create, view, and delete their own requests
- **Admins**: Can view, update, and delete all requests in their tenant
- **Tenant Isolation**: Users can only access requests within their tenant

## 📁 File Storage

- Supporting documents are stored in `sender_requests/` directory
- Files are automatically deleted when request is deleted
- Unique filenames prevent conflicts
- Files are accessible via Django's file storage system

## 🚀 Getting Started

1. **Authentication**: Ensure you have a valid JWT token
2. **Form Setup**: Create a form with sender_name, use_case, and file upload fields
3. **Validation**: Implement client-side validation as shown above
4. **Submission**: Use FormData to submit the request with files
5. **Status Tracking**: Poll the list endpoint to check request status

## 🔍 Error Handling

All endpoints return consistent error responses with:
- `success`: Boolean indicating if the operation was successful
- `message`: Human-readable error message
- `errors`: Object containing field-specific validation errors (when applicable)

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error
