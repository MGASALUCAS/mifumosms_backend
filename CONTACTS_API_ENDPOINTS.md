# Contacts API Endpoints

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

## 1. Mobile Contact Import (Direct from Phone Book)

**Endpoint:** `POST /api/messaging/contacts/import/`

**Purpose:** Import contacts directly from mobile phone book using Web Contacts API

### Frontend Implementation (Mobile Contact Picker):

```javascript
// Check if mobile contact picker is supported
const isContactPickerSupported = 
  typeof navigator !== "undefined" && 
  "contacts" in navigator && 
  typeof navigator.contacts?.select === "function";

// Function to fetch contacts from mobile device
async function fetchMobileContacts() {
  if (!isContactPickerSupported) {
    throw new Error("Mobile contact picker not supported on this device");
  }

  try {
    // Request permission and fetch contacts from mobile device
    const contacts = await navigator.contacts.select(
      ["name", "tel", "email"], 
      { multiple: true }
    );

    // Transform mobile contacts to API format
    const transformedContacts = contacts.map(contact => ({
      full_name: contact.name?.[0] || "",
      phone: contact.tel?.[0] || "",
      email: contact.email?.[0] || ""
    })).filter(contact => contact.full_name || contact.phone);

    return transformedContacts;
  } catch (error) {
    if (error.name === "NotAllowedError") {
      throw new Error("Please allow access to contacts to use this feature");
    }
    if (error.name === "AbortError") {
      throw new Error("Contact selection was cancelled");
    }
    throw error;
  }
}

// Import contacts to backend
async function importMobileContacts(contacts) {
  const response = await fetch('/api/messaging/contacts/import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contacts: contacts
    })
  });

  return await response.json();
}

// Complete mobile contact import flow
async function handleMobileContactImport() {
  try {
    const mobileContacts = await fetchMobileContacts();
    const result = await importMobileContacts(mobileContacts);
    console.log('Import result:', result);
    return result;
  } catch (error) {
    console.error('Mobile contact import failed:', error);
    throw error;
  }
}
```

### Request Body:
```json
{
  "contacts": [
    {
      "full_name": "John Mkumbo",
      "phone": "+255672883530",
      "email": "john@example.com"
    },
    {
      "full_name": "Fatma Mbwana",
      "phone": "+255771978307",
      "email": "fatma@example.com"
    }
  ]
}
```

### JSON Response (Success):
```json
{
  "imported": 2,
  "skipped": 0,
  "total_processed": 2,
  "errors": [],
  "message": "Successfully imported 2 contacts"
}
```

### JSON Response (With Duplicates):
```json
{
  "imported": 0,
  "skipped": 2,
  "total_processed": 2,
  "errors": [],
  "message": "Successfully imported 0 contacts"
}
```

---

## 2. Bulk Contact Import (CSV/Excel)

**Endpoint:** `POST /api/messaging/contacts/bulk-import/`

**Purpose:** Import contacts from CSV or Excel files

### Request Body (CSV):
```json
{
  "import_type": "csv",
  "csv_data": "name,phone,local_number,email,tags\nJohn Mkumbo,+255672883530,672883530,john@example.com,vip\nFatma Mbwana,+255771978307,771978307,fatma@example.com,customer",
  "skip_duplicates": true,
  "update_existing": false
}
```

### Request Body (Excel):
```json
{
  "import_type": "excel",
  "csv_data": "name,phone,local_number,email,tags\nJohn Mkumbo,+255672883530,672883530,john@example.com,vip\nFatma Mbwana,+255771978307,771978307,fatma@example.com,customer",
  "skip_duplicates": true,
  "update_existing": false
}
```

### JSON Response:
```json
{
  "success": true,
  "imported": 2,
  "updated": 0,
  "skipped": 0,
  "total_processed": 2,
  "errors": [],
  "message": "Successfully imported 2, updated 0, skipped 0 contacts"
}
```

---

## 3. Contact List

**Endpoint:** `GET /api/messaging/contacts/`

**Purpose:** Get list of all contacts for the current tenant

### JSON Response:
```json
{
  "count": 301,
  "next": "http://127.0.0.1:8001/api/messaging/contacts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "0a770470-2d1a-492e-bb50-28103d17d946",
      "name": "Joseph Mtega",
      "phone_e164": "+255772955046",
      "email": "",
      "attributes": {},
      "tags": [],
      "opt_in_at": null,
      "opt_out_at": null,
      "opt_out_reason": "",
      "is_active": true,
      "last_contacted_at": null,
      "is_opted_in": null,
      "created_by": "admin@mifumo.com",
      "created_by_id": 2,
      "created_at": "2025-10-23T02:12:04.079222+03:00",
      "updated_at": "2025-10-23T02:12:04.079222+03:00"
    }
  ]
}
```

