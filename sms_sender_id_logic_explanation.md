# SMS Sender ID Logic - Step by Step Explanation

## 🔄 **Complete SMS Sender ID Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMS SENDER ID LOGIC FLOW                     │
└─────────────────────────────────────────────────────────────────┘

1. 📱 SMS SEND REQUEST
   ├── User calls: sms_service.send_sms(to, message, sender_id)
   ├── SMSService.get_provider() finds active provider
   └── Routes to: BeemSMSService.send_sms()

2. 🔍 SENDER ID VALIDATION
   ├── Checks if sender_id is provided
   ├── Validates sender_id format
   └── Prepares for API call

3. 🌐 BEEM API REQUEST
   ├── POST to: https://apisms.beem.africa/v1/send
   ├── Headers: Basic Auth (API_KEY:SECRET_KEY)
   └── Body: {"source_addr": sender_id, "message": text, "recipients": [...]}

4. 📊 BEEM API RESPONSE
   ├── Success (200): {"successful": true, "request_id": "..."}
   ├── Error (400): {"code": 111, "message": "Invalid Sender Id"}
   └── Other errors: Network, auth, etc.

5. ✅ SUCCESS HANDLING
   ├── Returns: {success: true, message_id: "...", valid_count: 1}
   ├── Logs: SMS sent successfully
   └── Updates: SMSMessage record

6. ❌ ERROR HANDLING
   ├── Returns: {success: false, error: "Invalid Sender Id", code: 111}
   ├── Logs: SMS failed with error
   └── User sees: "Unknown error" (if error message not parsed)
```

## 🏗️ **Architecture Components**

### **1. SMSService (Main Controller)**
```python
class SMSService:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._providers = {}  # Cache for provider instances
    
    def get_provider(self, provider_id=None):
        # 1. Find active SMS provider for tenant
        # 2. Create provider instance (BeemSMSService)
        # 3. Cache and return provider
    
    def send_sms(self, to, message, sender_id, provider_id=None):
        # 1. Get provider instance
        # 2. Call provider.send_sms()
        # 3. Return result
```

### **2. BeemSMSService (Beem Implementation)**
```python
class BeemSMSService(BaseSMSProvider):
    def __init__(self, provider: SMSProvider):
        # 1. Set API credentials from provider
        # 2. Set API URLs from settings
        # 3. Initialize auth headers
    
    def send_sms(self, to, message, sender_id, **kwargs):
        # 1. Prepare recipients array
        # 2. Build request data with sender_id
        # 3. Make HTTP POST to Beem API
        # 4. Parse response and return result
```

### **3. Database Models**
```python
class SMSProvider:
    # Stores provider configuration
    tenant = ForeignKey(Tenant)
    provider_type = 'beem'
    api_key = CharField()
    secret_key = CharField()
    is_active = BooleanField()

class SMSSenderID:
    # Stores sender ID information
    provider = ForeignKey(SMSProvider)
    sender_id = CharField()  # e.g., "Taarifa-SMS"
    status = CharField()     # "active", "inactive", "pending"
    sample_content = TextField()
```

## 🔍 **Step-by-Step Process**

### **Step 1: SMS Request Initiation**
```python
# User calls this
sms_service = SMSService(tenant_id="tenant-uuid")
result = sms_service.send_sms(
    to="+255614853618",
    message="Hello from Mifumo!",
    sender_id="Taarifa-SMS"  # This is the key parameter
)
```

### **Step 2: Provider Resolution**
```python
def get_provider(self, provider_id=None):
    # 1. Query database for active SMS provider
    provider = SMSProvider.objects.filter(
        tenant_id=self.tenant_id,
        is_active=True
    ).first()
    
    # 2. Create provider instance
    if provider.provider_type == 'beem':
        return BeemSMSService(provider)
```

### **Step 3: Sender ID Validation**
```python
def send_sms(self, to, message, sender_id, **kwargs):
    # 1. Validate phone number format
    # 2. Check sender_id is not empty
    # 3. Prepare recipients array
    recipients = [{
        "recipient_id": 1,
        "dest_addr": to  # Phone number
    }]
