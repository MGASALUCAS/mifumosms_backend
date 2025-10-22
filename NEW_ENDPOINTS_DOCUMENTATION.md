# New Endpoints Documentation

This document describes the new endpoints implemented for bulk operations, user profile settings, and password reset functionality.

## Table of Contents

1. [Bulk Contact Operations](#bulk-contact-operations)
2. [User Profile Settings](#user-profile-settings)
3. [Password Reset](#password-reset)
4. [Testing](#testing)

---

## Bulk Contact Operations

### 1. Bulk Edit Contacts

**Endpoint:** `POST /api/messaging/contacts/bulk-edit/`

**Description:** Update multiple contacts at once with the same changes.

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "contact_ids": ["uuid1", "uuid2", "uuid3"],
  "updates": {
    "name": "Updated Name",
    "email": "updated@example.com",
    "tags": ["tag1", "tag2"],
    "attributes": {
      "company": "New Company"
    },
    "is_active": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully updated 3 contacts",
  "updated_count": 3,
  "total_requested": 3
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Some contacts not found: ['uuid1']",
  "updated_count": 0
}
```

### 2. Bulk Delete Contacts

**Endpoint:** `POST /api/messaging/contacts/bulk-delete/`

**Description:** Delete multiple contacts at once.

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "contact_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully deleted 3 contacts",
  "deleted_count": 3,
  "total_requested": 3
}
```

### 3. Phone Contact Import (Enhanced)

**Endpoint:** `POST /api/messaging/contacts/import/`

**Description:** Import contacts from phone contact picker with automatic phone number normalization.

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "contacts": [
    {
      "full_name": "John Doe",
      "phone": "+255700000100",
      "email": "john@example.com"
    },
    {
      "full_name": "Jane Smith",
      "phone": "255700000101",
      "email": "jane@example.com"
    }
  ]
}
```

**Response:**
```json
{
  "imported": 2,
  "skipped": 0,
  "total_processed": 2,
  "errors": [],
  "message": "Successfully imported 2 contacts"
}
```

---

## User Profile Settings

Based on the settings page screenshot, these endpoints provide comprehensive user profile management.

### 1. Profile Information

**Endpoint:** `GET/PUT/PATCH /api/accounts/settings/profile/`

**Description:** Manage personal information (first name, last name, phone number).

**Authentication:** Required (JWT Token)

**GET Response:**
```json
{
  "success": true,
  "data": {
    "first_name": "Admin",
    "last_name": "User",
    "phone_number": "+255700000001"
  }
}
```

**PUT/PATCH Request:**
```json
{
  "first_name": "Updated First",
  "last_name": "Updated Last",
  "phone_number": "+255700000999"
}
```

**PUT/PATCH Response:**
```json
{
  "success": true,
  "message": "Profile settings updated successfully",
  "data": {
    "first_name": "Updated First",
    "last_name": "Updated Last",
    "phone_number": "+255700000999"
  }
}
```

### 2. Preferences

**Endpoint:** `GET/PUT/PATCH /api/accounts/settings/preferences/`

**Description:** Manage language, timezone, and display settings.

**Authentication:** Required (JWT Token)

**GET Response:**
```json
{
  "success": true,
  "data": {
    "timezone": "UTC"
  }
}
```

**PUT/PATCH Request:**
```json
{
  "timezone": "Africa/Dar_es_Salaam"
}
```

### 3. Notifications

**Endpoint:** `GET/PUT/PATCH /api/accounts/settings/notifications/`

**Description:** Manage email and push notification preferences.

**Authentication:** Required (JWT Token)

**GET Response:**
```json
{
  "success": true,
  "data": {
    "email_notifications": true,
    "sms_notifications": false
  }
}
```

**PUT/PATCH Request:**
```json
{
  "email_notifications": true,
  "sms_notifications": true
}
```

### 4. Security

**Endpoint:** `GET/PUT/PATCH /api/accounts/settings/security/`

**Description:** Manage password and 2FA settings (2FA for future implementation).

**Authentication:** Required (JWT Token)

**GET Response:**
```json
{
  "success": true,
  "data": {
    "has_password": true,
    "is_verified": true,
    "last_login_at": "2024-01-15T10:30:00Z",
    "two_factor_enabled": false,
    "api_key_configured": true
  }
}
```

---

## Password Reset

### 1. Forgot Password

**Endpoint:** `POST /api/accounts/forgot-password/`

**Description:** Request a password reset email.

**Authentication:** Not Required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset email sent successfully. Please check your inbox and follow the instructions.",
  "email": "user@example.com"
}
```

### 2. Password Reset Request (Alternative)

**Endpoint:** `POST /api/accounts/password/reset/`

**Description:** Alternative endpoint for password reset request.

**Authentication:** Not Required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

### 3. Password Reset Confirm

**Endpoint:** `POST /api/accounts/password/reset/confirm/`

**Description:** Confirm password reset with token and new password.

**Authentication:** Not Required

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password reset successfully. You can now log in with your new password.",
  "user": {
    "email": "user@example.com",
    "first_name": "User",
    "last_name": "Name"
  }
}
```

---

## Testing

### Test Scripts

1. **Comprehensive Test:** `test_bulk_operations.py`
   - Tests all bulk operations
   - Tests user profile settings
   - Tests password reset functionality

2. **Simple Test:** `test_new_endpoints.py`
   - Quick verification of all new endpoints
   - Basic functionality testing

### Running Tests

```bash
# Make sure the Django server is running
python manage.py runserver

# Run comprehensive tests
python test_bulk_operations.py

# Run simple tests
python test_new_endpoints.py
```

### Test Coverage

- ✅ Bulk edit contacts
- ✅ Bulk delete contacts
- ✅ Phone contact import
- ✅ User profile settings (GET/PUT)
- ✅ User preferences (GET/PUT)
- ✅ User notifications (GET/PUT)
- ✅ User security (GET)
- ✅ Password reset flow
- ✅ Error handling
- ✅ Authentication

---

## Frontend Integration

### Settings Page Structure

The endpoints are designed to match the settings page structure shown in the screenshot:

1. **Profile** - `/api/accounts/settings/profile/`
2. **Preferences** - `/api/accounts/settings/preferences/`
3. **Notifications** - `/api/accounts/settings/notifications/`
4. **Security** - `/api/accounts/settings/security/`
5. **API & Webhooks** - Future implementation
6. **Team** - Future implementation
7. **Billing** - Already implemented

### Contact Management

- **Bulk Import** - `/api/messaging/contacts/import/` (phone picker)
- **Bulk Edit** - `/api/messaging/contacts/bulk-edit/`
- **Bulk Delete** - `/api/messaging/contacts/bulk-delete/`
- **CSV Import** - `/api/messaging/contacts/bulk-import/` (existing)

---

## Error Handling

All endpoints include comprehensive error handling:

- **400 Bad Request** - Invalid input data
- **401 Unauthorized** - Missing or invalid authentication
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server errors

Error responses follow a consistent format:

```json
{
  "success": false,
  "message": "Error description",
  "error": "Error code or details"
}
```

---

## Security Considerations

1. **Authentication Required** - All profile and bulk operation endpoints require JWT authentication
2. **User Isolation** - Users can only access their own data
3. **Input Validation** - All inputs are validated and sanitized
4. **Rate Limiting** - Bulk operations are limited to prevent abuse
5. **Token Expiration** - Password reset tokens expire after 1 hour
6. **Email Verification** - Password reset requires email verification

---

## Future Enhancements

1. **2FA Support** - Security endpoint ready for two-factor authentication
2. **API & Webhooks** - Settings page placeholder for future implementation
3. **Team Management** - Settings page placeholder for future implementation
4. **Advanced Bulk Operations** - More sophisticated bulk editing options
5. **Contact Validation** - Enhanced phone number and email validation