---

## 4. Create Single Contact

**Endpoint:** `POST /api/messaging/contacts/`

**Purpose:** Create a single contact

### Request Body:
```json
{
  "name": "John Mkumbo",
  "phone_e164": "+255672883530",
  "email": "john@example.com",
  "tags": ["vip", "customer"]
}
```

### JSON Response:
```json
{
  "id": "e9080f75-a862-4e8c-af4d-173d8503bf0f",
  "name": "John Mkumbo",
  "phone_e164": "+255672883530",
  "email": "john@example.com",
  "attributes": {},
  "tags": ["vip", "customer"],
  "opt_in_at": null,
  "opt_out_at": null,
  "opt_out_reason": "",
  "is_active": true,
  "last_contacted_at": null,
  "is_opted_in": null,
  "created_by": "admin@mifumo.com",
  "created_by_id": 2,
  "created_at": "2025-10-23T01:46:58.232919+03:00",
  "updated_at": "2025-10-23T01:46:58.232919+03:00"
}
```

---

## 5. Contact Detail

**Endpoint:** `GET /api/messaging/contacts/{contact_id}/`

**Purpose:** Get specific contact details

### JSON Response:
```json
{
  "id": "3f83f7dd-d09c-454a-8fdc-36de7967546d",
  "name": "Mgasa Engineer",
  "phone_e164": "+255689726060",
  "email": "admin@example.com",
  "attributes": {
    "company": "Quantum Intelligence",
    "department": ""
  },
  "tags": ["vip"],
  "opt_in_at": null,
  "opt_out_at": null,
  "opt_out_reason": "",
  "is_active": true,
  "last_contacted_at": null,
  "is_opted_in": null,
  "created_by": "admin@mifumo.com",
  "created_by_id": 2,
  "created_at": "2025-10-22T23:06:30.072215+03:00",
  "updated_at": "2025-10-22T23:08:05.129219+03:00"
}
```

---

## 6. Update Contact

**Endpoint:** `PUT /api/messaging/contacts/{contact_id}/`

**Purpose:** Update a specific contact

### Request Body:
```json
{
  "name": "John Mkumbo Updated",
  "phone_e164": "+255672883530",
  "email": "john.updated@example.com",
  "tags": ["vip", "customer", "updated"]
}
```

### JSON Response:
```json
{
  "id": "e9080f75-a862-4e8c-af4d-173d8503bf0f",
  "name": "John Mkumbo Updated",
  "phone_e164": "+255672883530",
  "email": "john.updated@example.com",
  "attributes": {},
  "tags": ["vip", "customer", "updated"],
  "opt_in_at": null,
  "opt_out_at": null,
  "opt_out_reason": "",
  "is_active": true,
  "last_contacted_at": null,
  "is_opted_in": null,
  "created_by": "admin@mifumo.com",
  "created_by_id": 2,
  "created_at": "2025-10-23T01:46:58.232919+03:00",
  "updated_at": "2025-10-23T02:15:30.123456+03:00"
}
```

---

## 7. Delete Contact

**Endpoint:** `DELETE /api/messaging/contacts/{contact_id}/`

**Purpose:** Delete a specific contact

### JSON Response:
```json
{
  "message": "Contact deleted successfully"
}
```

---

## Mobile Contact Picker Requirements

### Browser Support:
- **Chrome on Android** (recommended)
- **Edge on Android**
- **Samsung Internet on Android**

### Required Permissions:
- User must grant contact access permission
- Works only on mobile devices with contact picker support

### Frontend Integration:
1. Check if `navigator.contacts.select` is available
2. Request contact access permission
3. Use `navigator.contacts.select()` to fetch contacts
4. Transform contact data to API format
5. Send to backend import endpoint

### Error Handling:
- **NotAllowedError**: User denied contact access
- **AbortError**: User cancelled contact selection
- **NotSupportedError**: Browser doesn't support contact picker

---

## CSV/Excel Format Requirements

### CSV Format:
- **Required columns:** `name`, `phone`
- **Optional columns:** `local_number`, `email`, `tags`
- **Phone format:** E.164 format (+255XXXXXXXXX) or local format (0XXXXXXXXX)
- **Tags:** Comma-separated values

### Excel Format:
- **File types:** `.xlsx`, `.xls`
- **Same column structure as CSV**
- **First row must contain headers**

---

## Error Responses

### 400 Bad Request
```json
{
  "contacts": [
    "Contact 1: At least one field (name, phone, or email) is required"
  ]
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
  "message": "Error processing contacts",
  "imported_count": 0,
  "errors": ["Database error occurred"]
}
```
