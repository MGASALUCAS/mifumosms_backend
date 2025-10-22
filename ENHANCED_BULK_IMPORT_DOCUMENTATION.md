# Enhanced Bulk Import Documentation

## Overview

The bulk import functionality has been enhanced to support both **CSV/Excel files** and **phone contact picker** data through a unified endpoint. This provides maximum flexibility for importing contacts from various sources.

## Endpoint

**POST** `/api/messaging/contacts/bulk-import/`

## Features

- ✅ **CSV Import** - Import from CSV data or uploaded CSV files
- ✅ **Excel Import** - Import from Excel files (.xlsx, .xls)
- ✅ **Phone Contact Import** - Import from phone contact picker
- ✅ **Duplicate Handling** - Skip or update existing contacts
- ✅ **Phone Number Normalization** - Automatic Tanzanian phone number formatting
- ✅ **Error Handling** - Comprehensive error reporting
- ✅ **Bulk Operations** - Import up to 1000 contacts at once

---

## Import Types

### 1. CSV Import

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
      "phone": "255700000002",
      "email": "jane@example.com"
    }
  ],
  "skip_duplicates": true,
  "update_existing": false
}
```

**Phone Contact Format:**
- `full_name` - Contact's full name
- `phone` - Phone number (will be normalized to E.164 format)
- `email` - Email address (optional)

---

## Import Options

### Duplicate Handling

**`skip_duplicates` (boolean, default: true)**
- `true` - Skip contacts that already exist (based on phone number)
- `false` - Allow duplicate contacts

**`update_existing` (boolean, default: false)**
- `true` - Update existing contacts with new data
- `false` - Skip existing contacts (only works when `skip_duplicates` is true)

### Import Type

**`import_type` (string, choices: ['csv', 'excel', 'phone_contacts'])**
- `csv` - Import from CSV data
- `excel` - Import from Excel file
- `phone_contacts` - Import from phone contact picker

---

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Successfully imported 5, updated 2, skipped 1 contacts",
  "imported": 5,
  "updated": 2,
  "skipped": 1,
  "total_processed": 8,
  "errors": []
}
```

### Error Response

```json
{
  "success": false,
  "message": "Imported 3, updated 1, skipped 2 contacts with 2 errors",
  "imported": 3,
  "updated": 1,
  "skipped": 2,
  "total_processed": 6,
  "errors": [
    "Row 4: Invalid phone number format",
    "Contact 5: Email validation failed"
  ]
}
```

---

## Phone Number Normalization

The system automatically normalizes phone numbers to E.164 format:

**Tanzanian Numbers:**
- `255700000001` → `+255700000001`
- `0700000001` → `+255700000001`
- `+255700000001` → `+255700000001` (unchanged)

**Other Numbers:**
- `1234567890` → `+1234567890`
- `+1234567890` → `+1234567890` (unchanged)

---

## Frontend Integration Examples

### JavaScript - CSV Import

```javascript
const importCSVContacts = async (csvData) => {
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      import_type: 'csv',
      csv_data: csvData,
      skip_duplicates: true,
      update_existing: false
    })
  });
  
  const result = await response.json();
  console.log(`Imported: ${result.imported}, Updated: ${result.updated}, Skipped: ${result.skipped}`);
  return result;
};
```

### JavaScript - File Upload (Excel)

```javascript
const importExcelFile = async (file) => {
  const formData = new FormData();
  formData.append('import_type', 'excel');
  formData.append('file', file);
  formData.append('skip_duplicates', 'true');
  formData.append('update_existing', 'false');
  
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`
    },
    body: formData
  });
  
  const result = await response.json();
  return result;
};
```

### JavaScript - Phone Contact Import

```javascript
const importPhoneContacts = async (contacts) => {
  const response = await fetch('/api/messaging/contacts/bulk-import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      import_type: 'phone_contacts',
      contacts: contacts,
      skip_duplicates: true,
      update_existing: false
    })
  });
  
  const result = await response.json();
  return result;
};
```

### React Component Example

```jsx
import React, { useState } from 'react';

