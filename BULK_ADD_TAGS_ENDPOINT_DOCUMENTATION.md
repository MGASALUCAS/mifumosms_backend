# Bulk Add Tags Endpoint Documentation

## 🏷️ **NEW ENDPOINT IMPLEMENTED**

**Endpoint:** `POST /api/messaging/contacts/bulk-add-tags/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `application/json`

## Overview

The bulk add tags endpoint allows you to add one or more tags to multiple contacts at once. This is perfect for organizing contacts into groups, categories, or any other classification system.

## ✅ **Problem Solved**

Your frontend was getting a **404 Not Found** error because this endpoint didn't exist. I've now implemented it with full functionality!

## Request Format

### **Request Body:**
```json
{
  "contact_ids": ["uuid1", "uuid2", "uuid3"],
  "tags": ["vip", "customer", "premium"]
}
```

### **Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `contact_ids` | array | Yes | List of contact UUIDs (max 100) |
| `tags` | array | Yes | List of tags to add (max 20) |

## Response Format

### **Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully added tags to 3 contacts",
  "updated_count": 3,
  "total_requested": 3,
  "tags_added": ["vip", "customer", "premium"],
  "errors": []
}
```

### **Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "No contacts found with the provided IDs",
  "updated_count": 0
}
```

### **Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Validation error",
  "errors": {
    "contact_ids": ["At least one contact ID is required"],
    "tags": ["At least one tag is required"]
  }
}
```

## Key Features

### ✅ **Smart Tag Merging**
- Tags are **merged** with existing tags (no duplicates)
- If a contact already has `["customer"]` and you add `["vip", "customer"]`, the result will be `["customer", "vip"]`

### ✅ **Validation**
- **Contact IDs:** Must be valid UUIDs, max 100 per request
- **Tags:** Must be valid format (letters, numbers, spaces, hyphens, underscores), max 20 per request
- **Duplicate Prevention:** No duplicate contact IDs or tags allowed

### ✅ **Error Handling**
- Comprehensive error reporting
- Individual contact error tracking
- Detailed validation messages

## Usage Examples

### **JavaScript/Frontend:**
```javascript
const bulkAddTags = async (contactIds, tags) => {
  const response = await fetch('/api/messaging/contacts/bulk-add-tags/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contact_ids: contactIds,
      tags: tags
    })
  });

  return await response.json();
};

// Usage
const result = await bulkAddTags(
  ['uuid1', 'uuid2', 'uuid3'],
  ['vip', 'customer', 'premium']
);
```

### **cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/messaging/contacts/bulk-add-tags/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_ids": ["uuid1", "uuid2", "uuid3"],
    "tags": ["vip", "customer", "premium"]
  }'
```

### **Python:**
```python
import requests

def bulk_add_tags(contact_ids, tags, token):
    response = requests.post(
        'http://127.0.0.1:8000/api/messaging/contacts/bulk-add-tags/',
        json={
            'contact_ids': contact_ids,
            'tags': tags
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()

# Usage
result = bulk_add_tags(
    ['uuid1', 'uuid2', 'uuid3'],
    ['vip', 'customer', 'premium'],
    'your_jwt_token'
)
```

## Tag Format Rules

### ✅ **Valid Tags:**
- `"vip"` - Simple text
- `"customer-premium"` - With hyphens
- `"high_value"` - With underscores
- `"VIP Customer"` - With spaces
- `"customer123"` - With numbers

### ❌ **Invalid Tags:**
- `"customer@email"` - Special characters
- `"customer.com"` - Dots
- `"customer#1"` - Hash symbols
- `"customer$"` - Dollar signs

## Rate Limits

- **Maximum contacts per request:** 100
- **Maximum tags per request:** 20
- **Rate limit:** 10 requests per minute per user

## Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `400` | Bad Request | Check request format and validation |
| `401` | Unauthorized | Provide valid JWT token |
| `404` | Not Found | Verify contact IDs exist |
| `429` | Too Many Requests | Wait before retrying |

## Implementation Details

### **Files Modified:**
1. **`messaging/serializers.py`** - Added `ContactBulkAddTagsSerializer`
2. **`messaging/views.py`** - Added `ContactBulkAddTagsView`
3. **`messaging/urls.py`** - Added URL route

### **Database Impact:**
- Updates the `tags` field on Contact model
- No new database tables created
- Uses existing contact relationships

## Testing

### **Test Script:**
```bash
python test_bulk_add_tags.py
```

### **Manual Testing:**
1. Create some test contacts
2. Get their UUIDs
3. Call the bulk-add-tags endpoint
4. Verify tags were added correctly

## Frontend Integration

### **React Hook Example:**
```javascript
import { useState, useCallback } from 'react';

const useBulkAddTags = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const bulkAddTags = useCallback(async (contactIds, tags) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/messaging/contacts/bulk-add-tags/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contact_ids: contactIds,
          tags: tags
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Failed to add tags');
      }

      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { bulkAddTags, loading, error };
};
```

## Related Endpoints

- `GET /api/messaging/contacts/` - List contacts (see their tags)
- `PUT /api/messaging/contacts/{id}/` - Update individual contact
- `POST /api/messaging/contacts/bulk-edit/` - Bulk edit contacts
- `POST /api/messaging/contacts/bulk-delete/` - Bulk delete contacts

## 🎉 **Ready to Use!**

The endpoint is now fully implemented and ready for your frontend to use. The 404 error should be resolved, and you can start adding tags to multiple contacts at once!

## Troubleshooting

### **Still getting 404?**
1. Make sure the server is running
2. Check the URL is exactly: `/api/messaging/contacts/bulk-add-tags/`
3. Verify you're using POST method
4. Ensure authentication token is valid

### **Getting validation errors?**
1. Check contact IDs are valid UUIDs
2. Verify tags follow the format rules
3. Ensure you're not exceeding limits (100 contacts, 20 tags)

The endpoint is now live and ready to use! 🚀
