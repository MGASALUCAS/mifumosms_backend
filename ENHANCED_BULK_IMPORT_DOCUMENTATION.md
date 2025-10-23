# Enhanced Bulk Import Documentation

## 🚀 Overview

The bulk import functionality has been significantly enhanced to support flexible phone number formats and CSV column names. The system now automatically converts various phone number formats to E.164 standard and intelligently maps different column name variations.

## 📱 Enhanced Phone Number Support

### Supported Phone Number Formats

The system now supports a wide variety of phone number formats and automatically converts them to E.164 format:

#### Tanzanian Numbers
- `0712345678` → `+255712345678` (Local with 0)
- `712345678` → `+255712345678` (Local without 0)
- `255712345678` → `+255712345678` (International without +)
- `+255712345678` → `+255712345678` (Already E.164)
- `0712 345 678` → `+255712345678` (With spaces)
- `0712-345-678` → `+255712345678` (With dashes)
- `(0712) 345-678` → `+255712345678` (With parentheses)

#### Other East African Countries
- `254712345678` → `+254712345678` (Kenya)
- `256712345678` → `+256712345678` (Uganda)
- `250712345678` → `+250712345678` (Rwanda)
- `257712345678` → `+257712345678` (Burundi)

### Phone Number Normalization Features

1. **Automatic Country Detection**: Uses the `phonenumbers` library to detect country codes
2. **Format Cleaning**: Removes spaces, dashes, and parentheses
3. **Validation**: Ensures phone numbers are valid for their respective countries
4. **Fallback Handling**: Manual normalization for edge cases
5. **Error Reporting**: Clear error messages for invalid formats

## 📊 Flexible CSV Column Support

### Supported Column Name Variations

The system now intelligently maps various column name variations to standard fields:

#### Name Field Variations
- `name`, `full_name`, `fullname`
- `contact_name`, `first_name`, `last_name`

#### Phone Field Variations
- `phone`, `phone_number`, `phone_e164`
- `mobile`, `mobile_number`
- `tel`, `telephone`

#### Email Field Variations
- `email`, `email_address`, `e_mail`

### Column Mapping Examples

| Original Column | Mapped To | Example |
|----------------|-----------|---------|
| `Full Name` | `name` | `John Doe` |
| `Phone Number` | `phone` | `0712345678` |
| `Email Address` | `email` | `john@example.com` |
| `contact_name` | `name` | `Jane Smith` |
| `mobile_number` | `phone` | `0712345679` |
| `e_mail` | `email` | `jane@example.com` |

## 📈 Excel File Support

### Supported Excel Formats
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)

### Excel Processing
1. **Automatic Detection**: File extension determines processing method
2. **Pandas Integration**: Uses pandas for robust Excel reading
3. **Column Mapping**: Same flexible column mapping as CSV
4. **Format Conversion**: Automatically converts to CSV for processing

## 🔧 API Endpoints

### Bulk Import Endpoint

**URL:** `POST /api/messaging/contacts/bulk-import/`

**Authentication:** Required (JWT Bearer Token)

**Request Body:**
```json
{
  "import_type": "csv",
  "csv_data": "name,phone\nJohn Doe,0712345678\nJane Smith,0712345679",
  "skip_duplicates": true,
  "update_existing": false
}
```

**File Upload:**
```json
{
  "import_type": "excel",
  "file": "<file_upload>",
  "skip_duplicates": true,
  "update_existing": false
}
```

### Response Format

**Success Response (201):**
```json
{
  "success": true,
  "message": "Successfully imported 2, updated 0, skipped 0 contacts",
  "imported_count": 2,
  "updated_count": 0,
  "skipped_count": 0,
  "errors": []
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Invalid CSV format",
  "imported_count": 0,
  "errors": [
    "Row 2: Invalid phone number format: invalid_phone",
    "Row 3: Missing name field"
  ]
}
```

## 📋 CSV Format Examples

### Minimal Format
```csv
name,phone
John Doe,0712345678
Jane Smith,0712345679
```

### With Email
```csv
name,phone,email
John Doe,0712345678,john@example.com
Jane Smith,0712345679,jane@example.com
```

### Flexible Column Names
```csv
Full Name,Phone Number,Email Address
John Doe,0712345678,john@example.com
Jane Smith,0712345679,jane@example.com
```

