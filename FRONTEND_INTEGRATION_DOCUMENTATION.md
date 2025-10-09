# Frontend Integration Documentation

## Overview
This document provides comprehensive API documentation for integrating the campaign and contact management system with the frontend. The system has been simplified by removing tenant complexity - all data is now user-specific.

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 📱 CONTACT MANAGEMENT

### 1. List Contacts (Smart Filtering)
**GET** `/messaging/contacts/`

**Query Parameters:**
- `search` (optional): Search by name, phone, or email
- `is_active` (optional): Filter by active status (true/false)
- `is_opted_in` (optional): Filter by opt-in status (true/false)
- `tag` (optional): Filter by a single tag (repeatable for multiple tags)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 20)

**Smart Features:**
- Multi-field search across name, phone, and email
- Tag-based filtering with support for multiple tags
- Optimized pagination with count metadata
- Real-time filtering without page reload

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "name": "John Doe",
        "phone_e164": "+255123456789",
        "email": "john@example.com",
        "is_active": true,
        "is_opted_in": true,
        "opt_in_at": "2024-01-01T10:00:00Z",
        "last_contacted_at": "2024-01-15T14:30:00Z",
        "attributes": {
          "company": "Acme Corp",
          "department": "Marketing"
        },
        "tags": ["vip", "marketing"],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-15T14:30:00Z"
      }
    ],
    "count": 150,
    "next": "http://localhost:8000/api/messaging/contacts/?page=2",
    "previous": null
  }
}
```

### 2. Create/Upsert Contact (Smart Deduplication)
**POST** `/messaging/contacts/`

**Smart Features:**
- Auto-upsert by `phone_e164` or `email` - prevents duplicates
- E.164 phone number validation and normalization
- Tag normalization and deduplication
- Attribute validation (flat JSON object)
- Idempotency support with `Idempotency-Key` header

**Request Body:**
```json
{
  "name": "Jane Smith",
  "phone_e164": "+255987654321",
  "email": "jane@example.com",
  "attributes": {
    "company": "Acme Corp",
    "department": "Marketing"
  },
  "tags": ["vip", "marketing"],
  "is_active": true
}
```

**Response (Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Jane Smith",
    "phone_e164": "+255987654321",
    "email": "jane@example.com",
    "is_active": true,
    "is_opted_in": false,
    "opt_in_at": null,
    "last_contacted_at": null,
    "attributes": {
      "company": "Acme Corp",
      "department": "Marketing"
    },
    "tags": ["vip", "marketing"],
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "upserted": false
  }
}
```

**Response (Upserted - Contact Already Exists):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Jane Smith",
    "phone_e164": "+255987654321",
    "email": "jane@example.com",
    "is_active": true,
    "is_opted_in": true,
    "opt_in_at": "2024-01-10T08:00:00Z",
    "last_contacted_at": null,
    "attributes": {
      "company": "Acme Corp",
      "department": "Marketing"
    },
    "tags": ["vip", "marketing"],
    "created_at": "2023-12-15T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z",
    "upserted": true
  }
}
```

**Validation Error Response:**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "phone_e164": ["Invalid E.164 format"],
    "email": ["Invalid email address"]
  }
}
```

### 3. Update Contact
**PUT** `/messaging/contacts/{id}/`

**Request Body:**
```json
{
  "name": "Jane Smith Updated",
  "email": "jane.updated@example.com",
  "attributes": {
    "company": "New Corp",
    "department": "Sales"
  },
  "tags": ["vip", "sales"]
}
```

### 4. Delete Contact
**DELETE** `/messaging/contacts/{id}/`

**Response:**
```json
{
  "success": true,
  "message": "Contact deleted successfully"
}
```

### 5. Opt-in Contact (Compliance Tracking)
**POST** `/messaging/contacts/{id}/opt-in/`

**Smart Features:**
- Compliance tracking with timestamp
- Automatic status updates
- Audit trail for opt-in events