const ContactImport = () => {
  const [importType, setImportType] = useState('csv');
  const [csvData, setCsvData] = useState('');
  const [phoneContacts, setPhoneContacts] = useState([]);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleImport = async () => {
    let data = {
      import_type: importType,
      skip_duplicates: true,
      update_existing: false
    };

    if (importType === 'csv') {
      data.csv_data = csvData;
    } else if (importType === 'excel') {
      // Handle file upload
      const formData = new FormData();
      formData.append('import_type', 'excel');
      formData.append('file', file);
      formData.append('skip_duplicates', 'true');
      formData.append('update_existing', 'false');
      
      const response = await fetch('/api/messaging/contacts/bulk-import/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` },
        body: formData
      });
      
      setResult(await response.json());
      return;
    } else if (importType === 'phone_contacts') {
      data.contacts = phoneContacts;
    }

    const response = await fetch('/api/messaging/contacts/bulk-import/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    setResult(await response.json());
  };

  return (
    <div>
      <h2>Import Contacts</h2>
      
      <div>
        <label>
          Import Type:
          <select value={importType} onChange={(e) => setImportType(e.target.value)}>
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
            <option value="phone_contacts">Phone Contacts</option>
          </select>
        </label>
      </div>

      {importType === 'csv' && (
        <div>
          <label>
            CSV Data:
            <textarea 
              value={csvData} 
              onChange={(e) => setCsvData(e.target.value)}
              placeholder="name,phone_e164,email,tags&#10;John Doe,+255700000001,john@example.com,vip"
              rows={10}
              cols={50}
            />
          </label>
        </div>
      )}

      {importType === 'excel' && (
        <div>
          <label>
            Excel File:
            <input 
              type="file" 
              accept=".xlsx,.xls"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </label>
        </div>
      )}

      {importType === 'phone_contacts' && (
        <div>
          <label>
            Phone Contacts (JSON):
            <textarea 
              value={JSON.stringify(phoneContacts, null, 2)} 
              onChange={(e) => setPhoneContacts(JSON.parse(e.target.value))}
              rows={10}
              cols={50}
            />
          </label>
        </div>
      )}

      <button onClick={handleImport}>Import Contacts</button>

      {result && (
        <div>
          <h3>Import Result</h3>
          <p>Imported: {result.imported}</p>
          <p>Updated: {result.updated}</p>
          <p>Skipped: {result.skipped}</p>
          <p>Total Processed: {result.total_processed}</p>
          {result.errors.length > 0 && (
            <div>
              <h4>Errors:</h4>
              <ul>
                {result.errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ContactImport;
```

---

## Error Handling

### Common Errors

1. **Invalid CSV Format**
   ```json
   {
     "success": false,
     "message": "Invalid CSV format",
     "errors": ["CSV parsing error: line 2: expected 3 fields, got 2"]
   }
   ```

2. **Missing Required Fields**
   ```json
   {
     "success": false,
     "message": "Validation failed",
     "errors": ["Missing required field: phone_e164"]
   }
   ```

3. **Invalid Phone Number**
   ```json
   {
     "success": false,
     "message": "Import completed with errors",
     "errors": ["Row 3: Invalid phone number format"]
   }
   ```

4. **File Upload Error**
   ```json
   {
     "success": false,
     "message": "Error reading file",
     "errors": ["File reading error: Unsupported file format"]
   }
   ```

---

## Performance Considerations

- **Batch Size**: Recommended maximum 1000 contacts per import
- **File Size**: Excel files up to 10MB supported
- **Memory Usage**: Large imports are processed in chunks
- **Timeout**: 30-second timeout for large imports

---

## Security Features

- **Authentication Required**: JWT token required
- **User Isolation**: Users can only import to their own contact list
- **Input Validation**: All inputs are validated and sanitized
- **File Type Validation**: Only CSV and Excel files allowed
- **Phone Number Validation**: Automatic phone number format validation

---

## Testing

### Test Scripts

1. **Comprehensive Test**: `test_bulk_operations.py`
2. **Simple Test**: `test_new_endpoints.py`

### Running Tests

```bash
# Install dependencies
pip install pandas openpyxl

# Run comprehensive tests
python test_bulk_operations.py

# Run simple tests
python test_new_endpoints.py
```

---

## Migration from Old Endpoints

The old separate endpoints are still available for backward compatibility:

- **CSV Import**: `POST /api/messaging/contacts/bulk-import/` (old format)
- **Phone Import**: `POST /api/messaging/contacts/import/`

**Recommended**: Use the new unified endpoint for all bulk import operations.

---

## Summary

The enhanced bulk import functionality provides:

✅ **Unified Interface** - Single endpoint for all import types
✅ **Multiple Formats** - CSV, Excel, and phone contacts
✅ **Smart Duplicate Handling** - Skip or update existing contacts
✅ **Phone Number Normalization** - Automatic Tanzanian number formatting
✅ **Comprehensive Error Handling** - Detailed error reporting
✅ **Frontend Ready** - Easy integration with React/Vue/Angular
✅ **Backward Compatible** - Old endpoints still work
✅ **Production Ready** - Tested and documented

This implementation provides maximum flexibility for importing contacts from any source while maintaining data integrity and user experience.
