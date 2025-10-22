# Message Template API Documentation

## Overview

The Message Template API provides comprehensive functionality for managing message templates, including creation, editing, approval workflows, usage tracking, and advanced filtering. This API supports the template management interface shown in the UI screenshots.

## Base URL

```
/api/messaging/templates/
```

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. List Templates

**GET** `/api/messaging/templates/`

List all templates with advanced filtering, searching, and pagination.

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by category | `onboarding`, `promotions`, `reminders` |
| `language` | string | Filter by language | `en`, `sw`, `fr`, `ar` |
| `channel` | string | Filter by channel | `sms`, `whatsapp`, `email`, `all` |
| `status` | string | Filter by status | `draft`, `pending`, `approved`, `rejected` |
| `approved` | boolean | Filter by approval status | `true`, `false` |
| `is_favorite` | boolean | Filter by favorite status | `true`, `false` |
| `favorites_only` | boolean | Show only favorites | `true`, `false` |
| `approved_only` | boolean | Show only approved | `true`, `false` |
| `search` | string | Search in name, body_text, description | `Karibu` |
| `ordering` | string | Sort order | `name`, `-created_at`, `usage_count` |
| `page` | integer | Page number | `1`, `2`, `3` |
| `page_size` | integer | Items per page | `10`, `20`, `50` |

#### Response

```json
{
  "templates": [
    {
      "id": "uuid",
      "name": "Karibu - Asante kwa Kutua...",
      "category": "onboarding",
      "category_display": "Onboarding",
      "language": "sw",
      "language_display": "Kiswahili",
      "channel": "whatsapp",
      "channel_display": "WhatsApp",
      "preview_text": "Habari {{name}}! Asante kwa kutuamini {{company}}. Akaunti yako iko tayari—anza hapa: {{short_url}}",
      "variables_count": 3,
      "status": "approved",
      "approved": true,
      "is_favorite": true,
      "usage_count": 0,
      "last_used_display": "Never used",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "filter_options": {
    "categories": [
      {"value": "onboarding", "label": "Onboarding"},
      {"value": "promotions", "label": "Promotions"},
      {"value": "reminders", "label": "Reminders"},
      {"value": "loyalty", "label": "Loyalty"},
      {"value": "win_back", "label": "Win-Back"},
      {"value": "post_purchase", "label": "Post-Purchase"}
    ],
    "languages": [
      {"value": "en", "label": "English"},
      {"value": "sw", "label": "Kiswahili"},
      {"value": "fr", "label": "French"},
      {"value": "ar", "label": "Arabic"}
    ],
    "channels": [
      {"value": "sms", "label": "SMS"},
      {"value": "whatsapp", "label": "WhatsApp"},
      {"value": "email", "label": "Email"},
      {"value": "all", "label": "All Channels"}
    ],
    "statuses": [
      {"value": "draft", "label": "Draft"},
      {"value": "pending", "label": "Pending"},
      {"value": "approved", "label": "Approved"},
      {"value": "rejected", "label": "Rejected"}
    ]
  },
  "total_count": 25
}
```

---

### 2. Create Template

**POST** `/api/messaging/templates/`

Create a new message template.

#### Request Body

