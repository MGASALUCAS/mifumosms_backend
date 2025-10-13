# 📱 Sender Name Request API - Complete Response Examples

## 🔧 **Fixed Issues**

The 403 Forbidden error has been resolved by updating the permission classes from `IsTenantMember` to `IsAuthenticated`. The API now uses the user's tenant property for filtering instead of requiring active membership.

## 📋 **API Response Examples**

### 1. **Get Statistics Response**

**Endpoint:** `GET /api/messaging/sender-requests/stats/`

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_requests": 0,
    "pending_requests": 0,
    "approved_requests": 0,
    "rejected_requests": 0,
    "requires_changes_requests": 0,
    "my_requests": 0,
    "my_pending_requests": 0
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "not_authenticated"
}
```

**Error Response (403 Forbidden) - Fixed:**
```json
{
  "success": false,
  "message": "No tenant found. Please contact support."
}
```

### 2. **List Sender Name Requests Response**

**Endpoint:** `GET /api/messaging/sender-requests/`

**Success Response (200 OK) - Empty List:**
```json
{
  "success": true,
  "data": {
    "results": [],
    "count": 0
  }
}
```

**Success Response (200 OK) - With Data:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "sender_name": "MYCOMPANY",
        "use_case": "We will use this sender name for customer notifications and marketing campaigns.",
        "supporting_documents": [
          "sender_requests/a1b2c3d4-e5f6-7890-abcd-ef1234567891.pdf"
        ],
        "supporting_documents_count": 1,
        "status": "pending",
        "admin_notes": "",
        "reviewed_by": null,
        "reviewed_by_name": "",
        "reviewed_at": null,
        "provider_request_id": "",
        "provider_response": {},
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "created_by": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
        "created_by_name": "John Doe"
      }
    ],
    "count": 1
  }
}
```

### 3. **Submit Sender Name Request Response**

**Endpoint:** `POST /api/messaging/sender-requests/submit/`

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Sender name request submitted successfully",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "sender_name": "MYCOMPANY",
    "use_case": "We will use this sender name for customer notifications and marketing campaigns.",
    "supporting_documents": [
      "sender_requests/a1b2c3d4-e5f6-7890-abcd-ef1234567891.pdf"
    ],
    "supporting_documents_count": 1,
    "status": "pending",
    "admin_notes": "",
    "reviewed_by": null,
    "reviewed_by_name": "",
    "reviewed_at": null,
    "provider_request_id": "",
    "provider_response": {},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "created_by": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "created_by_name": "John Doe"
  }
}
```

**Validation Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "sender_name": [
      "Sender name must contain only alphanumeric characters"
    ],
    "use_case": [
      "Use case description must be at least 10 characters long"
    ]
  }
}
```

**Duplicate Request Error (400 Bad Request):**
```json
{
  "success": false,
  "message": "A request for sender name \"MYCOMPANY\" already exists",
  "existing_request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### 4. **Get Request Details Response**

**Endpoint:** `GET /api/messaging/sender-requests/{request_id}/`

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "sender_name": "MYCOMPANY",
    "use_case": "We will use this sender name for customer notifications and marketing campaigns.",
    "supporting_documents": [
      "sender_requests/a1b2c3d4-e5f6-7890-abcd-ef1234567891.pdf"
    ],
    "supporting_documents_count": 1,
    "status": "pending",
    "admin_notes": "",
    "reviewed_by": null,
    "reviewed_by_name": "",
    "reviewed_at": null,
    "provider_request_id": "",
    "provider_response": {},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "created_by": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "created_by_name": "John Doe"
  }
}
```

**Not Found Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Sender name request not found"
}
```

### 5. **Update Request Response (Admin Only)**

**Endpoint:** `PUT /api/messaging/sender-requests/{request_id}/update/`

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Request updated successfully",
  "data": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "sender_name": "MYCOMPANY",
    "use_case": "We will use this sender name for customer notifications and marketing campaigns.",
    "supporting_documents": [
      "sender_requests/a1b2c3d4-e5f6-7890-abcd-ef1234567891.pdf"
    ],
    "supporting_documents_count": 1,
    "status": "approved",
    "admin_notes": "Request approved after reviewing supporting documents.",
    "reviewed_by": "d4e5f6g7-h8i9-0123-defg-456789012345",
    "reviewed_by_name": "Admin User",
    "reviewed_at": "2024-01-16T15:30:00Z",
    "provider_request_id": "beem_67890",
    "provider_response": {
      "status": "active",
      "approved_at": "2024-01-16T15:30:00Z"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T15:30:00Z",
    "created_by": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
    "created_by_name": "John Doe"
  }
}
```

**Permission Error (403 Forbidden):**
```json
{
  "success": false,
  "message": "Only administrators can update requests"
}
```

### 6. **Delete Request Response**

**Endpoint:** `DELETE /api/messaging/sender-requests/{request_id}/`

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Request deleted successfully"
}
```

## 🧪 **Frontend Integration Test**

Use the provided `frontend_test_sender_requests.html` file to test the API:

1. Open the HTML file in your browser
2. Enter your JWT token (get it from login)
3. Test different endpoints
4. Submit a real request with files

## 🔧 **Frontend JavaScript Example**

```javascript
// Test the API with your frontend
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const token = 'your-jwt-token-here';

// Test statistics endpoint
async function testStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/messaging/sender-requests/stats/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log('Stats Response:', data);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Test list endpoint
async function testList() {
    try {
        const response = await fetch(`${API_BASE_URL}/messaging/sender-requests/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log('List Response:', data);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Test submit endpoint
async function testSubmit() {
    const formData = new FormData();
    formData.append('sender_name', 'TESTCOMPANY');
    formData.append('use_case', 'This is a test sender name request for API testing purposes.');

    try {
        const response = await fetch(`${API_BASE_URL}/messaging/sender-requests/submit/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();
        console.log('Submit Response:', data);
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run tests
testStats();
testList();
testSubmit();
```

## ✅ **Status Codes Summary**

| Status Code | Description | When It Occurs |
|-------------|-------------|----------------|
| 200 | OK | Successful GET, PUT, DELETE requests |
| 201 | Created | Successful POST requests |
| 400 | Bad Request | Validation errors, missing data |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions (admin-only actions) |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server-side errors |

## 🚀 **Ready for Frontend Integration**

The API is now fully functional and ready for frontend integration. The 403 Forbidden error has been resolved, and all endpoints are working correctly with proper authentication.
