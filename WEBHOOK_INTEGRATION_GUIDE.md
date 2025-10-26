# Webhook Integration Guide

## Overview

Webhooks allow you to receive real-time notifications about SMS delivery events. This enables you to track message status, handle delivery failures, and update your application accordingly.

## Webhook Events

### Available Events

| Event | Description | When Triggered |
|-------|-------------|----------------|
| `message.sent` | Message was sent to the SMS provider | Immediately after successful API call |
| `message.delivered` | Message was delivered to recipient | When delivery confirmation is received |
| `message.failed` | Message delivery failed | When delivery fails or times out |

## Setting Up Webhooks

### 1. Create Webhook in Dashboard

1. Log in to your Mifumo SMS dashboard
2. Go to **Settings** → **API & Webhooks**
3. Click **"+ Add Webhook"**
4. Enter your webhook URL
5. Select the events you want to receive
6. Click **"Save"**

### 2. Webhook URL Requirements

Your webhook endpoint must:
- Accept POST requests
- Return HTTP 200 status for successful processing
- Handle JSON payloads
- Respond within 30 seconds

### 3. Webhook Security

For production use, verify webhook authenticity:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

## Webhook Payloads

### Message Sent Event

```json
{
  "event": "message.sent",
  "message_id": "msg_123456789",
  "recipients": ["+255123456789", "+255987654321"],
  "sender_id": "Taarifa-SMS",
  "content": "Hello from Mifumo SMS!",
  "sent_at": "2024-01-01T10:00:00Z",
  "cost": 10.0,
  "currency": "USD",
  "provider": "beem_africa",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Message Delivered Event

```json
{
  "event": "message.delivered",
  "message_id": "msg_123456789",
  "recipient": "+255123456789",
  "status": "delivered",
  "delivered_at": "2024-01-01T10:05:00Z",
  "provider_status": "DELIVRD",
  "error_message": null,
  "timestamp": "2024-01-01T10:05:00Z"
}
```

### Message Failed Event

```json
{
  "event": "message.failed",
  "message_id": "msg_123456789",
  "recipient": "+255123456789",
  "status": "failed",
  "failed_at": "2024-01-01T10:05:00Z",
  "error_code": "INVALID_NUMBER",
  "error_message": "Invalid phone number format",
  "timestamp": "2024-01-01T10:05:00Z"
}
```

## Webhook Implementation Examples

### Python Flask

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook/sms', methods=['POST'])
def handle_sms_webhook():
    try:
        # Get webhook data
        data = request.get_json()
        
        # Verify webhook (optional but recommended)
        # signature = request.headers.get('X-Webhook-Signature')
        # if not verify_webhook(json.dumps(data), signature, WEBHOOK_SECRET):
        #     return jsonify({'error': 'Invalid signature'}), 401
        
        # Process webhook event
        event_type = data.get('event')
        message_id = data.get('message_id')
        
        if event_type == 'message.sent':
            print(f"Message {message_id} sent successfully")
            # Update your database
            update_message_status(message_id, 'sent')
            
        elif event_type == 'message.delivered':
            print(f"Message {message_id} delivered to {data.get('recipient')}")
            # Update delivery status
            update_delivery_status(message_id, data.get('recipient'), 'delivered')
            
        elif event_type == 'message.failed':
            print(f"Message {message_id} failed: {data.get('error_message')}")
            # Handle failure
            handle_delivery_failure(message_id, data.get('error_message'))
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'error': 'Internal error'}), 500

def update_message_status(message_id, status):
    # Update your database
    pass

def update_delivery_status(message_id, recipient, status):
    # Update delivery status in your database
    pass

def handle_delivery_failure(message_id, error_message):
    # Handle delivery failure (retry, notify user, etc.)
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Node.js Express

```javascript
const express = require('express');
const app = express();

app.use(express.json());

app.post('/webhook/sms', (req, res) => {
  try {
    const data = req.body;
    const eventType = data.event;
    const messageId = data.message_id;
    
    switch (eventType) {
      case 'message.sent':
        console.log(`Message ${messageId} sent successfully`);
        updateMessageStatus(messageId, 'sent');
        break;
        
      case 'message.delivered':
        console.log(`Message ${messageId} delivered to ${data.recipient}`);
        updateDeliveryStatus(messageId, data.recipient, 'delivered');
        break;
        
      case 'message.failed':
        console.log(`Message ${messageId} failed: ${data.error_message}`);
        handleDeliveryFailure(messageId, data.error_message);
        break;
        
      default:
        console.log(`Unknown event type: ${eventType}`);
    }
    
    res.status(200).json({ status: 'success' });
    
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: 'Internal error' });
  }
});

