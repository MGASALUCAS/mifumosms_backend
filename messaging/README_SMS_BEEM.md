# SMS Integration with Beem Africa

## Overview

This module provides comprehensive SMS messaging capabilities using Beem Africa as the primary SMS provider. Beem Africa is a leading SMS provider in Africa with excellent delivery rates, competitive pricing, and support for multiple African countries.

## Features

- ✅ **Single SMS Sending** - Send individual SMS messages
- ✅ **Bulk SMS Sending** - Send multiple SMS messages efficiently
- ✅ **Scheduled SMS** - Schedule messages for future delivery
- ✅ **Phone Number Validation** - Validate and format phone numbers
- ✅ **Cost Estimation** - Real-time cost calculation
- ✅ **Delivery Status Tracking** - Track message delivery status
- ✅ **Connection Testing** - Test API connectivity
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Multi-tenant Support** - Full tenant isolation
- ✅ **REST API** - Complete REST API for frontend integration

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API     │    │   Beem Africa   │
│   (React)       │◄──►│   (Backend)      │◄──►│   SMS API       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Database       │
                       │   (PostgreSQL)   │
                       └──────────────────┘
```

## Installation

### 1. Install Dependencies

The required packages are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Add the following variables to your `.env` file:

```env
# Beem Africa SMS Configuration
BEEM_API_KEY=your-beem-api-key
BEEM_SECRET_KEY=your-beem-secret-key
BEEM_DEFAULT_SENDER_ID=MIFUMO
BEEM_API_TIMEOUT=30
```

### 3. Database Migration

Run the database migrations to create the SMS tables:

```bash
python manage.py makemigrations messaging
python manage.py migrate
```

### 4. Test Configuration

Run the test script to verify your configuration:

```bash
python test_sms_beem.py
```

## API Endpoints

### Base URL
```
https://your-domain.com/api/messaging/sms/beem/
```

### Authentication
All endpoints require JWT authentication:
```http
Authorization: Bearer your-jwt-token
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/send/` | Send single SMS |
| `POST` | `/send-bulk/` | Send bulk SMS |
| `GET` | `/test-connection/` | Test Beem connection |
| `GET` | `/balance/` | Get account balance |
| `POST` | `/validate-phone/` | Validate phone number |
| `GET` | `/{message_id}/status/` | Get delivery status |

## Usage Examples

### 1. Send Single SMS

```python
import requests

url = "https://your-domain.com/api/messaging/sms/beem/send/"
headers = {
    "Authorization": "Bearer your-jwt-token",
    "Content-Type": "application/json"
}
data = {
    "message": "Hello from Mifumo WMS!",
    "recipients": ["255700000001", "255700000002"],
    "sender_id": "MIFUMO"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 2. Send Bulk SMS

```python
data = {
    "messages": [
        {
            "message": "Message 1",
            "recipients": ["255700000001"],
            "sender_id": "MIFUMO"
        },
        {
            "message": "Message 2", 
            "recipients": ["255700000002"],
            "sender_id": "MIFUMO"
        }
    ]
}

response = requests.post(url, json=data, headers=headers)
```

### 3. Schedule SMS

```python
from datetime import datetime, timedelta

schedule_time = datetime.now() + timedelta(hours=1)

data = {
    "message": "Scheduled message",
    "recipients": ["255700000001"],
    "sender_id": "MIFUMO",
    "schedule_time": schedule_time.isoformat()
}
```

### 4. Validate Phone Number

```python
url = "https://your-domain.com/api/messaging/sms/beem/validate-phone/"
data = {"phone_number": "255700000001"}

response = requests.post(url, json=data, headers=headers)
```

## Phone Number Format

Beem SMS requires phone numbers in international format without the `+` sign:

### Valid Formats
- `255700000001` (Tanzania)
- `254700000001` (Kenya) 
- `2347000000001` (Nigeria)
- `27123456789` (South Africa)

### Invalid Formats
- `+255700000001` (contains +)
- `0700000001` (missing country code)
- `255-700-000-001` (contains dashes)

## Cost Calculation

The system automatically calculates costs based on:
- Number of recipients
- Message length (160 characters per SMS part)
- Beem's current pricing

### Example Costs
- 1 recipient, 80 characters = $0.05
- 1 recipient, 200 characters = $0.10 (2 SMS parts)
- 10 recipients, 80 characters = $0.50

## Error Handling

### Common Error Responses

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error message"]
    }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid data |
| `401` | Unauthorized - Authentication required |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource not found |
| `500` | Internal Server Error - Server error |