```

### **Step 4: API Request Preparation**
```python
# 1. Build request data
data = {
    "source_addr": sender_id,  # "Taarifa-SMS"
    "message": message,        # "Hello from Mifumo!"
    "encoding": 0,
    "recipients": recipients
}

# 2. Prepare headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {base64_encoded_credentials}'
}
```

### **Step 5: Beem API Call**
```python
# 1. Make HTTP POST request
response = requests.post(
    'https://apisms.beem.africa/v1/send',
    json=data,
    headers=headers,
    timeout=30
)

# 2. Parse response
response_data = response.json()
```

### **Step 6: Response Handling**
```python
if response.status_code == 200 and response_data.get('successful'):
    # SUCCESS: SMS sent
    return {
        'success': True,
        'message_id': response_data.get('request_id'),
        'valid_count': response_data.get('valid', 0)
    }
else:
    # ERROR: Handle different error types
    return {
        'success': False,
        'error': response_data.get('message', 'Unknown error'),
        'error_code': response_data.get('code')
    }
```

## 🚨 **Common Error Scenarios**

### **Error 111: Invalid Sender Id**
```json
{
    "data": {
        "code": 111,
        "message": "Invalid Sender Id"
    }
}
```
**Cause**: Sender ID not registered with Beem
**Solution**: Use registered sender ID like "Taarifa-SMS"

### **Error 400: Missing Parameters**
```json
{
    "code": 400,
    "message": "\"senderid\" is required"
}
```
**Cause**: Missing sender_id in request
**Solution**: Always provide sender_id parameter

### **Error 401: Authentication Failed**
```json
{
    "code": 401,
    "message": "Unauthorized"
}
```
**Cause**: Invalid API credentials
**Solution**: Check BEEM_API_KEY and BEEM_SECRET_KEY

## 🔧 **Sender ID Management**

### **Getting Available Sender IDs**
```python
def get_sender_ids(self, q=None, status=None):
    # 1. Query Beem API for registered sender IDs
    response = requests.get(
        'https://apisms.beem.africa/public/v1/sender-names',
        headers=self._get_headers()
    )
    
    # 2. Return list of sender IDs with status
    return {
        'success': True,
        'sender_ids': response_data.get('data', [])
    }
```

### **Creating New Sender ID**
```python
def create_sender_id(self, sender_id, sample_content):
    # 1. Send registration request to Beem
    data = {
        "senderid": sender_id,
        "sample_content": sample_content
    }
    
    # 2. Beem reviews and approves (manual process)
    # 3. Returns status: "pending", "approved", "rejected"
```

## 📊 **Database Integration**

### **SMS Message Tracking**
```python
# 1. Create SMSMessage record before sending
sms_message = SMSMessage.objects.create(
    tenant=tenant,
    provider=provider,
    sender_id=sender_id,
    recipient_number=to,
    message=message,
    status='pending'
)

# 2. Update status after API response
if result['success']:
    sms_message.status = 'sent'
    sms_message.provider_message_id = result['message_id']
else:
    sms_message.status = 'failed'
    sms_message.error_message = result['error']

sms_message.save()
```

## 🎯 **Key Points**

1. **Sender ID is Required**: Every SMS must have a valid sender_id
2. **Registration Required**: Sender IDs must be registered with Beem first
3. **Status Matters**: Only "active" sender IDs can send SMS
4. **Error Handling**: Always check response codes and error messages
5. **Caching**: Provider instances are cached for performance
6. **Multi-tenant**: Each tenant can have different sender IDs

## 🔄 **Complete Flow Summary**

```
User Request → SMSService → BeemSMSService → Beem API → Response → Database Update
     ↓              ↓              ↓            ↓          ↓           ↓
  sender_id    Get Provider    Prepare Data   HTTP POST   Parse      Update SMS
  required     from Database   with sender_id  Request    Response   Message
```

This is how the SMS sender ID logic works in your Mifumo WMS system!