**Response:**
```json
{
  "success": true,
  "message": "Contact opted in successfully",
  "data": {
    "id": "uuid",
    "is_opted_in": true,
    "opt_in_at": "2024-01-20T09:00:00Z"
  }
}
```

### 6. Opt-out Contact (Reason Tracking)
**POST** `/messaging/contacts/{id}/opt-out/`

**Smart Features:**
- Reason tracking for compliance
- Automatic status updates
- Audit trail for opt-out events

**Request Body:**
```json
{
  "reason": "User requested"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Contact opted out successfully",
  "data": {
    "id": "uuid",
    "is_opted_in": false,
    "opt_out_reason": "User requested",
    "opt_out_at": "2024-01-20T09:05:00Z"
  }
}
```

---

## 🎯 CAMPAIGN MANAGEMENT

### 1. List Campaigns (Smart Analytics)
**GET** `/messaging/campaigns/`

**Query Parameters:**
- `status` (optional): Filter by status (draft, scheduled, running, paused, completed, cancelled, failed)
- `type` (optional): Filter by type (sms, whatsapp, email, mixed)
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 20)

**Smart Features:**
- Real-time analytics and metrics
- Smart filtering by status and type
- Progress tracking and delivery rates
- Action permissions based on campaign state

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "uuid",
        "name": "Black Friday Sale",
        "description": "Promotional campaign for Black Friday",
        "campaign_type": "sms",
        "campaign_type_display": "SMS",
        "message_text": "Get 50% off on all items! Use code BLACK50",
        "template": null,
        "status": "running",
        "status_display": "Running",
        "scheduled_at": null,
        "started_at": "2024-01-15T10:00:00Z",
        "completed_at": null,
        "total_recipients": 1000,
        "sent_count": 750,
        "delivered_count": 720,
        "read_count": 450,
        "failed_count": 30,
        "estimated_cost": 250.00,
        "actual_cost": 187.50,
        "progress_percentage": 75,
        "delivery_rate": 96.0,
        "read_rate": 62.5,
        "is_active": true,
        "can_edit": false,
        "can_start": false,
        "can_pause": true,
        "can_cancel": true,
        "is_recurring": false,
        "recurring_schedule": {},
        "settings": {},
        "created_by": "uuid",
        "created_by_name": "John Doe",
        "created_at": "2024-01-15T09:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "target_contact_count": 1000,
        "target_segment_names": ["VIP Customers", "New Subscribers"]
      }
    ],
    "count": 25,
    "next": "http://localhost:8000/api/messaging/campaigns/?page=2",
    "previous": null
  }
}
```

### 2. Create Campaign (Smart Targeting & Cost Estimation)
**POST** `/messaging/campaigns/`

**Smart Features:**
- Auto-recipient resolution from contacts, segments, and criteria
- Duplicate removal and opt-in validation
- Real-time cost estimation
- Dry-run mode for testing (`?dry_run=true`)
- Idempotency support with `Idempotency-Key` header

**Request Body:**
```json
{
  "name": "New Year Promotion",
  "description": "Welcome the new year with our special offers",
  "campaign_type": "sms",
  "message_text": "Happy New Year! Get 30% off on your first order. Use code NEWYEAR30",
  "template": null,
  "scheduled_at": "2024-01-01T09:00:00Z",
  "target_contact_ids": ["uuid1", "uuid2", "uuid3"],
  "target_segment_ids": ["uuid4", "uuid5"],
  "target_criteria": {
    "tags": ["vip", "premium"],
    "opt_in_status": "opted_in"
  },
  "settings": {
    "send_time": "09:00",
    "timezone": "Africa/Dar_es_Salaam"
  },
  "is_recurring": false,
  "recurring_schedule": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "New Year Promotion",
    "description": "Welcome the new year with our special offers",
    "campaign_type": "sms",
    "status": "draft",
    "total_recipients": 500,
    "estimated_cost": 125.0,
    "created_at": "2024-01-01T08:00:00Z",
    "target_contact_count": 200,
    "target_segment_names": ["VIP Customers"]
  }
}
```

**Dry-run Response:**
```json
{
  "success": true,
  "data": {
    "total_recipients": 500,
    "estimated_cost": 125.0,
    "explanations": [
      "Duplicates removed: 25 contacts",
      "Opted-out contacts excluded: 10 contacts",
      "Invalid numbers excluded: 5 contacts"
    ]
  }
}
```

### 3. Get Campaign Details
**GET** `/messaging/campaigns/{id}/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "New Year Promotion",
    "description": "Welcome the new year with our special offers",
    "campaign_type": "sms",
    "message_text": "Happy New Year! Get 30% off on your first order. Use code NEWYEAR30",
    "status": "draft",
    "total_recipients": 500,
    "sent_count": 0,
    "delivered_count": 0,
    "read_count": 0,
    "failed_count": 0,
    "progress_percentage": 0,
    "delivery_rate": 0,
    "read_rate": 0,
    "is_active": false,
    "can_edit": true,
    "can_start": true,
    "can_pause": false,
    "can_cancel": true,
    "created_by": "uuid",
    "created_by_name": "John Doe",
    "created_at": "2024-01-01T08:00:00Z",
    "updated_at": "2024-01-01T08:00:00Z"
  }
}
```

### 4. Update Campaign
**PUT** `/messaging/campaigns/{id}/`

**Request Body:**
```json
{
  "name": "Updated Campaign Name",
  "description": "Updated description",
  "message_text": "Updated message text",
  "scheduled_at": "2024-01-02T10:00:00Z",
  "target_contact_ids": ["uuid1", "uuid2"],
  "target_segment_ids": ["uuid3"]
}
```

### 5. Delete Campaign
**DELETE** `/messaging/campaigns/{id}/`

**Response:**
```json
{
  "success": true,
  "message": "Campaign deleted successfully"
}
```

### 6. Start Campaign
**POST** `/messaging/campaigns/{id}/start/`

**Response:**
```json
{
  "success": true,
  "message": "Campaign started successfully",
  "campaign": {
    "id": "uuid",
    "status": "running",
    "started_at": "2024-01-01T10:00:00Z"
  }
}
```

### 7. Pause Campaign
**POST** `/messaging/campaigns/{id}/pause/`

**Response:**
```json
{
  "success": true,
  "message": "Campaign paused successfully",
  "campaign": {
    "id": "uuid",
    "status": "paused"
  }
}
```

### 8. Cancel Campaign
**POST** `/messaging/campaigns/{id}/cancel/`

**Response:**
```json
{
  "success": true,
  "message": "Campaign cancelled successfully",
  "campaign": {
    "id": "uuid",
    "status": "cancelled",
    "completed_at": "2024-01-01T10:30:00Z"
  }
}
```

### 9. Get Campaign Analytics
**GET** `/messaging/campaigns/{id}/analytics/`

**Response:**
```json
{
  "success": true,
  "analytics": {
    "campaign_id": "uuid",
    "campaign_name": "Black Friday Sale",
    "status": "running",
    "total_recipients": 1000,
    "sent_count": 750,
    "delivered_count": 720,
    "read_count": 450,
    "failed_count": 30,
    "progress_percentage": 75,
    "delivery_rate": 96.0,
    "read_rate": 62.5,
    "estimated_cost": 250.00,
    "actual_cost": 187.50,
    "created_at": "2024-01-15T09:00:00Z",
    "started_at": "2024-01-15T10:00:00Z",
    "completed_at": null
  }
}
```

### 10. Duplicate Campaign
**POST** `/messaging/campaigns/{id}/duplicate/`

**Response:**
```json
{
  "success": true,
  "message": "Campaign duplicated successfully",
  "campaign": {
    "id": "new-uuid",
    "name": "Black Friday Sale (Copy)",
    "status": "draft",
    "created_at": "2024-01-15T11:00:00Z"
  }
}
```

### 11. Get Campaign Summary
**GET** `/messaging/campaigns/summary/`

**Response:**
```json
{
  "success": true,
  "summary": {
    "status_counts": {
      "draft": 5,
      "running": 2,
      "completed": 15,
      "cancelled": 1
    },
    "total_stats": {
      "total_campaigns": 23,
      "total_recipients": 50000,
      "total_sent": 45000,
      "total_delivered": 43200,
      "total_read": 27000,
      "total_failed": 1800,
      "total_estimated_cost": 15000.00,
      "total_actual_cost": 13500.00
    },
    "recent_campaigns": [
      {
        "id": "uuid",
        "name": "Latest Campaign",
        "status": "running",
        "progress_percentage": 60,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

## 📊 SEGMENT MANAGEMENT

### 1. List Segments
**GET** `/messaging/segments/`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "VIP Customers",
      "description": "High-value customers",
      "contact_count": 150,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

### 2. Create Segment
**POST** `/messaging/segments/`

**Request Body:**
```json
{
  "name": "New Subscribers",
  "description": "Customers who joined in the last 30 days",
  "filter_json": {
    "created_after": "2023-12-01",
    "tags": ["new"]
  }
}
```

---

## 🎨 FRONTEND INTEGRATION EXAMPLES

### React Hook Example
```typescript
import { useState, useEffect } from 'react';
import { apiClient } from './api';

export const useCampaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchCampaigns = async (filters = {}) => {
    setLoading(true);
    try {
      const response = await apiClient.get('/messaging/campaigns/', { params: filters });
      setCampaigns(response.data.data.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createCampaign = async (campaignData) => {
    try {
      const response = await apiClient.post('/messaging/campaigns/', campaignData);
      setCampaigns(prev => [response.data.data, ...prev]);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const startCampaign = async (campaignId) => {
    try {
      const response = await apiClient.post(`/messaging/campaigns/${campaignId}/start/`);
      // Update local state
      setCampaigns(prev => prev.map(c => 
        c.id === campaignId ? { ...c, status: 'running', started_at: new Date() } : c
      ));
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  return {
    campaigns,
    loading,
    error,
    fetchCampaigns,
    createCampaign,
    startCampaign
  };
};
```

### Campaign Form Component Example
```typescript
import React, { useState } from 'react';

const CreateCampaignForm = ({ onSubmit, contacts, segments }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    campaign_type: 'sms',
    message_text: '',
    scheduled_at: '',
    target_contact_ids: [],
    target_segment_ids: [],
    settings: {}
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await onSubmit(formData);
      // Reset form or show success message
    } catch (error) {
      console.error('Error creating campaign:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Campaign Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Message Text</label>
        <textarea
          value={formData.message_text}
          onChange={(e) => setFormData({...formData, message_text: e.target.value})}
          required
        />
      </div>
      
      <div>
        <label>Target Contacts</label>
        <select
          multiple
          value={formData.target_contact_ids}
          onChange={(e) => setFormData({
            ...formData, 
            target_contact_ids: Array.from(e.target.selectedOptions, option => option.value)
          })}
        >
          {contacts.map(contact => (
            <option key={contact.id} value={contact.id}>
              {contact.name} - {contact.phone_e164}
            </option>
          ))}
        </select>
      </div>
      
      <button type="submit">Create Campaign</button>
    </form>
  );
};
```

---

## 🚨 ERROR HANDLING

All API responses follow this format:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field_name": ["Specific field error"]
  }
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## 📝 NOTES FOR FRONTEND DEVELOPER

1. **User-Specific Data**: All campaigns and contacts are automatically filtered by the authenticated user. No need to handle tenant logic.

2. **Real-time Updates**: Consider implementing WebSocket connections for real-time campaign status updates.

3. **Pagination**: All list endpoints support pagination. Always check for `next` and `previous` URLs.

4. **Validation**: The backend validates all data. Display validation errors from the `errors` field in error responses.

5. **Campaign Status Flow**: 
   - `draft` → `scheduled` (when scheduled_at is set) → `running` → `completed`
   - Can be `paused` from `running` status
   - Can be `cancelled` from any status except `completed`

6. **Phone Number Format**: Always use E.164 format (+255123456789) for phone numbers.

7. **Date Format**: Use ISO 8601 format for all dates (2024-01-01T10:00:00Z).

8. **File Uploads**: For contact imports, use the bulk upload endpoint with CSV files.

---

## 🧠 Smart Management Rules & Best Practices

### Contact Management Rules
- **Uniqueness**: `phone_e164` and `email` are unique across contacts
- **Upsert Logic**: Create operations automatically upsert by phone/email
- **Normalization**: Phone numbers auto-converted to E.164 format
- **Tag Management**: Tags normalized to lowercase and deduplicated
- **Attribute Validation**: Must be flat JSON object with string/number/boolean values
- **Idempotency**: Support `Idempotency-Key` header for safe retries

### Campaign Management Rules
- **Recipient Resolution**: Union of contacts from IDs, segments, and criteria
- **Duplicate Removal**: Automatic deduplication of target contacts
- **Opt-in Compliance**: Only opted-in contacts receive messages
- **Cost Estimation**: Real-time calculation based on channel pricing
- **Status Management**: Smart state transitions with validation
- **Idempotency**: Create operations support `Idempotency-Key` header

### Error Handling (Enhanced)

**Validation Error Response:**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "phone_e164": ["Invalid E.164 format"],
    "email": ["Invalid email address"],
    "message_text": ["Message too long for single SMS"]
  }
}
```

**Business Logic Error Response:**
```json
{
  "success": false,
  "message": "Campaign cannot be started",
  "error_code": "INVALID_STATUS",
  "details": {
    "current_status": "completed",
    "allowed_statuses": ["draft", "scheduled"]
  }
}
```

### Rate Limiting (Smart)
- **Authentication endpoints**: 5 requests per minute
- **SMS sending**: 10 requests per minute
- **Contact operations**: 100 requests per minute
- **Campaign operations**: 50 requests per minute
- **Bulk operations**: 10 requests per minute

### Idempotency Support
All create operations support the `Idempotency-Key` header:
```
Idempotency-Key: unique-request-id-12345
```

Keys are valid for 24 hours and prevent duplicate operations.

### Frontend Integration Best Practices

#### 1. Smart Contact Management
```typescript
// Use upsert for contact creation
const createContact = async (contactData) => {
  const response = await apiClient.post('/messaging/contacts/', contactData, {
    headers: {
      'Idempotency-Key': `contact-${Date.now()}-${Math.random()}`
    }
  });
  
  if (response.data.upserted) {
    showNotification('Contact updated successfully');
  } else {
    showNotification('Contact created successfully');
  }
  
  return response.data;
};
```

#### 2. Smart Campaign Creation
```typescript
// Use dry-run for cost estimation
const estimateCampaignCost = async (campaignData) => {
  const response = await apiClient.post('/messaging/campaigns/?dry_run=true', campaignData);
  return response.data;
};

// Create campaign with idempotency
const createCampaign = async (campaignData) => {
  const response = await apiClient.post('/messaging/campaigns/', campaignData, {
    headers: {
      'Idempotency-Key': `campaign-${Date.now()}-${Math.random()}`
    }
  });
  
  return response.data;
};
```

#### 3. Real-time Updates
```typescript
// Poll for campaign updates
const useCampaignUpdates = (campaignId) => {
  const [campaign, setCampaign] = useState(null);
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await apiClient.get(`/messaging/campaigns/${campaignId}/`);
      setCampaign(response.data.data);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [campaignId]);
  
  return campaign;
};
```

#### 4. Error Handling
```typescript
const handleApiError = (error) => {
  if (error.response?.data?.errors) {
    // Display field-specific validation errors
    Object.entries(error.response.data.errors).forEach(([field, messages]) => {
      showFieldError(field, messages[0]);
    });
  } else if (error.response?.data?.error_code) {
    // Handle business logic errors
    showBusinessError(error.response.data.message, error.response.data.details);
  } else {
    // Generic error handling
    showGenericError(error.message);
  }
};
```

This documentation provides everything needed for smart frontend integration with intelligent error handling, real-time updates, and best practices. The API is designed to be developer-friendly while maintaining data integrity and compliance.
