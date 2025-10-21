#!/bin/bash

# Example curl command to test the contact import endpoint
# Replace the URL and authentication as needed

BASE_URL="http://localhost:8000"
ENDPOINT="$BASE_URL/api/contacts/import/"

# Example data
curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
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
      },
      {
        "full_name": "Bob Johnson",
        "phone": "255987654321",
        "email": ""
      }
    ]
  }'

echo ""
echo "Expected response:"
echo '{
  "imported": 3,
  "skipped": 0,
  "total_processed": 3,
  "errors": [],
  "message": "Successfully imported 3 contacts"
}'
