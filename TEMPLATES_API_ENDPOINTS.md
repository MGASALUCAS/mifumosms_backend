# Templates API Endpoints

## Base URL
```
http://127.0.0.1:8001/api/messaging/
```

## Authentication
All endpoints require JWT authentication:
```javascript
headers: {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
}
```

---

## 1. Templates List

**Endpoint:** `GET /api/messaging/templates/`

**Purpose:** Get list of all templates with filtering options

### Query Parameters:
- `category` - Filter by category (onboarding, promotions, reminders, etc.)
- `language` - Filter by language (en, sw, fr, ar)
- `channel` - Filter by channel (sms, whatsapp, email, all)
- `search` - Search in template name and content
- `favorites_only` - Show only favorite templates
- `approved_only` - Show only approved templates

### JSON Response:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": {
    "templates": [
      {
        "id": "ca4403a6-f51b-48bf-8f5c-8a0921096c67",
        "name": "Test Welcome Template",
        "category": "onboarding",
        "category_display": "Onboarding",
        "language": "en",
        "language_display": "English",
        "channel": "sms",
        "channel_display": "SMS",
        "preview_text": "Hello, welcome to our service! Your account is ready.",
        "variables_count": 0,
        "status": "draft",
        "approved": false,
        "is_favorite": false,
        "usage_count": 0,
        "last_used_display": "Never used",
        "created_at": "2025-10-23T03:28:45.889638+03:00",
        "updated_at": "2025-10-23T03:28:45.952538+03:00"
      }
    ],
    "filter_options": {
      "categories": [
        {"value": "onboarding", "label": "Onboarding"},
        {"value": "promotions", "label": "Promotions"},
        {"value": "reminders", "label": "Reminders"},
        {"value": "loyalty", "label": "Loyalty"},
        {"value": "win_back", "label": "Win-Back"},
        {"value": "post_purchase", "label": "Post-Purchase"},
        {"value": "authentication", "label": "Authentication"},
        {"value": "marketing", "label": "Marketing"},
        {"value": "utility", "label": "Utility"},
        {"value": "otp", "label": "One-time password"}
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
        {"value": "pending", "label": "Pending"},
        {"value": "approved", "label": "Approved"},
        {"value": "rejected", "label": "Rejected"},
        {"value": "draft", "label": "Draft"}
      ]
    },
    "total_count": 1
  }
}
```

---

## 2. Create Template

**Endpoint:** `POST /api/messaging/templates/`

**Purpose:** Create a new message template

### Request Body:
```json
{
  "name": "Welcome Template",
  "body_text": "Hello, welcome to our service! Your account is ready.",
  "category": "onboarding",
  "language": "en",
  "channel": "sms",
  "description": "A welcome template for new users"
}
```

### JSON Response (Success):
```json
{
  "name": "Welcome Template",
  "category": "onboarding",
  "language": "en",
  "channel": "sms",
  "body_text": "Hello, welcome to our service! Your account is ready.",
  "description": "A welcome template for new users",
  "status": "draft",
  "is_favorite": false
}
```

### JSON Response (Error):
```json
{
  "name": ["A template with this name already exists for sms channel."],
  "body_text": ["Body text cannot be empty."]
}
```

---

## 3. Template Detail

**Endpoint:** `GET /api/messaging/templates/{template_id}/`

**Purpose:** Get detailed information about a specific template

### JSON Response:
```json
{
  "id": "ca4403a6-f51b-48bf-8f5c-8a0921096c67",
  "name": "Test Welcome Template",
  "category": "onboarding",
  "category_display": "Onboarding",
  "language": "en",
  "language_display": "English",
  "channel": "sms",
  "channel_display": "SMS",
  "body_text": "Hello, welcome to our service! Your account is ready.",
  "formatted_body_text": "Hello, welcome to our service! Your account is ready.",
  "description": "A simple welcome template for new users",
  "variables": [],
  "status": "draft",
  "status_display": "Draft",
  "approved": false,
  "approval_status": "pending",
  "is_favorite": false,
  "wa_template_name": "",
  "wa_template_id": "",
  "usage_count": 0,
  "last_used_display": "Never used",
  "created_by": "admin@mifumo.com",
  "created_at": "2025-10-23T03:28:45.889638+03:00",
  "updated_at": "2025-10-23T03:28:45.952538+03:00"
}
```

---

## 4. Update Template

**Endpoint:** `PUT /api/messaging/templates/{template_id}/`

**Purpose:** Update an existing template

### Request Body:
```json
{
  "name": "Updated Welcome Template",
  "body_text": "Hello {{name}}, welcome to our service! Your account is ready.",
  "category": "onboarding",
  "language": "en",
  "channel": "sms",
  "description": "Updated welcome template with personalization"
}
```

### JSON Response:
```json
{
  "id": "ca4403a6-f51b-48bf-8f5c-8a0921096c67",
  "name": "Updated Welcome Template",
  "category": "onboarding",
  "language": "en",
  "channel": "sms",
  "body_text": "Hello {{name}}, welcome to our service! Your account is ready.",
  "description": "Updated welcome template with personalization",
  "status": "draft",
  "is_favorite": false,
  "updated_at": "2025-10-23T03:35:12.123456+03:00"
}
```

---

## 5. Toggle Template Favorite

**Endpoint:** `POST /api/messaging/templates/{template_id}/toggle-favorite/`

**Purpose:** Toggle favorite status of a template

### JSON Response:
```json
{
  "success": true,
  "is_favorite": true,
  "message": "Template added to favorites"
}
```

---

## 6. Increment Template Usage

**Endpoint:** `POST /api/messaging/templates/{template_id}/increment-usage/`

**Purpose:** Increment usage count for a template

### JSON Response:
```json
{
  "success": true,
  "usage_count": 1,
  "message": "Usage count updated"
}
```

---

## 7. Approve Template

**Endpoint:** `POST /api/messaging/templates/{template_id}/approve/`

**Purpose:** Approve a template for use

### JSON Response:
```json
{
  "success": true,
  "status": "approved",
  "approved": true,
  "message": "Template approved successfully"
}
```

---

## 8. Reject Template

**Endpoint:** `POST /api/messaging/templates/{template_id}/reject/`

**Purpose:** Reject a template

### JSON Response:
```json
{
  "success": true,
  "status": "rejected",
  "approved": false,
  "message": "Template rejected"
}
```

---

## Template Categories

| Value | Display Name | Description |
|-------|--------------|-------------|
| `onboarding` | Onboarding | Welcome and setup messages |
| `promotions` | Promotions | Marketing and promotional content |
| `reminders` | Reminders | Appointment and deadline reminders |
| `loyalty` | Loyalty | Customer loyalty program messages |
| `win_back` | Win-Back | Re-engagement campaigns |
| `post_purchase` | Post-Purchase | Order confirmation and follow-up |
| `authentication` | Authentication | OTP and verification codes |
| `marketing` | Marketing | General marketing messages |
| `utility` | Utility | Service notifications |
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
  language: 'en',
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
  body_text: 'Hello {{name}}, welcome to our service!',
  category: 'onboarding',
  language: 'en',
  channel: 'sms',
  description: 'Personalized welcome message'
});
```

### JavaScript - Toggle Favorite

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
```

---

## Error Responses

### 400 Bad Request
```json
{
  "name": ["A template with this name already exists for sms channel."],
  "body_text": ["Body text cannot be empty."]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "An error occurred while processing the request"
}
```
