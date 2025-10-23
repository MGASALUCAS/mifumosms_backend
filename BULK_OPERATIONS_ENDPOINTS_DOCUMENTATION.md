# Bulk Operations Endpoints Documentation

## Overview

This document provides comprehensive documentation for all bulk operation endpoints in the Mifumo SMS system. These endpoints allow you to perform operations on multiple contacts, send bulk SMS messages, and manage data efficiently.

## Table of Contents

1. [Contact Bulk Operations](#contact-bulk-operations)
2. [SMS Bulk Operations](#sms-bulk-operations)
3. [Bulk Import Operations](#bulk-import-operations)
4. [Rate Limits & Constraints](#rate-limits--constraints)
5. [Error Handling](#error-handling)
6. [Frontend Integration](#frontend-integration)
7. [Testing](#testing)

---

## Contact Bulk Operations

### 1. Bulk Edit Contacts

**Endpoint:** `POST /api/messaging/contacts/bulk-edit/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `application/json`

**Description:** Update multiple contacts at once with the same changes.

**Request Body:**
```json
{
  "contact_ids": ["uuid1", "uuid2", "uuid3"],
  "updates": {
    "name": "Updated Name",
    "email": "updated@example.com",
    "tags": ["tag1", "tag2"],
    "attributes": {
      "company": "New Company",
      "department": "Sales"
    },
    "is_active": true
  }
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contact_ids` | array | Yes | List of contact UUIDs (max 100) |
| `updates` | object | Yes | Fields to update |

**Allowed Update Fields:**
- `name` - Contact name
- `email` - Contact email
- `tags` - Array of tags
- `attributes` - Custom attributes object
- `is_active` - Boolean status

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully updated 3 contacts",
  "updated_count": 3,
  "total_requested": 3,
  "errors": []
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Some contacts not found: ['uuid1']",
  "updated_count": 0,
  "total_requested": 3,
  "errors": ["Contact with ID uuid1 not found"]
}
```

### 2. Bulk Delete Contacts

**Endpoint:** `POST /api/messaging/contacts/bulk-delete/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `application/json`

**Description:** Delete multiple contacts at once.

**Request Body:**
```json
{
  "contact_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contact_ids` | array | Yes | List of contact UUIDs (max 100) |

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully deleted 3 contacts",
  "deleted_count": 3,
  "total_requested": 3
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "No contacts found with the provided IDs",
  "deleted_count": 0,
  "total_requested": 3
}
```

---

## SMS Bulk Operations

### 1. Bulk Send SMS

**Endpoint:** `POST /api/messaging/sms/bulk-send/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `application/json`

**Description:** Send SMS messages to multiple contacts at once.

**Request Body:**
```json
{
  "contacts": [
    {
      "phone": "+255700000001",
      "name": "John Doe"
    },
    {
      "phone": "+255700000002",
      "name": "Jane Smith"
    }
  ],
  "message": "Hello from Mifumo SMS!",
  "sender_id": "MIFUMO",
  "template_id": "template_uuid",
  "schedule_at": "2025-01-01T10:00:00Z",
  "campaign_id": "campaign_uuid"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contacts` | array | Yes | List of contact objects |
| `message` | string | Yes | SMS message content |
| `sender_id` | string | Yes | Sender ID for SMS |
| `template_id` | string | No | Template to use |
| `schedule_at` | string | No | ISO datetime for scheduling |
| `campaign_id` | string | No | Campaign ID for tracking |

**Contact Object:**
```json
{
  "phone": "+255700000001",
  "name": "John Doe"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "total_contacts": 2,
  "processed_contacts": 2,
  "successful_contacts": 2,
  "results": [
    {
      "phone": "+255700000001",
      "success": true,
      "message_id": "msg_uuid_1"
    },
    {
      "phone": "+255700000002",
      "success": true,
      "message_id": "msg_uuid_2"
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Invalid phone number format",
  "total_contacts": 0,
  "processed_contacts": 0,
  "successful_contacts": 0,
  "results": []
}
```

### 2. Bulk SMS with Excel Upload

**Endpoint:** `POST /api/messaging/sms/bulk-upload/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `multipart/form-data`

**Description:** Send bulk SMS using Excel file upload.

**Request Body (Form Data):**
```
file: <Excel file>
sender_id: MIFUMO
template_id: template_uuid
campaign_id: campaign_uuid
```

**Excel Format Requirements:**
- **Column A:** Phone Number (E.164 format)
- **Column B:** Name (optional)
- **Column C:** Message (optional, uses template if not provided)
- **Column D:** Sender ID (optional, uses default if not provided)
- **Additional columns:** Custom variables for template

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Bulk SMS upload processed successfully",
  "upload_id": "upload_uuid",
  "total_contacts": 100,
  "processed_contacts": 95,
  "successful_contacts": 90,
  "errors": [
    "Row 5: Invalid phone number format",
    "Row 12: Missing required field"
  ]
}
```

---

## Bulk Import Operations

### 1. Bulk Import Contacts

**Endpoint:** `POST /api/messaging/contacts/bulk-import/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `application/json` or `multipart/form-data`

**Description:** Import multiple contacts from CSV, Excel, or phone contacts.

**Request Body (CSV Import):**
```json
{
  "import_type": "csv",
  "csv_data": "name,phone_e164,email,tags\nJohn Doe,+255700000001,john@example.com,vip\nJane Smith,+255700000002,jane@example.com,regular",
  "skip_duplicates": true,
  "update_existing": false
}
```

**Request Body (Excel Import):**
```json
{
  "import_type": "excel",
  "file": "<Excel file upload>",
  "skip_duplicates": true,
  "update_existing": false
}
```

**Request Body (Phone Contacts Import):**
```json
{
  "import_type": "phone_contacts",
  "contacts": [
    {
      "full_name": "John Doe",
      "phone": "+255700000001",
      "email": "john@example.com"
    },
    {
      "full_name": "Jane Smith",
      "phone": "+255700000002",
      "email": "jane@example.com"
    }
  ],
  "skip_duplicates": true,
  "update_existing": false
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "imported": 5,
  "updated": 2,
  "skipped": 1,
  "total_processed": 8,
  "errors": [],
  "message": "Successfully imported 5, updated 2, skipped 1 contacts"
}
```

---

## Rate Limits & Constraints

### Contact Operations
- **Bulk Edit:** Maximum 100 contacts per request
- **Bulk Delete:** Maximum 100 contacts per request
- **Bulk Import:** Maximum 1000 contacts per request
- **Rate Limit:** 10 requests per minute per user

### SMS Operations
- **Bulk Send:** Maximum 10,000 recipients per request
- **Bulk Upload:** Maximum 50,000 recipients per file
- **Rate Limit:** 5 requests per minute per user
- **File Size Limit:** 10MB for Excel uploads

### General Constraints
- **Authentication:** All endpoints require JWT Bearer token
- **Tenant Isolation:** Users can only operate on their tenant's data
- **Phone Validation:** All phone numbers must be in E.164 format
- **Error Handling:** Comprehensive error reporting for failed operations

---

## Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `400` | Bad Request | Check request format and required fields |
| `401` | Unauthorized | Provide valid JWT token |
| `403` | Forbidden | Check user permissions |
| `404` | Not Found | Verify contact IDs exist |
| `429` | Too Many Requests | Wait before retrying |
| `500` | Internal Server Error | Contact support |

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "Specific field error",
    "constraint": "Validation constraint"
  }
}
```

---

## Frontend Integration

### JavaScript Examples

#### Bulk Edit Contacts
```javascript
const bulkEditContacts = async (contactIds, updates) => {
  const response = await fetch('/api/messaging/contacts/bulk-edit/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contact_ids: contactIds,
      updates: updates
    })
  });

  return await response.json();
};

// Usage
const result = await bulkEditContacts(
  ['uuid1', 'uuid2', 'uuid3'],
  {
    tags: ['updated', 'bulk'],
    is_active: true
  }
);
```

#### Bulk Delete Contacts
```javascript
const bulkDeleteContacts = async (contactIds) => {
  const response = await fetch('/api/messaging/contacts/bulk-delete/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contact_ids: contactIds
    })
  });

  return await response.json();
};
```

#### Bulk Send SMS
```javascript
const bulkSendSMS = async (contacts, message, senderId) => {
  const response = await fetch('/api/messaging/sms/bulk-send/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contacts: contacts,
      message: message,
      sender_id: senderId
    })
  });

  return await response.json();
};
```

#### Bulk Import Contacts
```javascript
const bulkImportContacts = async (file, importType) => {
  const formData = new FormData();
  formData.append('import_type', importType);
  formData.append('file', file);
  formData.append('skip_duplicates', 'true');
  formData.append('update_existing', 'false');

  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  return await response.json();
};
```

### React Hook Example
```javascript
import { useState, useCallback } from 'react';

const useBulkOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const bulkEdit = useCallback(async (contactIds, updates) => {
    setLoading(true);
    setError(null);

    try {
      const result = await bulkEditContacts(contactIds, updates);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const bulkDelete = useCallback(async (contactIds) => {
    setLoading(true);
    setError(null);

    try {
      const result = await bulkDeleteContacts(contactIds);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { bulkEdit, bulkDelete, loading, error };
};
```

---

## Testing

### Test Files
- `test_bulk_operations.py` - Comprehensive test suite
- `test_contact_import.py` - Import functionality tests
- `test_enhanced_bulk_import.py` - Enhanced import tests

### Running Tests
```bash
# Run all bulk operation tests
python test_bulk_operations.py

# Run specific test
python -m pytest test_bulk_operations.py::TestBulkOperations::test_bulk_edit_contacts
```

### Test Data Examples
```python
# Test contact IDs
contact_ids = [
    "123e4567-e89b-12d3-a456-426614174000",
    "123e4567-e89b-12d3-a456-426614174001",
    "123e4567-e89b-12d3-a456-426614174002"
]

# Test updates
updates = {
    "tags": ["test", "bulk"],
    "is_active": True,
    "attributes": {
        "test_field": "test_value"
    }
}

# Test contacts for SMS
contacts = [
    {"phone": "+255700000001", "name": "Test User 1"},
    {"phone": "+255700000002", "name": "Test User 2"}
]
```

---

## Best Practices

### 1. Batch Size Optimization
- Use appropriate batch sizes (100 for edits/deletes, 1000 for imports)
- Monitor response times and adjust accordingly
- Consider pagination for large datasets

### 2. Error Handling
- Always check response status codes
- Implement retry logic for transient errors
- Provide user feedback for failed operations

### 3. Performance
- Use async operations for better UX
- Show progress indicators for long operations
- Cache frequently used data

### 4. Security
- Validate all input data
- Implement proper authentication
- Use HTTPS for all API calls

### 5. Monitoring
- Log all bulk operations
- Monitor rate limits
- Track success/failure rates

---

## Troubleshooting

### Common Issues

1. **"Contact IDs not found"**
   - Verify contact IDs exist in your tenant
   - Check for typos in UUIDs
   - Ensure contacts belong to your organization

2. **"Rate limit exceeded"**
   - Wait before retrying
   - Implement exponential backoff
   - Consider reducing batch sizes

3. **"Invalid phone number format"**
   - Use E.164 format (+255XXXXXXXXX)
   - Validate phone numbers before sending
   - Check country code formatting

4. **"File upload failed"**
   - Check file size limits (10MB)
   - Verify file format (.csv, .xlsx, .xls)
   - Ensure proper multipart/form-data encoding

### Debug Mode
Enable debug mode in Django settings for detailed error messages:
```python
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'messaging': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Related Documentation

- [Bulk Import Endpoint Documentation](./BULK_IMPORT_ENDPOINT_DOCUMENTATION.md)
- [SMS API Documentation](./messaging/api_documentation_sms.md)
- [Contact Management API](./CONTACTS_API_ENDPOINTS.md)
- [Frontend Integration Guide](./FRONTEND_INTEGRATION_JSON_SCRIPT.md)
