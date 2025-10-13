# Sender Name Requests API Integration Guide

## 🚀 Complete API Response Examples for Frontend Integration

This guide provides all the API responses you need to integrate the sender name requests functionality into your existing web page.

---

## 📋 **API Endpoints Overview**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/messaging/sender-requests/submit/` | Submit new request | ✅ |
| GET | `/api/messaging/sender-requests/` | List user requests | ✅ |
| GET | `/api/messaging/sender-requests/stats/` | Get statistics | ✅ |
| GET | `/api/messaging/sender-requests/{id}/` | Get request details | ✅ |
| PUT | `/api/messaging/sender-requests/{id}/update/` | Update request | ✅ |
| DELETE | `/api/messaging/sender-requests/{id}/delete/` | Delete request | ✅ |
| GET | `/api/messaging/sender-requests/admin/dashboard/` | Admin dashboard | ✅ (Admin only) |

---

## 🔐 **Authentication**

### Login Request
```javascript
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Login Response
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "is_active": true
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Token Usage
```javascript
// Include in all API requests
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

---

## 📝 **1. Submit Sender Name Request**

### Request
```javascript
POST /api/messaging/sender-requests/submit/
Content-Type: multipart/form-data
Authorization: Bearer {token}

FormData:
- sender_name: "MYCOMPANY"
- use_case: "This sender name will be used for customer notifications and marketing messages"
- supporting_documents: [file1.pdf, file2.jpg] // Optional files
```

### Success Response (201)
```json
{
  "success": true,
  "message": "Sender name request submitted successfully",
  "data": {
    "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
    "sender_name": "MYCOMPANY",
    "use_case": "This sender name will be used for customer notifications and marketing messages",
    "status": "pending",
    "supporting_documents": [
      "/media/sender_requests/supporting_docs/file1.pdf",
      "/media/sender_requests/supporting_docs/file2.jpg"
    ],
    "created_at": "2025-10-13T16:54:11.130456Z",
    "updated_at": "2025-10-13T16:54:11.130456Z",
    "created_by": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "tenant": {
      "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
      "name": "My Company"
    }
  }
}
```

### Error Response (400)
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

---

## 📋 **2. List User Requests**

### Request
```javascript
GET /api/messaging/sender-requests/?page=1&page_size=10&status=pending&search=MYCOMPANY
Authorization: Bearer {token}
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications",
        "status": "pending",
        "supporting_documents": [
          "/media/sender_requests/supporting_docs/file1.pdf"
        ],
        "supporting_documents_count": 1,
        "created_at": "2025-10-13T16:54:11.130456Z",
        "updated_at": "2025-10-13T16:54:11.130456Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "reviewed_by": null,
        "reviewed_at": null,
        "admin_notes": ""
      },
      {
        "id": "651af02d-68c7-4318-a63e-178eee5e4efb",
        "sender_name": "ADMINCORP",
        "use_case": "This is an admin test sender name request",
        "status": "approved",
        "supporting_documents": [],
        "supporting_documents_count": 0,
        "created_at": "2025-10-13T16:54:11.156464Z",
        "updated_at": "2025-10-13T16:54:11.156464Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "reviewed_by": {
          "id": 2,
          "email": "admin@example.com",
          "first_name": "Admin",
          "last_name": "User"
        },
        "reviewed_at": "2025-10-13T17:00:00.000000Z",
        "admin_notes": "Approved after review of documentation"
      }
    ],
    "count": 2,
    "page": 1,
    "page_size": 10,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

## 📊 **3. Get Statistics**

### Request
```javascript
GET /api/messaging/sender-requests/stats/
Authorization: Bearer {token}
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "total_requests": 3,
    "pending_requests": 1,
    "approved_requests": 1,
    "rejected_requests": 1,
    "requires_changes_requests": 0,
    "recent_activity": {
      "last_7_days": 2,
      "last_30_days": 3
    },
    "status_breakdown": [
      {"status": "pending", "count": 1},
      {"status": "approved", "count": 1},
      {"status": "rejected", "count": 1}
    ]
  }
}
```

---

## 🔍 **4. Get Request Details**

### Request
```javascript
GET /api/messaging/sender-requests/a7022b8b-f099-4371-ba0b-eebdd38354f4/
Authorization: Bearer {token}
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
    "sender_name": "MYCOMPANY",
    "use_case": "This sender name will be used for customer notifications and marketing messages",
    "status": "pending",
    "supporting_documents": [
      "/media/sender_requests/supporting_docs/file1.pdf",
      "/media/sender_requests/supporting_docs/file2.jpg"
    ],
    "supporting_documents_count": 2,
    "created_at": "2025-10-13T16:54:11.130456Z",
    "updated_at": "2025-10-13T16:54:11.130456Z",
    "created_by": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "reviewed_by": null,
    "reviewed_at": null,
    "admin_notes": "",
    "provider_request_id": "",
    "provider_response": {},
    "tenant": {
      "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
      "name": "My Company"
    }
  }
}
```

---

## ✏️ **5. Update Request**

### Request
```javascript
PUT /api/messaging/sender-requests/a7022b8b-f099-4371-ba0b-eebdd38354f4/update/
Content-Type: application/json
Authorization: Bearer {token}

