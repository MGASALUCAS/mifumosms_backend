# Contact Import API Documentation

## Overview

The Contact Import API allows you to import contacts from a phone's contact picker (Android Chrome/Edge) or other sources. This endpoint is designed to work with the Contact Picker API data format and includes automatic phone number normalization for Tanzanian numbers.

## Endpoint

```
POST /api/contacts/import/
```

## Authentication

Requires authentication. Include your authentication token in the request headers.

## Request Format

### Headers
```
Content-Type: application/json
Authorization: Bearer <your-token>
```

### Request Body

```json
{
  "contacts": [
    {
      "full_name": "John Doe",
      "phone": "+255123456789",
      "email": "john@example.com"
    },
    {
      "full_name": "Jane Smith",
      "phone": "0712345678",
      "email": "jane@example.com"
    }
  ]
}
```

### Field Descriptions

- `contacts` (array, required): Array of contact objects (1-100 contacts)
- `full_name` (string, optional): Contact's full name
- `phone` (string, optional): Phone number (will be normalized to E.164 format)
- `email` (string, optional): Email address

**Note**: At least one of `full_name`, `phone`, or `email` must be provided for each contact.

## Phone Number Normalization

The API automatically normalizes phone numbers to E.164 format:

- `0712345678` → `+255712345678` (Tanzanian mobile)
- `255123456789` → `+255123456789` (Already with country code)
- `+255123456789` → `+255123456789` (Already in E.164 format)

## Response Format

### Success Response (201 Created)

```json
{
  "imported": 2,
  "skipped": 0,
  "total_processed": 2,
  "errors": [],
  "message": "Successfully imported 2 contacts"
}
```

### Response Fields

- `imported` (integer): Number of contacts successfully imported
- `skipped` (integer): Number of contacts skipped (duplicates)
- `total_processed` (integer): Total number of contacts processed
- `errors` (array): List of error messages for failed imports
- `message` (string): Human-readable summary message

### Error Response (400 Bad Request)

```json
{
  "contacts": [
    "Contact 1: At least one field (name, phone, or email) is required"
  ]
}
```

## Frontend Integration

### React/TypeScript Example

```typescript
// Contact picker support detection
export const isContactPickerSupported =
  typeof navigator !== "undefined" &&
  "contacts" in navigator &&
  // @ts-ignore
  typeof navigator.contacts?.select === "function";

// Contact import handler
export async function handlePickFromPhone(userId: string) {
  if (!isContactPickerSupported) {
    throw new Error(
      "Phone contact import isn't supported on this device/browser. Try Chrome on Android or use CSV."
    );
  }

  try {
    // @ts-ignore
    const picked: RawContact[] = await navigator.contacts.select(
      ["name", "tel", "email"],
      { multiple: true }
    );

    const contacts = picked
      .map((c) => ({
        full_name: (c.name?.[0] ?? "").trim(),
        phone: normalizeTZ(c.tel?.[0]),
        email: c.email?.[0] || null,
      }))
      .filter((x) => x.full_name || x.phone || x.email);

    if (!contacts.length) return { imported: 0 };

    // Send to backend
    const res = await fetch("/api/contacts/import/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contacts }),
      credentials: "include",
    });

    if (!res.ok) throw new Error("Server rejected the import.");

    return await res.json();
  } catch (err: any) {
    if (err?.name === "NotAllowedError") {
      throw new Error("Please allow access to contacts to use this feature.");
    }
    if (err?.name === "AbortError") {
      return { imported: 0, canceled: true };
    }
    throw err;
  }
}

// Phone number normalization
const normalizeTZ = (raw?: string) => {
  if (!raw) return "";
  const d = raw.replace(/\D/g, "");
  if (d.startsWith("255")) return `+${d}`;
  if (d.startsWith("0") && d.length === 10) return `+255${d.slice(1)}`;
  return raw.startsWith("+") ? raw : `+${d}`;
};
```

### UI Button Example

```tsx
<Button
  onClick={async () => {
    try {
      const result = await handlePickFromPhone(currentUser.id);
      if (result.canceled) return;
      if (result.imported) {
        toast.success(`Imported ${result.imported} contact(s).`);
      } else {
        toast("No contacts selected.");
      }
      // Refresh contacts list
    } catch (e: any) {
      toast.error(e.message || "Import failed. Try again or use CSV.");
    }
  }}
  disabled={!isContactPickerSupported}
  title={
    isContactPickerSupported
      ? "Pick from phone"
      : "Not supported on this device — use CSV"
  }
>
  Phone
</Button>
```

## Error Handling

### Common Error Scenarios

1. **No valid contacts**: All contacts are empty or invalid
2. **Invalid phone format**: Phone number cannot be normalized
3. **Duplicate contacts**: Contact with same phone number already exists
4. **Validation errors**: Missing required fields or invalid data

### Error Response Examples

```json
{
  "contacts": [
    "Contact 1: At least one field (name, phone, or email) is required",
    "Contact 2: Invalid phone number format"
  ]
}
```

## Rate Limiting

The endpoint respects the same rate limiting as other contact operations. Avoid importing large batches (>100 contacts) in a single request.

## Browser Compatibility

- **Android Chrome/Edge**: Full support for Contact Picker API
- **iOS Safari**: Not supported (use CSV fallback)
- **Desktop browsers**: Not supported (use CSV fallback)

## Testing

Use the provided test script to verify the endpoint:

```bash
python test_contact_import.py
```

Make sure to:
1. Update the `BASE_URL` in the test script
2. Add proper authentication headers
3. Run the Django development server

## Security Considerations

- All contacts are associated with the authenticated user
- Phone numbers are validated and normalized
- Duplicate contacts are automatically skipped
- Input is sanitized and validated
- Rate limiting prevents abuse
