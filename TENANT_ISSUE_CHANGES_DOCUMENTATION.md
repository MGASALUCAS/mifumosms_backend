# Tenant Issue Branch - Complete Changes Documentation

## Overview

This document provides a comprehensive overview of all changes made in the `tenant_issue` branch, including new features, API endpoints, database changes, and frontend integration requirements.

## 🎯 Main Features Implemented

### 1. **Automatic Tenant Creation System**
- **Purpose**: Automatically create tenant information when a new user registers
- **Benefit**: Ensures SMS functionality is immediately available for all users
- **Implementation**: Django signals-based automatic setup

### 2. **Shared Sender ID System**
- **Purpose**: All users share the same sender ID "Taarifa-SMS" but have individual SMS credits
- **Benefit**: Simplified sender ID management while maintaining individual billing
- **Implementation**: Default sender ID creation with zero credits

### 3. **Flexible User Workflow**
- **Purpose**: Different workflows for different user types
- **Admin/Superadmin**: Get default sender ID automatically (no purchase required)
- **Normal Users**: Can choose order of SMS purchase and sender ID request

### 4. **Sender ID Request System**
- **Purpose**: Allow users to request sender ID approval
- **Benefit**: Controlled sender ID management with admin approval
- **Implementation**: Complete request/approval workflow

## 📁 Files Changed

### **New Files Created**

#### 1. `accounts/apps.py`
```python
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals
```
**Purpose**: Register Django signals for automatic user setup

#### 2. `accounts/signals.py`
```python
# Key functions:
- create_user_profile_and_tenant()  # Auto-create tenant on user creation
- create_default_tenant_for_user()  # Setup tenant with SMS config
- setup_basic_sms_config()         # Configure SMS provider and sender ID
- generate_unique_subdomain()      # Generate unique tenant subdomain
```
**Purpose**: Automatic tenant and SMS configuration setup

#### 3. `accounts/management/commands/setup_shared_sender_id.py`
```python
# Management command to setup shared sender ID for existing tenants
python manage.py setup_shared_sender_id
```
**Purpose**: Migrate existing tenants to shared sender ID system

#### 4. `messaging/models_sender_requests.py`
```python
# New models:
- SenderIDRequest     # User requests for sender ID approval
- SenderIDUsage       # Track sender ID usage with SMS packages
- SenderIDReview      # Admin review and approval system
```
**Purpose**: Sender ID request and approval system

#### 5. `messaging/serializers_sender_requests.py`
```python
# Serializers for API endpoints:
- SenderIDRequestSerializer     # Create/update sender ID requests
- SenderIDReviewSerializer     # Admin review and approval
- SenderIDUsageSerializer      # Track sender ID usage
```
**Purpose**: API serialization for sender ID management

### **Modified Files**

#### 1. `accounts/serializers.py`
**Changes Made**:
- Added email uniqueness validation for profile updates
- Added validation for required fields (first_name, last_name)
- Added validation for boolean fields (email_notifications, sms_notifications)
- Removed username field (not used in custom User model)

**New Validation Methods**:
```python
def validate_email(self, value)           # Email uniqueness check
def validate_first_name(self, value)      # Required field validation
def validate_last_name(self, value)       # Required field validation
def validate_email_notifications(self, value)  # Boolean validation
def validate_sms_notifications(self, value)    # Boolean validation
```

#### 2. `billing/models.py`
**Changes Made**:
- Added `user` field to `Purchase` model
- Fixed admin configuration errors

**New Field**:
```python
class Purchase(models.Model):
    # ... existing fields ...
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
```

#### 3. `billing/admin.py`
**Changes Made**:
- Fixed admin configuration errors
- Removed references to non-existent fields
- Updated list_display and search_fields

#### 4. `mifumo/settings.py`
**Changes Made**:
- Updated `LOCAL_APPS` to use `'accounts.apps.AccountsConfig'`
- Ensured signals are properly registered

#### 5. `messaging/views_sender_requests.py`
**Changes Made**:
- Removed SMS credit requirement validation
- Made SMS purchase optional for sender ID requests
- Updated API responses to reflect flexible workflow

#### 6. `messaging/serializers_sender_requests.py`
**Changes Made**:
- Removed SMS credit requirement validation
- Updated validation messages for flexible workflow

## 🚀 New API Endpoints

### **Sender ID Management Endpoints**

