# Frontend Integration Guide - Tenant Issue Changes

## 🎯 Overview

This guide provides specific instructions for frontend developers to integrate the new tenant issue changes, including new API endpoints, UI components, and workflow updates.

## 🚀 New API Endpoints to Integrate

### 1. **Sender ID Request Management**

#### **Create Sender ID Request**
```javascript
// POST /api/messaging/sender-requests/
const createSenderIDRequest = async (requestData) => {
    const response = await fetch('/api/messaging/sender-requests/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            request_type: 'default',
            requested_sender_id: 'Taarifa-SMS',
            sample_content: 'A test use case for the sender name purposely used for information transfer.',
            business_justification: 'Requesting to use the default sender ID for SMS messaging.'
        })
    });
    
    if (!response.ok) {
        const errors = await response.json();
        throw new Error(`Request failed: ${JSON.stringify(errors)}`);
    }
    
    return await response.json();
};
```

#### **Get Sender ID Request Status**
```javascript
// GET /api/messaging/sender-requests/status/
const getSenderIDStatus = async () => {
    const response = await fetch('/api/messaging/sender-requests/status/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        }
    });
    
    return await response.json();
};
```

#### **List Sender ID Requests**
```javascript
// GET /api/messaging/sender-requests/
const getSenderIDRequests = async () => {
    const response = await fetch('/api/messaging/sender-requests/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        }
    });
    
    return await response.json();
};
```

### 2. **Updated Profile Management**

#### **Update User Profile (Fixed Validation)**
```javascript
// PUT /api/auth/profile/
const updateProfile = async (profileData) => {
    const response = await fetch('/api/auth/profile/', {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
    });
    
    if (!response.ok) {
        const errors = await response.json();
        // Handle validation errors
        console.error('Profile update validation errors:', errors);
        throw new Error(`Profile update failed: ${JSON.stringify(errors)}`);
    }
    
    return await response.json();
};
```

## 🎨 New UI Components to Implement

### 1. **Sender ID Request Form Component**

```jsx
// components/SenderIDRequestForm.jsx
import React, { useState } from 'react';

const SenderIDRequestForm = ({ onSuccess, onError }) => {
    const [formData, setFormData] = useState({
        request_type: 'default',
        requested_sender_id: 'Taarifa-SMS',
        sample_content: 'A test use case for the sender name purposely used for information transfer.',
        business_justification: ''
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const response = await fetch('/api/messaging/sender-requests/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errors = await response.json();
                throw new Error(`Request failed: ${JSON.stringify(errors)}`);
            }
            
            const result = await response.json();
            onSuccess(result);
        } catch (error) {
            onError(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="sender-id-request-form">
            <h3>Request Sender ID</h3>
            
            <div className="form-group">
                <label>Request Type</label>
                <select 
                    value={formData.request_type}
                    onChange={(e) => setFormData({...formData, request_type: e.target.value})}
                    disabled
                >
                    <option value="default">Default (Taarifa-SMS)</option>
                </select>
            </div>
            
            <div className="form-group">
                <label>Requested Sender ID</label>
                <input 
                    type="text"
                    value={formData.requested_sender_id}
                    onChange={(e) => setFormData({...formData, requested_sender_id: e.target.value})}
                    disabled
                />
            </div>
            
            <div className="form-group">
                <label>Sample Content</label>
                <textarea 
                    value={formData.sample_content}
                    onChange={(e) => setFormData({...formData, sample_content: e.target.value})}
                    rows={3}
                />
            </div>
            
            <div className="form-group">
                <label>Business Justification *</label>
                <textarea 
                    value={formData.business_justification}
                    onChange={(e) => setFormData({...formData, business_justification: e.target.value})}
                    rows={3}
                    required
                    placeholder="Explain why you need this sender ID..."
                />
            </div>
            
            <button type="submit" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Request'}
            </button>
        </form>
    );
};

export default SenderIDRequestForm;
```

### 2. **Sender ID Status Component**

