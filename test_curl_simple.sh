#!/bin/bash

echo "Curl Test for Payment System"
echo "============================"

echo ""
echo "1. Testing Mobile Money Providers (should require auth):"
echo "--------------------------------------------------------"
curl -X GET "http://127.0.0.1:8000/api/billing/payments/providers/" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "2. Testing SMS Packages (should require auth):"
echo "-----------------------------------------------"
curl -X GET "http://127.0.0.1:8000/api/billing/sms/packages/" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "3. Testing Payment Initiation (should require auth):"
echo "-----------------------------------------------------"
curl -X POST "http://127.0.0.1:8000/api/billing/payments/initiate/" \
  -H "Content-Type: application/json" \
  -d '{
    "package_id": "test-package-id",
    "buyer_email": "test@example.com",
    "buyer_name": "Test User",
    "buyer_phone": "0744963858",
    "mobile_money_provider": "vodacom"
  }' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "4. Testing Webhook Endpoint:"
echo "-----------------------------"
curl -X POST "http://127.0.0.1:8000/api/billing/payments/webhook/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "test-order-123",
    "payment_status": "COMPLETED",
    "reference": "REF123456789"
  }' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "5. Testing with a real transaction ID (should fail - transaction not found):"
echo "-----------------------------------------------------------------------------"
curl -X POST "http://127.0.0.1:8000/api/billing/payments/webhook/" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "ZP-20241017-ABC12345",
    "payment_status": "COMPLETED",
    "reference": "REF123456789",
    "transid": "TXN123456789",
    "channel": "MPESA-TZ",
    "msisdn": "255744963858"
  }' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "Test Complete!"
echo "=============="
echo "Expected Results:"
echo "- Endpoints 1-3 should return 401 (Unauthorized) - authentication required"
echo "- Endpoint 4 should return 200 (webhook processed, but transaction not found)"
echo "- Endpoint 5 should return 404 (transaction not found)"