```json
{
  "name": "Karibu - Asante kwa Kutua...",
  "category": "onboarding",
  "language": "sw",
  "channel": "whatsapp",
  "body_text": "Habari {{name}}! Asante kwa kutuamini {{company}}. Akaunti yako iko tayari—anza hapa: {{short_url}}",
  "description": "Welcome message for new users",
  "status": "draft",
  "is_favorite": true
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Template name (unique per channel) |
| `category` | string | Yes | Template category |
| `language` | string | Yes | Template language |
| `channel` | string | Yes | Communication channel |
| `body_text` | string | Yes | Message content with variables |
| `description` | string | No | Template description |
| `status` | string | No | Template status (default: draft) |
| `is_favorite` | boolean | No | Favorite status (default: false) |

#### Response

```json
{
  "id": "uuid",
  "name": "Karibu - Asante kwa Kutua...",
  "category": "onboarding",
  "category_display": "Onboarding",
  "language": "sw",
  "language_display": "Kiswahili",
  "channel": "whatsapp",
  "channel_display": "WhatsApp",
  "body_text": "Habari {{name}}! Asante kwa kutuamini {{company}}. Akaunti yako iko tayari—anza hapa: {{short_url}}",
  "description": "Welcome message for new users",
  "variables": ["name", "company", "short_url"],
  "variables_count": 3,
  "status": "draft",
  "status_display": "Draft",
  "approved": false,
  "approval_status": "pending",
  "is_favorite": true,
  "wa_template_name": "",
  "wa_template_id": "",
  "usage_count": 0,
  "last_used_at": null,
  "last_used_display": "Never used",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by": "uuid",
  "created_by_name": "Test User"
}
```

---

### 3. Get Template Details

**GET** `/api/messaging/templates/{id}/`

Get detailed information about a specific template.

#### Response

```json
{
  "id": "uuid",
  "name": "Karibu - Asante kwa Kutua...",
  "category": "onboarding",
  "category_display": "Onboarding",
  "language": "sw",
  "language_display": "Kiswahili",
  "channel": "whatsapp",
  "channel_display": "WhatsApp",
  "body_text": "Habari {{name}}! Asante kwa kutuamini {{company}}. Akaunti yako iko tayari—anza hapa: {{short_url}}",
  "formatted_body_text": "Habari <span class='variable'>{{name}}</span>! Asante kwa kutuamini <span class='variable'>{{company}}</span>. Akaunti yako iko tayari—anza hapa: <span class='variable'>{{short_url}}</span>",
  "description": "Welcome message for new users",
  "variables": ["name", "company", "short_url"],
  "variables_count": 3,
  "status": "approved",
  "status_display": "Approved",
  "approved": true,
  "approval_status": "approved",
  "is_favorite": true,
  "wa_template_name": "",
  "wa_template_id": "",
  "usage_count": 5,
  "last_used_at": "2024-01-15T10:30:00Z",
  "last_used_display": "2024-01-15",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "created_by": "uuid",
  "created_by_name": "Test User",
  "statistics": {
    "total_uses": 5,
    "last_used": "2024-01-15",
    "created": "2024-01-15",
    "variables_count": 3
  }
}
```

---

### 4. Update Template

**PUT/PATCH** `/api/messaging/templates/{id}/`

Update an existing template.

#### Request Body (PATCH)

```json
{
  "name": "Updated Template Name",
  "description": "Updated description",
  "body_text": "Updated message with {{variable}}",
  "status": "pending",
  "is_favorite": false
}
```

#### Response

```json
{
  "id": "uuid",
  "name": "Updated Template Name",
  "category": "onboarding",
  "category_display": "Onboarding",
  "language": "sw",
  "language_display": "Kiswahili",
  "channel": "whatsapp",
  "channel_display": "WhatsApp",
  "body_text": "Updated message with {{variable}}",
  "description": "Updated description",
  "variables": ["variable"],
  "variables_count": 1,
  "status": "pending",
  "status_display": "Pending",
  "approved": false,
  "approval_status": "pending",
  "is_favorite": false,
  "usage_count": 5,
  "last_used_at": "2024-01-15T10:30:00Z",
  "last_used_display": "2024-01-15",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "created_by": "uuid",
  "created_by_name": "Test User"
}
```

---

### 5. Delete Template

**DELETE** `/api/messaging/templates/{id}/`

Delete a template.

#### Response

```json
{
  "message": "Template deleted successfully"
}
```

---

## Template Actions

### 6. Toggle Favorite

**POST** `/api/messaging/templates/{id}/toggle-favorite/`

Toggle the favorite status of a template.

#### Response

```json
{
  "message": "Template added to favorites",
  "is_favorite": true
}
```

---

### 7. Increment Usage

**POST** `/api/messaging/templates/{id}/increment-usage/`

Increment the usage count and update last used timestamp.

#### Response

```json
{
  "message": "Usage count updated",
  "usage_count": 6,
  "last_used_at": "2024-01-15T12:00:00Z"
}
```

---

### 8. Approve Template

**POST** `/api/messaging/templates/{id}/approve/`

Approve a template for use.

#### Response

```json
{
  "message": "Template approved successfully",
  "approved": true,
  "status": "approved"
}
```

---

### 9. Reject Template

**POST** `/api/messaging/templates/{id}/reject/`

Reject a template.

#### Request Body

```json
{
  "reason": "Content violates guidelines"
}
```

#### Response

```json
{
  "message": "Template rejected successfully",
  "approved": false,
  "status": "rejected",
  "reason": "Content violates guidelines"
}
```

---

### 10. Get Template Variables

**GET** `/api/messaging/templates/{id}/variables/`

Get the variables used in a template.

#### Response

```json
{
  "template_id": "uuid",
  "template_name": "Karibu - Asante kwa Kutua...",
  "variables": ["name", "company", "short_url"],
  "variables_count": 3
}
```

---

### 11. Copy Template

**POST** `/api/messaging/templates/{id}/copy/`

Create a copy of an existing template.

#### Request Body

```json
{
  "name": "Karibu - Copy"
}
```

#### Response

```json
{
  "message": "Template copied successfully",
  "template": {
    "id": "new-uuid",
    "name": "Karibu - Copy",
    "category": "onboarding",
    "language": "sw",
    "channel": "whatsapp",
    "body_text": "Habari {{name}}! Asante kwa kutuamini {{company}}. Akaunti yako iko tayari—anza hapa: {{short_url}}",
    "description": "Welcome message for new users",
    "status": "draft",
    "variables": ["name", "company", "short_url"],
    "variables_count": 3,
    "usage_count": 0,
    "last_used_display": "Never used",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
}
```

---

### 12. Template Statistics

**GET** `/api/messaging/templates/statistics/`

Get comprehensive statistics about templates.

#### Response

```json
{
  "overview": {
    "total_templates": 25,
    "approved_templates": 20,
    "draft_templates": 3,
    "favorite_templates": 8,
    "approval_rate": 80.0
  },
  "category_breakdown": [
    {
      "category": "onboarding",
      "category_display": "Onboarding",
      "count": 5
    },
    {
      "category": "promotions",
      "category_display": "Promotions",
      "count": 8
    },
    {
      "category": "reminders",
      "category_display": "Reminders",
      "count": 4
    }
  ],
  "language_breakdown": [
    {
      "language": "sw",
      "language_display": "Kiswahili",
      "count": 15
    },
    {
      "language": "en",
      "language_display": "English",
      "count": 10
    }
  ],
  "channel_breakdown": [
    {
      "channel": "whatsapp",
      "channel_display": "WhatsApp",
      "count": 18
    },
    {
      "channel": "sms",
      "channel_display": "SMS",
      "count": 7
    }
  ]
}
```

---

## Template Categories

| Value | Display Name | Description |
|-------|--------------|-------------|
| `onboarding` | Onboarding | Welcome and setup messages |
| `promotions` | Promotions | Marketing and promotional content |
| `reminders` | Reminders | Appointment and service reminders |
| `loyalty` | Loyalty | Customer retention messages |
| `win_back` | Win-Back | Re-engagement campaigns |
| `post_purchase` | Post-Purchase | Post-purchase follow-up |
| `authentication` | Authentication | Login and verification |
| `marketing` | Marketing | General marketing content |
| `utility` | Utility | Functional messages |
| `otp` | One-time password | OTP and verification codes |

---

## Template Languages

| Value | Display Name |
|-------|--------------|
| `en` | English |
| `sw` | Kiswahili |
| `fr` | French |
| `ar` | Arabic |

---

## Template Channels

| Value | Display Name |
|-------|--------------|
| `sms` | SMS |
| `whatsapp` | WhatsApp |
| `email` | Email |
| `all` | All Channels |

---

## Template Status

| Value | Display Name | Description |
|-------|--------------|-------------|
| `draft` | Draft | Template being created |
| `pending` | Pending | Awaiting approval |
| `approved` | Approved | Ready for use |
| `rejected` | Rejected | Not approved for use |

---

## Variable Format

Templates use double curly brace syntax for variables:

```
Hello {{name}}, your order {{order_id}} is ready for pickup at {{location}}.
```

**Valid variables:**
- `{{name}}` ✅
- `{{order_id}}` ✅
- `{{location}}` ✅

**Invalid variables:**
- `{{name with spaces}}` ❌
- `{{name-with-dashes}}` ❌
- `{{name.with.dots}}` ❌

---

## Frontend Integration Examples

### JavaScript - List Templates with Filtering

```javascript
const getTemplates = async (filters = {}) => {
  const params = new URLSearchParams();
  
  if (filters.category) params.append('category', filters.category);
  if (filters.language) params.append('language', filters.language);
  if (filters.channel) params.append('channel', filters.channel);
  if (filters.search) params.append('search', filters.search);
  if (filters.favorites_only) params.append('favorites_only', 'true');
  if (filters.approved_only) params.append('approved_only', 'true');
  
  const response = await fetch(`/api/messaging/templates/?${params}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

// Usage
const templates = await getTemplates({
  category: 'onboarding',
  language: 'sw',
  favorites_only: true
});
```

### JavaScript - Create Template

```javascript
const createTemplate = async (templateData) => {
  const response = await fetch('/api/messaging/templates/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(templateData)
  });
  
  return await response.json();
};

// Usage
const newTemplate = await createTemplate({
  name: 'Welcome Message',
  category: 'onboarding',
  language: 'sw',
  channel: 'whatsapp',
  body_text: 'Habari {{name}}! Karibu kwenye {{company}}.',
  description: 'Welcome message for new users',
  is_favorite: true
});
```

### JavaScript - Template Actions

```javascript
const toggleFavorite = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/toggle-favorite/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

const approveTemplate = async (templateId) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/approve/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

const copyTemplate = async (templateId, newName) => {
  const response = await fetch(`/api/messaging/templates/${templateId}/copy/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ name: newName })
  });
  
  return await response.json();
};
```

### React Component Example

```jsx
import React, { useState, useEffect } from 'react';