```jsx
// components/SenderIDStatus.jsx
import React, { useState, useEffect } from 'react';

const SenderIDStatus = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchSenderIDStatus();
    }, []);

    const fetchSenderIDStatus = async () => {
        try {
            const response = await fetch('/api/messaging/sender-requests/status/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error('Failed to fetch sender ID status:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="sender-id-status">
            <h3>SMS & Sender ID Status</h3>
            
            <div className="status-card">
                <h4>SMS Balance</h4>
                <p>Credits: {status?.sms_balance?.credits || 0}</p>
                <p>Total Purchased: {status?.sms_balance?.total_purchased || 0}</p>
            </div>
            
            <div className="status-card">
                <h4>Sender ID Status</h4>
                {status?.sender_id_requests?.length > 0 ? (
                    <div>
                        <p>Status: {status.sender_id_requests[0].status}</p>
                        <p>Sender ID: {status.sender_id_requests[0].requested_sender_id}</p>
                        {status.sender_id_requests[0].status === 'rejected' && (
                            <p>Reason: {status.sender_id_requests[0].rejection_reason}</p>
                        )}
                    </div>
                ) : (
                    <p>No sender ID request found</p>
                )}
            </div>
        </div>
    );
};

export default SenderIDStatus;
```

### 3. **Admin Sender ID Approval Component**

