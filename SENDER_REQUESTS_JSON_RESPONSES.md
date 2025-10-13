# Sender Name Requests - Complete JSON API Responses

## 🔐 Authentication Responses

### Login Success (200)
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
    "is_active": true,
    "date_joined": "2025-10-13T10:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3Mjg4MjQwMDB9.example_access_token",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3Mjg4ODQwMDB9.example_refresh_token"
  }
}
```

### Login Error (400)
```json
{
  "success": false,
  "message": "Invalid credentials",
  "non_field_errors": ["Invalid credentials."]
}
```

### Token Refresh (200)
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.new_access_token_here"
}
```

---

## 📝 Submit Sender Name Request

### Success Response (201)
```json
{
  "success": true,
  "message": "Sender name request submitted successfully",
  "data": {
    "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
    "sender_name": "MYCOMPANY",
    "use_case": "This sender name will be used for customer notifications and marketing messages for our e-commerce platform",
    "status": "pending",
    "supporting_documents": [
      "/media/sender_requests/supporting_docs/2025/10/13/business_license.pdf",
      "/media/sender_requests/supporting_docs/2025/10/13/company_logo.jpg"
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
      "name": "My Company",
      "is_active": true
    }
  }
}
```

### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "sender_name": [
      "Sender name must contain only alphanumeric characters",
      "Sender name cannot exceed 11 characters"
    ],
    "use_case": [
      "Use case description must be at least 10 characters long"
    ],
    "supporting_documents": [
      "File 'document.txt' has unsupported format. Allowed: PDF, JPEG, PNG",
      "File 'large_file.pdf' exceeds 5MB size limit"
    ]
  }
}
```

### File Upload Error (400)
```json
{
  "success": false,
  "message": "File upload failed",
  "errors": {
    "supporting_documents": [
      "Maximum 5 supporting documents allowed",
      "File 'corrupted.pdf' could not be processed"
    ]
  }
}
```

---

## 📋 List User Requests

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications and marketing messages",
        "status": "pending",
        "supporting_documents": [
          "/media/sender_requests/supporting_docs/2025/10/13/business_license.pdf"
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
        "admin_notes": "",
        "provider_request_id": "",
        "provider_response": {},
        "tenant": {
          "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
          "name": "My Company"
        }
      },
      {
        "id": "651af02d-68c7-4318-a63e-178eee5e4efb",
        "sender_name": "ADMINCORP",
        "use_case": "This is an admin test sender name request for our internal communications",
        "status": "approved",
        "supporting_documents": [],
        "supporting_documents_count": 0,
        "created_at": "2025-10-13T16:54:11.156464Z",
        "updated_at": "2025-10-13T17:00:00.000000Z",
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
        "admin_notes": "Approved after review of documentation. Sender name meets all requirements.",
        "provider_request_id": "beem_12345",
        "provider_response": {
          "status": "approved",
          "provider_id": "beem_12345",
          "message": "Sender ID successfully registered"
        },
        "tenant": {
          "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
          "name": "My Company"
        }
      },
      {
        "id": "6f30d159-96d2-4f0f-8bca-81bb8c3c0147",
        "sender_name": "REJECTED123",
        "use_case": "This is a rejected test sender name request",
        "status": "rejected",
        "supporting_documents": [
          "/media/sender_requests/supporting_docs/2025/10/13/incomplete_doc.pdf"
        ],
        "supporting_documents_count": 1,
        "created_at": "2025-10-13T16:54:11.179493Z",
        "updated_at": "2025-10-13T17:30:00.000000Z",
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
        "reviewed_at": "2025-10-13T17:30:00.000000Z",
        "admin_notes": "Rejected due to insufficient documentation. Please provide complete business registration documents.",
        "provider_request_id": "",
        "provider_response": {},
        "tenant": {
          "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
          "name": "My Company"
        }
      }
    ],
    "count": 3,
    "page": 1,
    "page_size": 10,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

### Empty Results (200)
```json
{
  "success": true,
  "data": {
    "results": [],
    "count": 0,
    "page": 1,
    "page_size": 10,
    "total_pages": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

---

## 📊 Statistics Response

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
      "last_30_days": 3,
      "last_90_days": 3
    },
    "status_breakdown": [
      {
        "status": "pending",
        "count": 1
      },
      {
        "status": "approved",
        "count": 1
      },
      {
        "status": "rejected",
        "count": 1
      },
      {
        "status": "requires_changes",
        "count": 0
      }
    ],
    "user_breakdown": [
      {
        "created_by__email": "user@example.com",
        "created_by__first_name": "John",
        "created_by__last_name": "Doe",
        "count": 3
      }
    ],
    "monthly_trends": {
      "2025-10": 3,
      "2025-09": 0,
      "2025-08": 0
    }
  }
}
```

---

## 🔍 Get Request Details

### Success Response (200)
```json
{
  "success": true,
  "data": {
    "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
    "sender_name": "MYCOMPANY",
    "use_case": "This sender name will be used for customer notifications and marketing messages for our e-commerce platform. We need this to send order confirmations, shipping updates, and promotional messages to our customers.",
    "status": "pending",
    "supporting_documents": [
      "/media/sender_requests/supporting_docs/2025/10/13/business_license.pdf",
      "/media/sender_requests/supporting_docs/2025/10/13/company_logo.jpg",
      "/media/sender_requests/supporting_docs/2025/10/13/tax_certificate.pdf"
    ],
    "supporting_documents_count": 3,
    "created_at": "2025-10-13T16:54:11.130456Z",
    "updated_at": "2025-10-13T16:54:11.130456Z",
    "created_by": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_staff": false
    },
    "reviewed_by": null,
    "reviewed_at": null,
    "admin_notes": "",
    "provider_request_id": "",
    "provider_response": {},
    "tenant": {
      "id": "3e8786e9-cc32-476e-bcfc-dbdc0fc144a5",
      "name": "My Company",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  }
}
```

### Not Found (404)
```json
{
  "success": false,
  "message": "Request not found",
  "detail": "The requested sender name request was not found"
}
```

---

## ✏️ Update Request

### Success Response (200)
```json
{
  "success": true,
  "message": "Request updated successfully",
  "data": {
    "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
    "sender_name": "MYCOMPANY",
    "use_case": "Updated use case description with more comprehensive details about our business needs and SMS communication requirements",
    "status": "pending",
    "updated_at": "2025-10-13T18:00:00.000000Z",
    "created_at": "2025-10-13T16:54:11.130456Z"
  }
}
```

### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "sender_name": [
      "Sender name cannot be changed after submission"
    ],
    "use_case": [
      "Use case description must be at least 10 characters long"
    ]
  }
}
```

