# Bulk Import Endpoint Documentation

## Overview

The bulk import endpoint allows you to import multiple contacts into the system from various sources including CSV files, Excel files, and mobile phone contacts. This endpoint supports up to 1000 contacts per import operation.

## Endpoint Details

**URL:** `POST /api/messaging/contacts/bulk-import/`
**Authentication:** Required (JWT Bearer Token)
**Content-Type:** `application/json` or `multipart/form-data` (for file uploads)

## Request Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `import_type` | string | Type of import: `csv`, `excel`, or `phone_contacts` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `csv_data` | string | - | CSV data as string (for CSV import) |
| `file` | file | - | File upload (for Excel/CSV import) |
| `contacts` | array | - | Array of contact objects (for phone contacts) |
| `skip_duplicates` | boolean | `true` | Skip contacts that already exist |
| `update_existing` | boolean | `false` | Update existing contacts instead of skipping |

## Import Types

### 1. CSV Import

Import contacts from CSV data or uploaded CSV files.

**Request Body:**
```json
{
  "import_type": "csv",
  "csv_data": "name,phone_e164,email,tags\nJohn Doe,+255700000001,john@example.com,vip,customer\nJane Smith,+255700000002,jane@example.com,regular",
  "skip_duplicates": true,
  "update_existing": false
}
```

**CSV Format Requirements:**
- **Required columns:** `name`, `phone_e164`
- **Optional columns:** `email`, `tags` (comma-separated)
- **Additional columns:** Any other columns will be stored in `attributes`

**Example CSV:**
```csv
name,phone_e164,email,tags,company,department
John Doe,+255700000001,john@example.com,vip,customer,Acme Corp,Sales
Jane Smith,+255700000002,jane@example.com,regular,ABC Ltd,Marketing
```

### 2. Excel Import

Import contacts from Excel files (.xlsx, .xls).

**Request Body (File Upload):**
```json
{
  "import_type": "excel",
  "file": "<Excel file upload>",
  "skip_duplicates": true,
  "update_existing": false
}
```

**Supported Excel Formats:**
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

**Excel Format Requirements:**
- Same as CSV format
- First row should contain headers
- Data starts from second row

### 3. Phone Contact Import

Import contacts from mobile phone contact picker.

**Request Body:**
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

## Response Format

### Success Response (201 Created)

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

### Error Response (400 Bad Request)

```json
{
  "success": false,
  "message": "Invalid CSV format",
  "imported_count": 0,
  "errors": ["CSV parsing error: Invalid phone number format: 123"]
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the import was successful |
| `imported` | integer | Number of new contacts imported |
| `updated` | integer | Number of existing contacts updated |
| `skipped` | integer | Number of contacts skipped (duplicates) |
| `total_processed` | integer | Total number of contacts processed |
| `errors` | array | List of error messages |
| `message` | string | Human-readable summary message |

## Phone Number Format

The system automatically normalizes phone numbers to E.164 format:

- **Tanzanian numbers:** `+255XXXXXXXXX`
- **International format:** `+[country code][number]`
- **Local format:** Automatically converted to E.164

## Error Handling

The endpoint provides comprehensive error handling:

1. **File Format Errors:** Unsupported file types
2. **Data Validation Errors:** Invalid phone numbers, missing required fields
3. **CSV Parsing Errors:** Malformed CSV data
4. **Duplicate Handling:** Based on phone number matching

## Rate Limits

- **Maximum contacts per import:** 1000
- **File size limit:** 10MB
- **Rate limit:** 10 imports per minute per user

## Examples

### Example 1: CSV Import with File Upload

```bash
curl -X POST "http://127.0.0.1:8000/api/messaging/contacts/bulk-import/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "import_type=csv" \
  -F "file=@contacts.csv" \
  -F "skip_duplicates=true" \
  -F "update_existing=false"
```

### Example 2: Phone Contacts Import

```bash
curl -X POST "http://127.0.0.1:8000/api/messaging/contacts/bulk-import/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Example 3: Excel Import

```bash
curl -X POST "http://127.0.0.1:8000/api/messaging/contacts/bulk-import/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "import_type=excel" \
  -F "file=@contacts.xlsx" \
  -F "skip_duplicates=true" \
  -F "update_existing=true"
```

## Frontend Integration

### JavaScript Example

```javascript
// CSV Import
const importCSV = async (csvData) => {
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      import_type: 'csv',
      csv_data: csvData,
      skip_duplicates: true,
      update_existing: false
    })
  });

  return await response.json();
};

// File Upload Import
const importFile = async (file) => {
  const formData = new FormData();
  formData.append('import_type', 'excel');
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

// Phone Contacts Import
const importPhoneContacts = async (contacts) => {
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      import_type: 'phone_contacts',
      contacts: contacts,
      skip_duplicates: true,
      update_existing: false
    })
  });

  return await response.json();
};
```

## Testing

You can test the endpoint using the provided test files:

1. **CSV Test:** Use `test_contact_import.py`
2. **Excel Test:** Use `test_enhanced_bulk_import.py`
3. **Phone Contacts Test:** Use `test_mobile_contacts.py`

## Troubleshooting

### Common Issues

1. **"Invalid phone number format"**
   - Ensure phone numbers are in E.164 format (+255XXXXXXXXX)
   - Check for proper country code

2. **"CSV parsing error"**
   - Verify CSV format is correct
   - Check for required columns: `name`, `phone_e164`

3. **"Unsupported file format"**
   - Use only .csv, .xlsx, or .xls files
   - Check file extension

4. **"Empty CSV data provided"**
   - Ensure CSV data is not empty
   - Check file upload was successful

### Debug Mode

Enable debug mode in Django settings to see detailed error messages:

```python
DEBUG = True
```

## Related Endpoints

- `GET /api/messaging/contacts/` - List contacts
- `POST /api/messaging/contacts/` - Create single contact
- `GET /api/messaging/contacts/{id}/` - Get contact details
- `PUT /api/messaging/contacts/{id}/` - Update contact
- `DELETE /api/messaging/contacts/{id}/` - Delete contact