function updateMessageStatus(messageId, status) {
  // Update your database
}

function updateDeliveryStatus(messageId, recipient, status) {
  // Update delivery status in your database
}

function handleDeliveryFailure(messageId, errorMessage) {
  // Handle delivery failure
}

app.listen(5000, () => {
  console.log('Webhook server running on port 5000');
});
```

### PHP

```php
<?php
// webhook_handler.php

// Get webhook data
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Verify webhook (optional but recommended)
// $signature = $_SERVER['HTTP_X_WEBHOOK_SIGNATURE'] ?? '';
// if (!verify_webhook($input, $signature, WEBHOOK_SECRET)) {
//     http_response_code(401);
//     echo json_encode(['error' => 'Invalid signature']);
//     exit;
// }

try {
    $eventType = $data['event'] ?? '';
    $messageId = $data['message_id'] ?? '';
    
    switch ($eventType) {
        case 'message.sent':
            error_log("Message {$messageId} sent successfully");
            updateMessageStatus($messageId, 'sent');
            break;
            
        case 'message.delivered':
            $recipient = $data['recipient'] ?? '';
            error_log("Message {$messageId} delivered to {$recipient}");
            updateDeliveryStatus($messageId, $recipient, 'delivered');
            break;
            
        case 'message.failed':
            $errorMessage = $data['error_message'] ?? '';
            error_log("Message {$messageId} failed: {$errorMessage}");
            handleDeliveryFailure($messageId, $errorMessage);
            break;
            
        default:
            error_log("Unknown event type: {$eventType}");
    }
    
    http_response_code(200);
    echo json_encode(['status' => 'success']);
    
} catch (Exception $e) {
    error_log("Webhook error: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['error' => 'Internal error']);
}

function updateMessageStatus($messageId, $status) {
    // Update your database
}

function updateDeliveryStatus($messageId, $recipient, $status) {
    // Update delivery status in your database
}

function handleDeliveryFailure($messageId, $errorMessage) {
    // Handle delivery failure
}
?>
```

## Webhook Testing

### Test Webhook Locally

Use ngrok to expose your local server:

```bash
# Install ngrok
npm install -g ngrok

# Start your webhook server
python webhook_server.py

# In another terminal, expose your local server
ngrok http 5000
```

Use the ngrok URL as your webhook URL in the dashboard.

### Test Webhook with cURL

```bash
# Test message.sent event
curl -X POST "https://your-webhook-url.com/webhook/sms" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message.sent",
    "message_id": "msg_test_123",
    "recipients": ["+255123456789"],
    "sender_id": "Taarifa-SMS",
    "content": "Test message",
    "sent_at": "2024-01-01T10:00:00Z",
    "cost": 10.0,
    "currency": "USD",
    "provider": "beem_africa",
    "timestamp": "2024-01-01T10:00:00Z"
  }'
```

## Webhook Retry Policy

If your webhook endpoint fails:
- We retry up to 3 times
- Retry intervals: 1 minute, 5 minutes, 15 minutes
- After 3 failures, the webhook is marked as failed
- You can reactivate failed webhooks in the dashboard

## Best Practices

1. **Idempotency**: Make your webhook handler idempotent to handle duplicate events
2. **Quick Response**: Respond within 30 seconds to avoid timeouts
3. **Error Handling**: Log errors and return appropriate HTTP status codes
4. **Security**: Verify webhook signatures in production
5. **Monitoring**: Monitor webhook delivery success rates
6. **Queue Processing**: Use message queues for high-volume webhook processing

## Troubleshooting

### Common Issues

**Webhook not receiving events:**
- Check webhook URL is accessible
- Verify webhook is active in dashboard
- Check firewall/security group settings

**Webhook timing out:**
- Optimize your webhook handler
- Use asynchronous processing
- Increase timeout if possible

**Duplicate events:**
- Implement idempotency checks
- Use message IDs to track processed events

### Debug Mode

Enable debug mode in your webhook handler to log all incoming events:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/webhook/sms', methods=['POST'])
def handle_sms_webhook():
    logger.debug(f"Received webhook: {request.get_json()}")
    # ... rest of your code
```

## Support

For webhook-related issues:
- Check webhook logs in the dashboard
- Verify your endpoint is working with test calls
- Contact support: support@mifumosms.com