### Mixed Case Columns
```csv
NAME,PHONE_NUMBER,EMAIL
John Doe,0712345678,john@example.com
Jane Smith,0712345679,jane@example.com
```

## 🛠️ Technical Implementation

### Phone Number Normalization

The system uses a multi-layered approach:

1. **Primary**: `phonenumbers` library for international validation
2. **Fallback**: Manual pattern matching for Tanzanian numbers
3. **Cleaning**: Regex-based format cleaning
4. **Validation**: Country-specific number validation

### Column Mapping Algorithm

```python
def _map_csv_columns(self, columns):
    column_mapping = {}

    # Define variation patterns
    name_variations = ['name', 'full_name', 'fullname', 'contact_name']
    phone_variations = ['phone', 'phone_number', 'mobile', 'mobile_number']
    email_variations = ['email', 'email_address', 'e_mail']

    # Map columns using case-insensitive matching
    for col in columns:
        col_lower = col.lower().strip()
        if any(var in col_lower for var in name_variations):
            column_mapping[col] = 'name'
        elif any(var in col_lower for var in phone_variations):
            column_mapping[col] = 'phone'
        elif any(var in col_lower for var in email_variations):
            column_mapping[col] = 'email'

    return column_mapping
```

## 🚨 Error Handling

### Common Error Scenarios

1. **Invalid Phone Format**
   - Error: `Row X: Invalid phone number format: invalid_phone`
   - Solution: Use supported phone number formats

2. **Missing Required Fields**
   - Error: `Row X: Missing name field`
   - Solution: Ensure CSV has name and phone columns

3. **Unsupported File Format**
   - Error: `Unsupported file format. Please use CSV or Excel files.`
   - Solution: Use .csv, .xlsx, or .xls files

4. **Empty Data**
   - Error: `CSV data cannot be empty`
   - Solution: Provide valid CSV data

### Error Recovery

- **Partial Success**: System continues processing valid rows
- **Detailed Reporting**: Specific row numbers for errors
- **Skip Invalid**: Invalid rows are skipped, not stopping the entire import
- **Summary Statistics**: Clear counts of imported/updated/skipped contacts

## 📊 Performance Considerations

### Batch Processing
- Processes contacts in batches for better performance
- Memory-efficient CSV/Excel reading
- Database transactions for data integrity

### Rate Limiting
- Maximum 1000 contacts per import
- Prevents system overload
- Configurable limits

### Duplicate Handling
- `skip_duplicates: true` - Skip existing contacts
- `update_existing: true` - Update existing contacts
- Phone number-based duplicate detection

## 🔍 Testing

### Test Scripts
- `test_enhanced_bulk_import.py` - Comprehensive testing
- `test_simple_import.py` - Basic endpoint testing

### Test Coverage
- ✅ Phone number format variations
- ✅ CSV column name variations
- ✅ Excel file processing
- ✅ Error handling scenarios
- ✅ Authentication requirements

## 🎯 Usage Examples

### Frontend Integration

```javascript
// Upload CSV file
const formData = new FormData();
formData.append('file', csvFile);
formData.append('import_type', 'csv');
formData.append('skip_duplicates', 'true');

const response = await fetch('/api/messaging/contacts/bulk-import/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### Direct CSV Data

```javascript
const csvData = `name,phone
John Doe,0712345678
Jane Smith,0712345679`;

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
```

## 🎉 Benefits

### For Users
- **Flexible Input**: Accept various phone number formats
- **Easy Import**: No need to standardize column names
- **Error Recovery**: Clear error messages and partial success
- **Multiple Formats**: Support for both CSV and Excel

### For Developers
- **Robust Processing**: Handles edge cases gracefully
- **Clear Documentation**: Comprehensive API documentation
- **Easy Integration**: Simple REST API
- **Extensible**: Easy to add new phone number formats

## 🔧 Configuration

### Required Dependencies
```
phonenumbers==8.13.25
pandas==2.2.3
openpyxl==3.1.5
```

### Environment Variables
- No additional configuration required
- Uses existing authentication system
- Leverages existing database models

---

## 📞 Support

For technical support or questions about the enhanced bulk import functionality, please refer to the API documentation or contact the development team.

**Last Updated:** October 2024
**Version:** 2.0
**Status:** Production Ready ✅