#### 1. **POST** `/api/messaging/sender-requests/`
**Purpose**: Create a new sender ID request
**Authentication**: Required
**Request Body**:
```json
{
    "request_type": "default",
    "requested_sender_id": "Taarifa-SMS",
    "sample_content": "A test use case for the sender name...",
    "business_justification": "Requesting to use the default sender ID..."
}
```
**Response** (201):
```json
{
    "id": "uuid-here",
    "request_type": "default",
    "requested_sender_id": "Taarifa-SMS",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### 2. **GET** `/api/messaging/sender-requests/`
**Purpose**: List all sender ID requests for current user
**Authentication**: Required
**Response** (200):
```json
[
    {
        "id": "uuid-here",
        "requested_sender_id": "Taarifa-SMS",
        "status": "pending",
        "created_at": "2024-01-01T00:00:00Z"
    }
]
```

#### 3. **GET** `/api/messaging/sender-requests/{id}/`
**Purpose**: Get specific sender ID request details
**Authentication**: Required
**Response** (200):
```json
{
    "id": "uuid-here",
    "requested_sender_id": "Taarifa-SMS",
    "status": "pending",
    "sample_content": "A test use case...",
    "business_justification": "Requesting to use...",
    "created_at": "2024-01-01T00:00:00Z"
}
```

#### 4. **PUT** `/api/messaging/sender-requests/{id}/`
**Purpose**: Update sender ID request
**Authentication**: Required
**Request Body**:
```json
{
    "sample_content": "Updated sample content",
    "business_justification": "Updated justification"
}
```

#### 5. **POST** `/api/messaging/sender-requests/{id}/approve/`
**Purpose**: Approve sender ID request (Admin only)
**Authentication**: Required (Admin)
**Request Body**:
```json
{
    "status": "approved",
    "admin_notes": "Approved for use"
}
```

#### 6. **POST** `/api/messaging/sender-requests/{id}/reject/`
**Purpose**: Reject sender ID request (Admin only)
**Authentication**: Required (Admin)
**Request Body**:
```json
{
    "status": "rejected",
    "rejection_reason": "Reason for rejection"
}
```

#### 7. **GET** `/api/messaging/sender-requests/status/`
**Purpose**: Get sender ID request status and SMS balance
**Authentication**: Required
**Response** (200):
```json
{
    "sms_balance": {
        "credits": 100,
        "total_purchased": 500,
        "can_request_sender_id": true
    },
    "sender_id_requests": [
        {
            "id": "uuid-here",
            "requested_sender_id": "Taarifa-SMS",
            "status": "approved"
        }
    ]
}
```

### **Updated Profile Endpoint**

#### **PUT** `/api/auth/profile/`
**Purpose**: Update user profile
**Authentication**: Required
**Request Body**:
```json
{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+255700000000",
    "timezone": "UTC",
    "bio": "User bio",
    "email_notifications": true,
    "sms_notifications": false
}
```
**Response** (200):
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "+255700000000",
    "timezone": "UTC",
    "bio": "User bio",
    "email_notifications": true,
    "sms_notifications": false,
    "is_verified": true,
    "created_at": "2024-01-01T00:00:00Z"
}
```

**Validation Errors** (400):
```json
{
    "email": ["A user with this email already exists."],
    "first_name": ["This field may not be blank."],
    "last_name": ["This field may not be blank."],
    "email_notifications": ["Must be a boolean value."],
    "sms_notifications": ["Must be a boolean value."]
}
```

## 🗄️ Database Changes

### **New Migrations**

#### 1. `billing/migrations/0009_remove_customsmspurchase_user_and_more.py`
- Removed `user` field from `CustomSMSPurchase` model
- Fixed admin configuration issues

#### 2. `messaging/migrations/0007_senderidrequest_senderidusage.py`
- Added `SenderIDRequest` model
- Added `SenderIDUsage` model
- Added `SenderIDReview` model

### **New Models**