const TemplateManager = () => {
  const [templates, setTemplates] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    language: '',
    channel: '',
    search: '',
    favorites_only: false,
    approved_only: false
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, [filters]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/messaging/templates/?${new URLSearchParams(filters)}`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setTemplates(data.templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (templateId) => {
    try {
      await fetch(`/api/messaging/templates/${templateId}/toggle-favorite/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      loadTemplates(); // Reload to update UI
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleApproveTemplate = async (templateId) => {
    try {
      await fetch(`/api/messaging/templates/${templateId}/approve/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      loadTemplates(); // Reload to update UI
    } catch (error) {
      console.error('Failed to approve template:', error);
    }
  };

  return (
    <div className="template-manager">
      <h2>Templates</h2>
      
      {/* Filters */}
      <div className="filters">
        <input
          type="text"
          placeholder="Search templates..."
          value={filters.search}
          onChange={(e) => setFilters({...filters, search: e.target.value})}
        />
        
        <select
          value={filters.category}
          onChange={(e) => setFilters({...filters, category: e.target.value})}
        >
          <option value="">All categories</option>
          <option value="onboarding">Onboarding</option>
          <option value="promotions">Promotions</option>
          <option value="reminders">Reminders</option>
        </select>
        
        <select
          value={filters.language}
          onChange={(e) => setFilters({...filters, language: e.target.value})}
        >
          <option value="">All languages</option>
          <option value="en">English</option>
          <option value="sw">Kiswahili</option>
        </select>
        
        <select
          value={filters.channel}
          onChange={(e) => setFilters({...filters, channel: e.target.value})}
        >
          <option value="">All channels</option>
          <option value="sms">SMS</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="email">Email</option>
        </select>
        
        <label>
          <input
            type="checkbox"
            checked={filters.favorites_only}
            onChange={(e) => setFilters({...filters, favorites_only: e.target.checked})}
          />
          Favorites only
        </label>
        
        <label>
          <input
            type="checkbox"
            checked={filters.approved_only}
            onChange={(e) => setFilters({...filters, approved_only: e.target.checked})}
          />
          Approved only
        </label>
      </div>

      {/* Template List */}
      <div className="template-grid">
        {loading ? (
          <div>Loading...</div>
        ) : (
          templates.map(template => (
            <div key={template.id} className="template-card">
              <div className="template-header">
                <h3>{template.name}</h3>
                <div className="template-actions">
                  <button
                    onClick={() => handleToggleFavorite(template.id)}
                    className={template.is_favorite ? 'favorite active' : 'favorite'}
                  >
                    ⭐
                  </button>
                  <button className="more-options">⋯</button>
                </div>
              </div>
              
              <div className="template-tags">
                <span className="category-tag">{template.category_display}</span>
                <span className="language-tag">{template.language_display}</span>
              </div>
              
              <div className="template-status">
                {template.approved && <span className="approved">✓ Approved</span>}
              </div>
              
              <div className="template-content">
                <p>{template.preview_text}</p>
              </div>
              
              <div className="template-variables">
                <span>Variables: {template.variables_count}</span>
              </div>
              
              <div className="template-stats">
                <span>Used {template.usage_count} times</span>
                <span>Last used {template.last_used_display}</span>
              </div>
              
              <div className="template-actions">
                <button onClick={() => handleApproveTemplate(template.id)}>
                  Approve
                </button>
                <button>Edit</button>
                <button>Copy</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TemplateManager;
```

---

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "name": ["A template with this name already exists for whatsapp channel."],
  "body_text": ["Body text cannot be empty."]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
  "detail": "A server error occurred."
}
```

---

## Rate Limiting

Template endpoints are subject to rate limiting:

- **List/Create/Update**: 100 requests per minute per user
- **Actions**: 50 requests per minute per user
- **Statistics**: 20 requests per minute per user

---

## Testing

Run the template test suite:

```bash
python test_template_endpoints.py
```

This will test all template functionality including:
- CRUD operations
- Filtering and searching
- Template actions
- Variable extraction
- Usage tracking
- Statistics

---

## Summary

The Message Template API provides:

✅ **Complete CRUD Operations** - Create, read, update, delete templates
✅ **Advanced Filtering** - Filter by category, language, channel, status
✅ **Search Functionality** - Search in name, content, and description
✅ **Template Actions** - Favorite, approve, reject, copy templates
✅ **Usage Tracking** - Track usage count and last used date
✅ **Variable Management** - Automatic variable extraction and validation
✅ **Statistics** - Comprehensive template analytics
✅ **Multi-language Support** - Support for multiple languages
✅ **Multi-channel Support** - SMS, WhatsApp, Email, All channels
✅ **Approval Workflow** - Draft, pending, approved, rejected statuses
✅ **Frontend Ready** - Complete integration examples

This API fully supports the template management interface shown in the UI screenshots and provides all the functionality needed for a comprehensive template management system.