```jsx
// components/AdminSenderIDApproval.jsx
import React, { useState, useEffect } from 'react';

const AdminSenderIDApproval = () => {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchRequests();
    }, []);

    const fetchRequests = async () => {
        try {
            const response = await fetch('/api/messaging/sender-requests/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            const data = await response.json();
            setRequests(data);
        } catch (error) {
            console.error('Failed to fetch requests:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (requestId) => {
        try {
            const response = await fetch(`/api/messaging/sender-requests/${requestId}/approve/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: 'approved',
                    admin_notes: 'Approved for use'
                })
            });
            
            if (response.ok) {
                fetchRequests(); // Refresh list
            }
        } catch (error) {
            console.error('Failed to approve request:', error);
        }
    };

    const handleReject = async (requestId) => {
        const reason = prompt('Enter rejection reason:');
        if (!reason) return;
        
        try {
            const response = await fetch(`/api/messaging/sender-requests/${requestId}/reject/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: 'rejected',
                    rejection_reason: reason
                })
            });
            
            if (response.ok) {
                fetchRequests(); // Refresh list
            }
        } catch (error) {
            console.error('Failed to reject request:', error);
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="admin-sender-id-approval">
            <h3>Sender ID Request Approval</h3>
            
            {requests.length === 0 ? (
                <p>No pending requests</p>
            ) : (
                <div className="requests-list">
                    {requests.map(request => (
                        <div key={request.id} className="request-card">
                            <h4>Request from: {request.user_email}</h4>
                            <p>Sender ID: {request.requested_sender_id}</p>
                            <p>Status: {request.status}</p>
                            <p>Sample Content: {request.sample_content}</p>
                            <p>Justification: {request.business_justification}</p>
                            
                            {request.status === 'pending' && (
                                <div className="action-buttons">
                                    <button 
                                        onClick={() => handleApprove(request.id)}
                                        className="approve-btn"
                                    >
                                        Approve
                                    </button>
                                    <button 
                                        onClick={() => handleReject(request.id)}
                                        className="reject-btn"
                                    >
                                        Reject
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AdminSenderIDApproval;
```

### 4. **Updated Profile Form Component**

```jsx
// components/ProfileForm.jsx (Updated)
import React, { useState, useEffect } from 'react';

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
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const response = await fetch('/api/auth/profile/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            const data = await response.json();
            setFormData(data);
        } catch (error) {
            console.error('Failed to fetch profile:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrors({});
        
        try {
            const response = await fetch('/api/auth/profile/', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                setErrors(errorData);
                return;
            }
            
            const result = await response.json();
            console.log('Profile updated successfully:', result);
        } catch (error) {
            console.error('Profile update failed:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="profile-form">
            <h3>Update Profile</h3>
            
            <div className="form-group">
                <label>Email *</label>
                <input 
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                />
                {errors.email && <span className="error">{errors.email[0]}</span>}
            </div>
            
            <div className="form-group">
                <label>First Name *</label>
                <input 
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                    required
                />
                {errors.first_name && <span className="error">{errors.first_name[0]}</span>}
            </div>
            
            <div className="form-group">
                <label>Last Name *</label>
                <input 
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                    required
                />
                {errors.last_name && <span className="error">{errors.last_name[0]}</span>}
            </div>
            
            <div className="form-group">
                <label>Phone Number</label>
                <input 
                    type="tel"
                    value={formData.phone_number}
                    onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                />
            </div>
            
            <div className="form-group">
                <label>Timezone</label>
                <select 
                    value={formData.timezone}
                    onChange={(e) => setFormData({...formData, timezone: e.target.value})}
                >
                    <option value="UTC">UTC</option>
                    <option value="Africa/Dar_es_Salaam">Africa/Dar_es_Salaam</option>
                </select>
            </div>
            
            <div className="form-group">
                <label>Bio</label>
                <textarea 
                    value={formData.bio}
                    onChange={(e) => setFormData({...formData, bio: e.target.value})}
                    rows={3}
                />
            </div>
            
            <div className="form-group">
                <label>
                    <input 
                        type="checkbox"
                        checked={formData.email_notifications}
                        onChange={(e) => setFormData({...formData, email_notifications: e.target.checked})}
                    />
                    Email Notifications
                </label>
                {errors.email_notifications && <span className="error">{errors.email_notifications[0]}</span>}
            </div>
            
            <div className="form-group">
                <label>
                    <input 
                        type="checkbox"
                        checked={formData.sms_notifications}
                        onChange={(e) => setFormData({...formData, sms_notifications: e.target.checked})}
                    />
                    SMS Notifications
                </label>
                {errors.sms_notifications && <span className="error">{errors.sms_notifications[0]}</span>}
            </div>
            
            <button type="submit" disabled={loading}>
                {loading ? 'Updating...' : 'Update Profile'}
            </button>
        </form>
    );
};

export default ProfileForm;
```

## 🔄 Updated User Workflow

### **New User Onboarding Flow**

```jsx
// components/UserOnboarding.jsx
import React, { useState, useEffect } from 'react';
import SenderIDRequestForm from './SenderIDRequestForm';
import SenderIDStatus from './SenderIDStatus';

const UserOnboarding = () => {
    const [userType, setUserType] = useState(null);
    const [step, setStep] = useState(1);

    useEffect(() => {
        // Check if user is admin/superadmin
        const user = JSON.parse(localStorage.getItem('user'));
        if (user?.is_staff || user?.is_superuser) {
            setUserType('admin');
            setStep(3); // Skip to ready state
        } else {
            setUserType('normal');
            setStep(1); // Start with workflow choice
        }
    }, []);

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <div className="workflow-choice">
                        <h3>Choose Your Workflow</h3>
                        <p>You can either request a sender ID first, or purchase SMS credits first.</p>
                        
                        <div className="workflow-options">
                            <button onClick={() => setStep(2)}>
                                Request Sender ID First
                            </button>
                            <button onClick={() => setStep(4)}>
                                Purchase SMS Credits First
                            </button>
                            <button onClick={() => setStep(5)}>
                                Do Both Simultaneously
                            </button>
                        </div>
                    </div>
                );
            
            case 2:
                return (
                    <div>
                        <h3>Step 1: Request Sender ID</h3>
                        <SenderIDRequestForm 
                            onSuccess={() => setStep(3)}
                            onError={(error) => console.error(error)}
                        />
                    </div>
                );
            
            case 3:
                return (
                    <div>
                        <h3>Ready to Use!</h3>
                        <SenderIDStatus />
                        <p>You can now send SMS messages.</p>
                    </div>
                );
            
            case 4:
                return (
                    <div>
                        <h3>Step 1: Purchase SMS Credits</h3>
                        <p>Redirect to SMS package purchase page...</p>
                        <button onClick={() => setStep(2)}>
                            Next: Request Sender ID
                        </button>
                    </div>
                );
            
            case 5:
                return (
                    <div>
                        <h3>Complete Setup</h3>
                        <div className="simultaneous-setup">
                            <div className="setup-section">
                                <h4>Request Sender ID</h4>
                                <SenderIDRequestForm 
                                    onSuccess={() => console.log('Sender ID requested')}
                                    onError={(error) => console.error(error)}
                                />
                            </div>
                            
                            <div className="setup-section">
                                <h4>Purchase SMS Credits</h4>
                                <p>Redirect to SMS package purchase page...</p>
                            </div>
                        </div>
                    </div>
                );
            
            default:
                return <div>Invalid step</div>;
        }
    };

    return (
        <div className="user-onboarding">
            {renderStep()}
        </div>
    );
};

export default UserOnboarding;
```

## 🎨 CSS Styles

```css
/* styles/sender-id-components.css */
.sender-id-request-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.sender-id-request-form .form-group {
    margin-bottom: 15px;
}

.sender-id-request-form label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.sender-id-request-form input,
.sender-id-request-form textarea,
.sender-id-request-form select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.sender-id-request-form button {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.sender-id-request-form button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.sender-id-status {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 20px 0;
}

.status-card {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
}

.status-card h4 {
    margin-top: 0;
    color: #333;
}

.admin-sender-id-approval {
    max-width: 800px;
    margin: 0 auto;
}

.requests-list {
    display: grid;
    gap: 15px;
}

.request-card {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background-color: #f9f9f9;
}

.action-buttons {
    margin-top: 10px;
}

.approve-btn {
    background-color: #28a745;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    margin-right: 10px;
    cursor: pointer;
}

.reject-btn {
    background-color: #dc3545;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.profile-form {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}

.profile-form .form-group {
    margin-bottom: 15px;
}

.profile-form .error {
    color: #dc3545;
    font-size: 14px;
    display: block;
    margin-top: 5px;
}

.workflow-choice {
    text-align: center;
    max-width: 500px;
    margin: 0 auto;
}

.workflow-options {
    display: grid;
    gap: 15px;
    margin-top: 20px;
}

.workflow-options button {
    padding: 15px;
    border: 2px solid #007bff;
    background-color: white;
    color: #007bff;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
}

.workflow-options button:hover {
    background-color: #007bff;
    color: white;
}

.simultaneous-setup {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.setup-section {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
}
```

## 🧪 Testing Integration

### **Test API Integration**

```javascript
// utils/api-test.js
export const testSenderIDAPI = async () => {
    const token = localStorage.getItem('access_token');
    
    try {
        // Test create request
        const createResponse = await fetch('/api/messaging/sender-requests/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                request_type: 'default',
                requested_sender_id: 'Taarifa-SMS',
                sample_content: 'Test content',
                business_justification: 'Test justification'
            })
        });
        
        console.log('Create request:', createResponse.status);
        
        // Test get status
        const statusResponse = await fetch('/api/messaging/sender-requests/status/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const statusData = await statusResponse.json();
        console.log('Status data:', statusData);
        
        return true;
    } catch (error) {
        console.error('API test failed:', error);
        return false;
    }
};
```

## 📋 Integration Checklist

### **Backend Integration**
- [ ] Pull latest changes from `tenant_issue` branch
- [ ] Run database migrations
- [ ] Setup shared sender ID for existing tenants
- [ ] Test all new API endpoints

### **Frontend Integration**
- [ ] Add new API service functions
- [ ] Implement SenderIDRequestForm component
- [ ] Implement SenderIDStatus component
- [ ] Implement AdminSenderIDApproval component
- [ ] Update ProfileForm with new validation
- [ ] Add CSS styles for new components
- [ ] Update user onboarding flow
- [ ] Test complete workflow

### **Testing**
- [ ] Test sender ID request creation
- [ ] Test sender ID status checking
- [ ] Test admin approval workflow
- [ ] Test profile update validation
- [ ] Test complete user workflow
- [ ] Test error handling

---

**Last Updated**: October 19, 2025  
**Version**: 1.0  
**Status**: Ready for Integration