### Not Found (404)
```json
{
  "success": false,
  "message": "Request not found",
  "detail": "The requested sender name request was not found"
}
```

---

## 🗑️ Delete Request

### Success Response (200)
```json
{
  "success": true,
  "message": "Request deleted successfully"
}
```

### Not Found (404)
```json
{
  "success": false,
  "message": "Request not found",
  "detail": "The requested sender name request was not found"
}
```

### Permission Denied (403)
```json
{
  "success": false,
  "message": "Permission denied",
  "detail": "You can only delete your own pending requests"
}
```

---

## 🔒 Admin Dashboard

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
        "use_case": "This sender name will be used for customer notifications and marketing messages",
        "status": "pending",
        "created_at": "2025-10-13T16:54:11.130456Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "supporting_documents_count": 2
      },
      {
        "id": "651af02d-68c7-4318-a63e-178eee5e4efb",
        "sender_name": "ADMINCORP",
        "use_case": "This is an admin test sender name request for our internal communications",
        "status": "approved",
        "created_at": "2025-10-13T16:54:11.156464Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "supporting_documents_count": 0
      },
      {
        "id": "6f30d159-96d2-4f0f-8bca-81bb8c3c0147",
        "sender_name": "REJECTED123",
        "use_case": "This is a rejected test sender name request",
        "status": "rejected",
        "created_at": "2025-10-13T16:54:11.179493Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "supporting_documents_count": 1
      }
    ],
    "pending_requests": [
      {
        "id": "a7022b8b-f099-4371-ba0b-eebdd38354f4",
        "sender_name": "MYCOMPANY",
        "use_case": "This sender name will be used for customer notifications and marketing messages",
        "status": "pending",
        "created_at": "2025-10-13T16:54:11.130456Z",
        "created_by": {
          "id": 1,
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe"
        },
        "supporting_documents_count": 2
      }
    ],
    "status_breakdown": [
      {
        "status": "pending",
        "count": 1
      },
      {
        "status": "approved",
        "count": 1
      },
      {
        "status": "rejected",
        "count": 1
      }
    ],
    "user_breakdown": [
      {
        "created_by__email": "user@example.com",
        "created_by__first_name": "John",
        "created_by__last_name": "Doe",
        "count": 3
      }
    ],
    "recent_activity": 2,
    "tenant_name": "My Company",
    "admin_user": "admin@example.com"
  }
}
```

### Admin Access Denied (403)
```json
{
  "success": false,
  "message": "Admin access required",
  "detail": "You must be an admin to access this endpoint"
}
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Bad request",
  "detail": "Invalid request data provided"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication required",
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
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