## Models

### SMSProvider
Stores SMS provider configurations (Beem, Twilio, etc.)

### SMSSenderID
Manages registered sender IDs for tenants

### SMSTemplate
SMS message templates with variables

### SMSMessage
Tracks individual SMS messages and their status

### SMSDeliveryReport
Delivery status reports from providers

## Services

### BeemSMSService
Main service class for Beem SMS operations:

```python
from messaging.services.beem_sms import BeemSMSService

service = BeemSMSService()

# Send SMS
result = service.send_sms(
    message="Hello!",
    recipients=["255700000001"],
    source_addr="MIFUMO"
)

# Test connection
result = service.test_connection()

# Validate phone
is_valid = service.validate_phone_number("255700000001")
```

## Testing

### Run Test Suite

```bash
python test_sms_beem.py
```

### Manual Testing

1. **Test Connection**
```bash
curl -X GET "https://your-domain.com/api/messaging/sms/beem/test-connection/" \
  -H "Authorization: Bearer your-jwt-token"
```

2. **Send Test SMS**
```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/send/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test message",
    "recipients": ["255700000001"],
    "sender_id": "TEST"
  }'
```

3. **Validate Phone**
```bash
curl -X POST "https://your-domain.com/api/messaging/sms/beem/validate-phone/" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "255700000001"}'
```

## Configuration

### Django Settings

The following settings are automatically configured:

```python
# Beem Africa SMS
BEEM_API_KEY = config('BEEM_API_KEY', default='')
BEEM_SECRET_KEY = config('BEEM_SECRET_KEY', default='')
BEEM_DEFAULT_SENDER_ID = config('BEEM_DEFAULT_SENDER_ID', default='MIFUMO')
BEEM_API_TIMEOUT = config('BEEM_API_TIMEOUT', default=30, cast=int)
```

### Environment Variables

Create a `.env` file in your project root:

```env
# Beem Africa SMS Configuration
BEEM_API_KEY=your-beem-api-key-here
BEEM_SECRET_KEY=your-beem-secret-key-here
BEEM_DEFAULT_SENDER_ID=MIFUMO
BEEM_API_TIMEOUT=30
```

## Monitoring and Logging

### Logging

The service includes comprehensive logging:

```python
import logging
logger = logging.getLogger(__name__)

# Logs are automatically generated for:
# - SMS sending attempts
# - API responses
# - Error conditions
# - Cost calculations
```

### Monitoring

Track SMS usage and costs:

```python
# Get SMS statistics
from messaging.models_sms import SMSMessage

total_sent = SMSMessage.objects.filter(status='sent').count()
total_cost = SMSMessage.objects.aggregate(
    total=Sum('cost_amount')
)['total']
```

## Troubleshooting

### Common Issues

1. **API Key Not Configured**
   - Ensure `BEEM_API_KEY` and `BEEM_SECRET_KEY` are set in `.env`
   - Restart the Django server after adding environment variables

2. **Phone Number Validation Fails**
   - Use international format without `+` sign
   - Include country code (e.g., 255 for Tanzania)

3. **SMS Not Sending**
   - Check Beem account balance
   - Verify sender ID is active
   - Check phone number format

4. **Connection Timeout**
   - Increase `BEEM_API_TIMEOUT` setting
   - Check network connectivity

### Debug Mode

Enable debug logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'messaging.services.beem_sms': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Security

### API Key Protection
- Store API keys in environment variables
- Never commit `.env` files to version control
- Use different keys for development and production

### Rate Limiting
- Maximum 1000 recipients per single SMS call
- Maximum 100 messages per bulk SMS call
- API timeout: 30 seconds (configurable)

### Data Privacy
- Phone numbers are stored securely
- Message content is encrypted at rest
- Full tenant isolation

## Performance

### Optimization Tips
1. Use bulk SMS for multiple recipients
2. Implement message queuing for high volume
3. Cache phone number validation results
4. Use database indexes for message queries

### Scaling
- The service is designed to handle high volume
- Database queries are optimized
- API calls are batched when possible

## Support

### Documentation
- [API Documentation](api_documentation_sms.md)
- [Beem Africa Docs](https://login.beem.africa)

### Contact
- **Support Email**: support@mifumo.com
- **Technical Issues**: tech@mifumo.com

## Changelog

### Version 1.0.0
- Initial release with Beem Africa integration
- Support for single and bulk SMS sending
- Phone number validation and formatting
- Cost estimation and tracking
- Delivery status monitoring
- Comprehensive error handling
- REST API endpoints
- Test suite and documentation
