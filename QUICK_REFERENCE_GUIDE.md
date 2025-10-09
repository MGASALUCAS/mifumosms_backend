# Quick Reference Guide - Campaign & Contact Management

## 🚀 Most Common Operations

### 1. Create a New Campaign
```bash
POST /api/messaging/campaigns/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Welcome Campaign",
  "campaign_type": "sms",
  "message_text": "Welcome to our service!",
  "target_contact_ids": ["contact-uuid-1", "contact-uuid-2"]
}
```

### 2. Add a New Contact
```bash
POST /api/messaging/contacts/
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "John Doe",
  "phone_e164": "+255123456789",
  "email": "john@example.com"
}
```

### 3. Start a Campaign
```bash
POST /api/messaging/campaigns/{campaign-id}/start/
Authorization: Bearer <token>
```

### 4. Get All User's Campaigns
```bash
GET /api/messaging/campaigns/
Authorization: Bearer <token>
```

### 5. Get All User's Contacts
```bash
GET /api/messaging/contacts/
Authorization: Bearer <token>
```

## 📱 Frontend Integration Checklist

### ✅ Required API Endpoints
- [ ] `GET /api/messaging/contacts/` - List contacts
- [ ] `POST /api/messaging/contacts/` - Create contact
- [ ] `PUT /api/messaging/contacts/{id}/` - Update contact
- [ ] `DELETE /api/messaging/contacts/{id}/` - Delete contact
- [ ] `GET /api/messaging/campaigns/` - List campaigns
- [ ] `POST /api/messaging/campaigns/` - Create campaign
- [ ] `GET /api/messaging/campaigns/{id}/` - Get campaign details
- [ ] `PUT /api/messaging/campaigns/{id}/` - Update campaign
- [ ] `DELETE /api/messaging/campaigns/{id}/` - Delete campaign
- [ ] `POST /api/messaging/campaigns/{id}/start/` - Start campaign
- [ ] `POST /api/messaging/campaigns/{id}/pause/` - Pause campaign
- [ ] `POST /api/messaging/campaigns/{id}/cancel/` - Cancel campaign
- [ ] `GET /api/messaging/campaigns/summary/` - Get campaign summary

### ✅ Key Features to Implement
- [ ] Contact management (CRUD operations)
- [ ] Campaign creation with targeting
- [ ] Campaign status management (start/pause/cancel)
- [ ] Real-time campaign progress tracking
- [ ] Campaign analytics dashboard
- [ ] Contact import/export functionality
- [ ] Search and filtering for contacts and campaigns

### ✅ UI Components Needed
- [ ] Contact list with search/filter
- [ ] Contact form (create/edit)
- [ ] Campaign list with status indicators
- [ ] Campaign creation wizard
- [ ] Campaign analytics charts
- [ ] Contact selection for campaigns
- [ ] Campaign action buttons (start/pause/cancel)

## 🔧 Testing Endpoints

### Test Contact Creation
```bash
curl -X POST http://localhost:8000/api/messaging/contacts/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "phone_e164": "+255123456789",
    "email": "test@example.com"
  }'
```

### Test Campaign Creation
```bash
curl -X POST http://localhost:8000/api/messaging/campaigns/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Campaign",
    "campaign_type": "sms",
    "message_text": "This is a test message",
    "target_contact_ids": ["CONTACT_UUID_HERE"]
  }'
```

## 📊 Data Models Summary

### Contact
- `id`: UUID
- `name`: String
- `phone_e164`: String (E.164 format)
- `email`: String (optional)
- `is_active`: Boolean
- `is_opted_in`: Boolean
- `created_at`: DateTime

### Campaign
- `id`: UUID
- `name`: String
- `campaign_type`: String (sms, whatsapp, email, mixed)
- `message_text`: String
- `status`: String (draft, scheduled, running, paused, completed, cancelled, failed)
- `total_recipients`: Integer
- `sent_count`: Integer
- `delivered_count`: Integer
- `read_count`: Integer
- `progress_percentage`: Integer (0-100)
- `created_by`: UUID (user ID)

## 🎯 Campaign Status Flow

```
Draft → Scheduled → Running → Completed
  ↓        ↓         ↓
Cancelled  Cancelled  Paused
  ↓        ↓         ↓
           Cancelled  Running
```

## 📞 Phone Number Format
Always use E.164 format: `+255123456789`
- Country code: +255 (Tanzania)
- No spaces or special characters
- Include the + sign

## 🕐 Date Format
Use ISO 8601 format: `2024-01-01T10:00:00Z`
- Always include timezone (Z for UTC)
- Format: YYYY-MM-DDTHH:MM:SSZ

## 🔐 Authentication
- All requests require JWT token
- Include in Authorization header: `Bearer <token>`
- Token expires after 24 hours (configurable)

## 🚨 Common Errors
- `400 Bad Request`: Validation errors (check `errors` field)
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server error

## 📈 Performance Tips
- Use pagination for large lists
- Implement search/filtering on frontend
- Cache campaign summary data
- Use WebSockets for real-time updates
- Implement optimistic UI updates

This quick reference should help with the most common integration tasks!