#### 1. `SenderIDRequest`
```python
class SenderIDRequest(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    requested_sender_id = models.CharField(max_length=50)
    sample_content = models.TextField()
    business_justification = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### 2. `SenderIDUsage`
```python
class SenderIDUsage(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    sender_id_request = models.ForeignKey(SenderIDRequest, on_delete=models.CASCADE)
    sms_package = models.ForeignKey(SMSPackage, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 🎨 Frontend Integration Requirements

### **New UI Components Needed**

#### 1. **Sender ID Request Form**
```javascript
// Component: SenderIDRequestForm
const SenderIDRequestForm = () => {
    const [formData, setFormData] = useState({
        request_type: 'default',
        requested_sender_id: 'Taarifa-SMS',
        sample_content: 'A test use case for the sender name...',
        business_justification: 'Requesting to use the default sender ID...'
    });

    const handleSubmit = async () => {
        const response = await fetch('/api/messaging/sender-requests/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
    };
};
```

#### 2. **Sender ID Request Status**
```javascript
// Component: SenderIDStatus
const SenderIDStatus = () => {
    const [status, setStatus] = useState(null);

    useEffect(() => {
        fetch('/api/messaging/sender-requests/status/')
            .then(res => res.json())
            .then(data => setStatus(data));
    }, []);

    return (
        <div>
            <h3>SMS Balance: {status?.sms_balance?.credits || 0} credits</h3>
            <h3>Sender ID Status: {status?.sender_id_requests?.[0]?.status || 'Not requested'}</h3>
        </div>
    );
};
```

#### 3. **Admin Approval Interface**
```javascript
// Component: AdminSenderIDApproval
const AdminSenderIDApproval = () => {
    const [requests, setRequests] = useState([]);

    const handleApprove = async (requestId) => {
        await fetch(`/api/messaging/sender-requests/${requestId}/approve/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: 'approved',
                admin_notes: 'Approved for use'
            })
        });
    };

    const handleReject = async (requestId) => {
        await fetch(`/api/messaging/sender-requests/${requestId}/reject/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: 'rejected',
                rejection_reason: 'Reason for rejection'
            })
        });
    };
};
```

### **Updated Profile Form**
```javascript
// Component: ProfileForm (Updated)
const ProfileForm = () => {
    const [formData, setFormData] = useState({
        email: '',
        first_name: '',
        last_name: '',
        phone_number: '',
        timezone: 'UTC',
        bio: '',
        email_notifications: true,
        sms_notifications: false
    });

    const handleSubmit = async () => {
        try {
            const response = await fetch('/api/auth/profile/', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errors = await response.json();
                // Handle validation errors
                console.error('Validation errors:', errors);
            }
        } catch (error) {
            console.error('Profile update failed:', error);
        }
    };
};
```

## 🔄 User Workflow Changes

### **New User Registration Flow**

#### **Admin/Superadmin Users**
1. **Register** → Automatic tenant creation
2. **Get Default Sender ID** → "Taarifa-SMS" created automatically
3. **Ready to Use** → Can send SMS immediately (if they have credits)

#### **Normal Users**
1. **Register** → Automatic tenant creation
2. **Choose Workflow**:
   - **Option A**: Request sender ID → Get approved → Purchase SMS → Send SMS
   - **Option B**: Purchase SMS → Request sender ID → Get approved → Send SMS
   - **Option C**: Do both simultaneously

### **SMS Sending Flow**
1. **Check Sender ID Status** → Must be approved
2. **Check SMS Credits** → Must have credits
3. **Send SMS** → Deduct credits and send

## 🛠️ Management Commands

### **Setup Shared Sender ID**
```bash
python manage.py setup_shared_sender_id
```
**Purpose**: Migrate existing tenants to shared sender ID system
**Usage**: Run after deploying changes to update existing data

## 🧪 Testing

### **Test Scripts Created**
- `test_user_types_workflow.py` - Test different user types
- `test_mvp_complete_flow.py` - Test complete MVP workflow
- `test_user_ownership_verification.py` - Test user ownership
- `test_real_sms_sending.py` - Test actual SMS sending

### **Test Results**
- ✅ Admin users get default sender ID automatically
- ✅ Superadmin users get default sender ID automatically
- ✅ Normal users can choose workflow order
- ✅ Sender ID request/approval system works
- ✅ SMS sending works end-to-end
- ✅ Profile update validation works correctly

## 🚀 Deployment Checklist

### **Backend Deployment**
1. **Pull latest changes** from `tenant_issue` branch
2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```
3. **Setup shared sender ID**:
   ```bash
   python manage.py setup_shared_sender_id
   ```
4. **Restart server** to load new signals

### **Frontend Integration**
1. **Update API calls** to use new endpoints
2. **Add sender ID request components**
3. **Update profile form** with new validation
4. **Add admin approval interface**
5. **Test complete workflow**

## 📊 Impact Summary

### **Benefits**
- ✅ **Automatic Setup**: Users get tenant and SMS config automatically
- ✅ **Flexible Workflow**: Users can choose their preferred order
- ✅ **Shared Sender ID**: Simplified sender ID management
- ✅ **Admin Control**: Controlled sender ID approval process
- ✅ **Better Validation**: Improved profile update validation
- ✅ **End-to-End Testing**: Complete workflow verified

### **Breaking Changes**
- ⚠️ **Profile Update Validation**: Stricter validation for profile updates
- ⚠️ **New Required Fields**: Some fields now have stricter validation
- ⚠️ **API Response Changes**: Some endpoints return different response formats

### **New Dependencies**
- No new external dependencies added
- Uses existing Django and DRF features

## 🔗 Related Documentation

- [API Documentation](./COMPLETE_API_DOCUMENTATION.md)
- [SMS Integration Guide](./BEEM_SMS_INTEGRATION_SUMMARY.md)
- [Admin Setup Guide](./ADMIN_SETUP_GUIDE.md)
- [Frontend Integration Guide](./FRONTEND_INTEGRATION_DOCUMENTATION.md)

---

**Branch**: `tenant_issue`  
**Last Updated**: October 19, 2025  
**Status**: Ready for Production  
**Next Steps**: Merge to main and deploy
