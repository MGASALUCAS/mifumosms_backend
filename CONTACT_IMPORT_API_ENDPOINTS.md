# Contact Import API Endpoints

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

## 1. Bulk Contact Import

**Endpoint:** `POST /api/messaging/contacts/bulk-import/`

**Purpose:** Import multiple contacts from CSV, Excel, or mobile phone book

### Request Body Options:

#### Option A: CSV Import
```json
{
  "import_type": "csv",
  "csv_data": "name,phone,local_number,email,tags\nJohn Mkumbo,+255672883530,672883530,john@example.com,vip\nFatma Mbwana,+255771978307,771978307,fatma@example.com,customer",
  "skip_duplicates": true,
  "update_existing": false
}
```

#### Option B: Excel Import
```json
{
  "import_type": "excel",
  "csv_data": "name,phone,local_number,email,tags\nJohn Mkumbo,+255672883530,672883530,john@example.com,vip\nFatma Mbwana,+255771978307,771978307,fatma@example.com,customer",
  "skip_duplicates": true,
  "update_existing": false
}
```

#### Option C: Mobile Phone Book Import
```json
{
  "import_type": "phone_contacts",
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
  ],
  "skip_duplicates": true,
  "update_existing": false
}
```

### CSV/Excel Format (Required Columns):
```csv
name,phone,local_number,email,tags
John Mkumbo,+255672883530,672883530,john@example.com,vip
Fatma Mbwana,+255771978307,771978307,fatma@example.com,customer
Juma Shaaban,+255601709528,601709528,juma@example.com,regular
Gloria Kimaro,+255754865908,754865908,gloria@example.com,vip
Hassan Ndallahwa,+255766684630,766684630,hassan@example.com,customer
```

### JSON Response (Success):
```json
{
  "success": true,
  "imported": 5,
  "updated": 0,
  "skipped": 0,
  "total_processed": 5,
  "errors": [],
  "message": "Successfully imported 5, updated 0, skipped 0 contacts"
}
```

### JSON Response (With Duplicates):
```json
{
  "success": true,
  "imported": 0,
  "updated": 0,
  "skipped": 5,
  "total_processed": 5,
  "errors": [],
  "message": "Successfully imported 0, updated 0, skipped 5 contacts"
}
```

### JSON Response (Error):
```json
{
  "success": false,
  "message": "Invalid CSV format",
  "imported_count": 0,
  "errors": ["CSV parsing error: Invalid phone number format: 123"]
}
```

---

## 2. Contact List

**Endpoint:** `GET /api/messaging/contacts/`

**Purpose:** Get list of all contacts for the current tenant

### JSON Response:
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "e9080f75-a862-4e8c-af4d-173d8503bf0f",
      "name": "Hassan Ndallahwa",
      "phone_e164": "+255766684630",
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
      "created_at": "2025-10-23T01:46:58.232919+03:00",
      "updated_at": "2025-10-23T01:46:58.232919+03:00"
    },
    {
      "id": "0bbb63f5-b9fe-4f9d-8da6-10dee0903d4b",
      "name": "Gloria Kimaro",
      "phone_e164": "+255754865908",
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
      "created_at": "2025-10-23T01:46:58.132045+03:00",
      "updated_at": "2025-10-23T01:46:58.132045+03:00"
    }
  ]
}
```

---

## 3. Contact Detail

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

## Supported File Formats

### CSV Format
- **Required columns:** `name`, `phone`
- **Optional columns:** `local_number`, `email`, `tags`
- **Phone format:** E.164 format (+255XXXXXXXXX) or local format (0XXXXXXXXX)
- **Tags:** Comma-separated values

### Excel Format
- **File types:** `.xlsx`, `.xls`
- **Same column structure as CSV**
- **First row must contain headers**

### Mobile Phone Book Format
- **Required fields:** `full_name`, `phone`
- **Optional fields:** `email`
- **Phone format:** Any format (automatically normalized to E.164)

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Unsupported file format. Please use CSV or Excel files.",
  "imported_count": 0,
  "errors": ["Unsupported file format"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Error reading file",
  "imported_count": 0,
  "errors": ["File reading error: Invalid file format"]
}
```