### 413 Payload Too Large
```json
{
  "success": false,
  "message": "File too large",
  "detail": "The uploaded file exceeds the maximum allowed size of 5MB"
}
```

### 415 Unsupported Media Type
```json
{
  "success": false,
  "message": "Unsupported file type",
  "detail": "Only PDF, JPEG, and PNG files are allowed"
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "detail": "Too many requests. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Internal server error",
  "detail": "An unexpected error occurred. Please try again later."
}
```

---

## 🔄 Status Values Reference

| Status | Description | Color Code | Next Actions |
|--------|-------------|------------|--------------|
| `pending` | Awaiting admin review | Orange (#f59e0b) | Edit, Delete |
| `approved` | Approved by admin | Green (#10b981) | View only |
| `rejected` | Rejected by admin | Red (#ef4444) | Resubmit |
| `requires_changes` | Needs user changes | Blue (#3b82f6) | Edit, Resubmit |

---

## 📁 File Upload Response Examples

### Successful File Upload
```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "data": {
    "uploaded_files": [
      {
        "filename": "business_license.pdf",
        "size": 2048576,
        "url": "/media/sender_requests/supporting_docs/2025/10/13/business_license.pdf",
        "content_type": "application/pdf"
      },
      {
        "filename": "company_logo.jpg",
        "size": 1024000,
        "url": "/media/sender_requests/supporting_docs/2025/10/13/company_logo.jpg",
        "content_type": "image/jpeg"
      }
    ],
    "total_size": 3072576,
    "file_count": 2
  }
}
```

### File Upload Error
```json
{
  "success": false,
  "message": "File upload failed",
  "errors": {
    "files": [
      "File 'document.txt' is not a supported format",
      "File 'large_file.pdf' exceeds 5MB size limit",
      "Maximum 5 files allowed per request"
    ]
  }
}
```

---

## 🎯 Quick Reference

### Common Response Structure
```json
{
  "success": boolean,
  "message": "string",
  "data": object | null,
  "errors": object | null
}
```

### Pagination Structure
```json
{
  "results": array,
  "count": number,
  "page": number,
  "page_size": number,
  "total_pages": number,
  "has_next": boolean,
  "has_previous": boolean
}
```

### User Object Structure
```json
{
  "id": number,
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "is_staff": boolean,
  "is_active": boolean
}
```

### Tenant Object Structure
```json
{
  "id": "uuid",
  "name": "string",
  "is_active": boolean,
  "created_at": "datetime"
}
```

This comprehensive JSON response reference covers all possible API responses for the sender name requests functionality! 🚀
