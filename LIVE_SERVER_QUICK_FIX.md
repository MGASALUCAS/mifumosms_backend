# Live Server Sender ID API Fix Guide

## 🚨 **Common Issues & Quick Fixes**

### **Issue 1: Frontend API Endpoint Mismatch**

**Problem**: Frontend is calling wrong endpoint
**Solution**: Check these endpoints are working:

```bash
# Test these endpoints on your live server:
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://your-domain.com/api/messaging/sender-ids/"

curl -H "Authorization: Bearer YOUR_TOKEN" \
     "https://your-domain.com/api/messaging/sender-requests/available/"
```

### **Issue 2: User Doesn't Have Tenant**

**Problem**: User is not associated with a tenant
**Solution**: Check user-tenant relationship:

```python
# Run on live server:
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from tenants.models import Tenant
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> print(f"User tenant: {user.tenant}")
>>> print(f"Tenant name: {user.tenant.name if user.tenant else 'None'}")
```

### **Issue 3: Sender ID Status Not Active**

**Problem**: Sender ID exists but status is not 'active'
**Solution**: Update sender ID status:

```python
# Run on live server:
python manage.py shell
>>> from messaging.models_sms import SMSSenderID
>>> sender = SMSSenderID.objects.get(sender_id='Taarifa-SMS')
>>> sender.status = 'active'
>>> sender.save()
>>> print(f"Updated sender ID status: {sender.status}")
```

### **Issue 4: Frontend Authentication Issue**

**Problem**: Frontend not sending proper authentication
**Solution**: Check frontend API calls:

```javascript
// Frontend should include:
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

## 🔧 **Quick Debug Steps**

### **Step 1: Run Debug Script**

```bash
# On your live server:
python debug_live_server.py
```

This will show you:
- All tenants and their sender IDs
- Sender ID statuses
- Common issues

### **Step 2: Test API Endpoints**

```bash
# On your live server:
python test_live_api.py
```

This will test all sender ID endpoints.

### **Step 3: Check Frontend Network Tab**

1. Open browser developer tools
2. Go to Network tab
3. Try to load sender IDs
4. Check the API request/response

## 🎯 **Most Likely Issues**

### **1. Wrong API Endpoint**
Frontend might be calling:
- ❌ `/api/sender-ids/` (wrong)
- ✅ `/api/messaging/sender-ids/` (correct)

### **2. Missing Authentication**
Frontend might not be sending:
- ❌ No Authorization header
- ✅ `Authorization: Bearer <token>`

### **3. Wrong Response Format**
Frontend might expect:
- ❌ Direct array: `["Taarifa-SMS"]`
- ✅ Wrapped response: `{"success": true, "data": [...]}`

## 🚀 **Quick Fix Commands**

### **Fix Sender ID Status**
```bash
python manage.py shell -c "
from messaging.models_sms import SMSSenderID
SMSSenderID.objects.filter(sender_id='Taarifa-SMS').update(status='active')
print('Updated Taarifa-SMS status to active')
"
```

### **Check User Tenant**
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
for user in User.objects.filter(tenant__isnull=False)[:5]:
    print(f'{user.email} -> {user.tenant.name}')
"
```

### **Test API Response**
```bash
python manage.py shell -c "
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()
client = Client()
user = User.objects.filter(tenant__isnull=False).first()
client.force_login(user)
response = client.get('/api/messaging/sender-ids/')
print(f'Status: {response.status_code}')
print(f'Response: {response.content}')
"
```

## 📋 **Frontend Integration Checklist**

- [ ] **API Endpoint**: Using `/api/messaging/sender-ids/`
- [ ] **Authentication**: Sending `Authorization: Bearer <token>`
- [ ] **Response Format**: Expecting `{"success": true, "data": [...]}`
- [ ] **Error Handling**: Checking for `success: false`
- [ ] **Loading States**: Showing loading while fetching

## 🔍 **Debug Output Examples**

### **Working API Response**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "sender_id": "Taarifa-SMS",
      "sample_content": "A test use case...",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### **Error Response**
```json
{
  "success": false,
  "message": "User is not associated with any tenant"
}
```

## 🎉 **Success Indicators**

- ✅ API returns `200` status
- ✅ Response has `"success": true`
- ✅ Data array contains sender IDs
- ✅ Sender ID status is `"active"`
- ✅ Frontend displays sender IDs in dropdown

Run the debug scripts on your live server and share the output - I can help you identify the exact issue!