{
  "sender_name": "MYCOMPANY",
  "use_case": "Updated use case description with more details about our business needs"
}
```

### Success Response (200)
```json
{
  "success": true,
  "message": "Request updated successfully",
  "data": {
    "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
    "sender_name": "MYCOMPANY",
    "use_case": "Updated use case description with more details about our business needs",
    "status": "pending",
    "updated_at": "2025-10-13T18:00:00.000000Z"
  }
}
```

---

## 🗑️ **6. Delete Request**

### Request
```javascript
DELETE /api/messaging/sender-requests/a7022b8b-f099-4371-ba0b-eebdd38354f4/delete/
Authorization: Bearer {token}
```

### Success Response (200)
```json
{
  "success": true,
  "message": "Request deleted successfully"
}
```

---

## 🔒 **7. Admin Dashboard**

### Request
```javascript
GET /api/messaging/sender-requests/admin/dashboard/
Authorization: Bearer {token} // Admin token required
```

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "stats": {
      "total_requests": 3,
      "pending_requests": 1,
      "approved_requests": 1,
      "rejected_requests": 1,
      "requires_changes_requests": 0
    },
    "recent_requests": [
      {
        "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications",
        "status": "pending",
        "created_at": "2025-10-13T16:54:11.130456Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        }
      }
    ],
    "pending_requests": [
      {
        "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications",
        "status": "pending",
        "created_at": "2025-10-13T16:54:11.130456Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        }
      }
    ],
    "tenant_name": "My Company",
    "admin_user": "admin@example.com"
  }
}
```

---

## ❌ **Error Responses**

### 400 Bad Request
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication required",
  "detail": "Given token not valid for any token type"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "Permission denied",
  "detail": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Not found",
  "detail": "The requested resource was not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "detail": "An unexpected error occurred"
}
```

---

## 🛠️ **Frontend Integration Examples**

### JavaScript Fetch Examples

#### Submit Request with File Upload
```javascript
async function submitSenderRequest(formData) {
  try {
    const response = await fetch('/api/messaging/sender-requests/submit/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      },
      body: formData // FormData object with files
    });

    const data = await response.json();

    if (response.ok) {
      console.log('Request submitted:', data.data);
      return data;
    } else {
      console.error('Error:', data.message);
      return data;
    }
  } catch (error) {
    console.error('Network error:', error);
    return { success: false, message: 'Network error' };
  }
}
```

#### Get User Requests
```javascript
async function getUserRequests(page = 1, status = null) {
  try {
    let url = `/api/messaging/sender-requests/?page=${page}`;
    if (status) url += `&status=${status}`;

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching requests:', error);
    return { success: false, message: 'Network error' };
  }
}
```

#### Get Statistics
```javascript
async function getStatistics() {
  try {
    const response = await fetch('/api/messaging/sender-requests/stats/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    return { success: false, message: 'Network error' };
  }
}
```

---

## 📱 **Status Values**

| Status | Description | Color Suggestion |
|--------|-------------|------------------|
| `pending` | Awaiting admin review | Orange/Yellow |
| `approved` | Approved by admin | Green |
| `rejected` | Rejected by admin | Red |
| `requires_changes` | Needs user changes | Blue |

---

## 🔧 **File Upload Requirements**

- **Supported formats**: PDF, JPEG, PNG
- **Maximum file size**: 5MB per file
- **Maximum files**: 5 files per request
- **Field name**: `supporting_documents`

---

## 🎯 **Quick Integration Checklist**

- [ ] Add authentication headers to all requests
- [ ] Handle file uploads with FormData
- [ ] Implement error handling for all status codes
- [ ] Add loading states for async operations
- [ ] Validate form inputs before submission
- [ ] Display status badges with appropriate colors
- [ ] Implement pagination for request lists
- [ ] Add admin-only sections for dashboard access

---

This guide provides everything you need to integrate the sender name requests functionality into your existing web page! 🚀
