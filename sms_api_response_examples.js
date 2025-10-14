/**
 * SMS API Response Examples for Mifumo WMS
 *
 * This file contains all the expected response formats for SMS API endpoints.
 * Use this as a reference for frontend integration.
 */

// =============================================================================
// 1. SEND SMS ENDPOINT
// =============================================================================

/**
 * POST /api/messaging/sms/send/
 *
 * Request Body:
 * {
 *   "message": "Hello from Mifumo WMS!",
 *   "recipients": ["255700000001", "255700000002"],
 *   "sender_id": "MIFUMO",
 *   "template_id": "uuid-optional",
 *   "schedule_time": "2024-01-01T10:00:00Z",
 *   "encoding": 0
 * }
 */

// ✅ SUCCESS Response (200)
const sendSmsSuccessResponse = {
    "success": true,
    "message": "SMS sent successfully",
    "data": {
        "message_id": "550e8400-e29b-41d4-a716-446655440000",
        "provider": "beem",
        "recipients": [{
                "phone": "255700000001",
                "status": "sent",
                "provider_message_id": "beem_12345"
            },
            {
                "phone": "255700000002",
                "status": "sent",
                "provider_message_id": "beem_12346"
            }
        ],
        "total_recipients": 2,
        "successful_sends": 2,
        "failed_sends": 0,
        "cost": 0.02,
        "currency": "USD",
        "scheduled_time": null,
        "created_at": "2024-01-01T10:00:00Z"
    }
};

// ❌ ERROR Response (400) - Validation Error
const sendSmsValidationErrorResponse = {
    "success": false,
    "message": "Validation error",
    "errors": {
        "message": ["This field is required."],
        "recipients": ["This field is required."],
        "sender_id": ["This field is required."]
    }
};

// ❌ ERROR Response (400) - Invalid Phone Number
const sendSmsInvalidPhoneResponse = {
    "success": false,
    "message": "Invalid phone number format",
    "errors": {
        "recipients": ["Phone number must be in international format (e.g., 255700000001)"]
    }
};

// ❌ ERROR Response (400) - Sender ID Not Registered
const sendSmsSenderIdErrorResponse = {
    "success": false,
    "message": "Sender ID not registered or inactive",
    "errors": {
        "sender_id": ["Sender ID 'INVALID' is not registered with Beem Africa"]
    }
};

// ❌ ERROR Response (500) - Provider Error
const sendSmsProviderErrorResponse = {
    "success": false,
    "message": "SMS provider error",
    "error": "Beem Africa API returned error: Insufficient balance"
};

// =============================================================================
// 2. GET SMS BALANCE ENDPOINT
// =============================================================================

/**
 * GET /api/messaging/sms/balance/
 */

// ✅ SUCCESS Response (200)
const getBalanceSuccessResponse = {
    "success": true,
    "data": {
        "provider": "beem",
        "balance": 150.75,
        "currency": "USD",
        "last_updated": "2024-01-01T10:00:00Z",
        "account_status": "active"
    }
};

// ❌ ERROR Response (500) - Provider Error
const getBalanceErrorResponse = {
    "success": false,
    "message": "Failed to fetch balance",
    "error": "Beem Africa API error: Invalid credentials"
};

// =============================================================================
// 3. GET SMS STATS ENDPOINT
// =============================================================================

/**
 * GET /api/messaging/sms/stats/
 */

// ✅ SUCCESS Response (200)
const getStatsSuccessResponse = {
    "success": true,
    "data": {
        "total_sent": 1250,
        "total_delivered": 1180,
        "total_failed": 70,
        "delivery_rate": 94.4,
        "total_cost": 25.00,
        "currency": "USD",
        "period": {
            "start": "2024-01-01T00:00:00Z",
            "end": "2024-01-31T23:59:59Z"
        },
        "by_status": {
            "sent": 1250,
            "delivered": 1180,
            "failed": 70,
            "pending": 0
        },
        "by_provider": {
            "beem": 1250
        }
    }
};

// =============================================================================
// 4. TEST CONNECTION ENDPOINT
// =============================================================================

/**
 * GET /api/messaging/sms/test-connection/
 */

// ✅ SUCCESS Response (200)
const testConnectionSuccessResponse = {
    "success": true,
    "message": "SMS provider connection successful",
    "data": {
        "provider": "beem",
        "status": "connected",
        "response_time": 0.25,
        "api_version": "v1",
        "last_checked": "2024-01-01T10:00:00Z"
    }
};

// ❌ ERROR Response (500) - Connection Failed
const testConnectionErrorResponse = {
    "success": false,
    "message": "SMS provider connection failed",
    "error": "Beem Africa API error: Invalid API key"
};

// =============================================================================
// 5. VALIDATE PHONE NUMBER ENDPOINT
// =============================================================================

/**
 * POST /api/messaging/sms/validate-phone/
 *
 * Request Body:
 * {
 *   "phone": "255700000001"
 * }
 */

// ✅ SUCCESS Response (200) - Valid Phone
const validatePhoneSuccessResponse = {
    "success": true,
    "message": "Phone number is valid",
    "data": {
        "phone": "255700000001",
        "is_valid": true,
        "formatted": "+255700000001",
        "country_code": "255",
        "national_number": "700000001",
        "country": "Tanzania",
        "carrier": "Vodacom"
    }
};

// ❌ ERROR Response (400) - Invalid Phone
const validatePhoneErrorResponse = {
    "success": false,
    "message": "Phone number is invalid",
    "errors": {
        "phone": ["Invalid phone number format. Use international format (e.g., 255700000001)"]
    }
};

// =============================================================================
// 6. GET SMS DELIVERY STATUS ENDPOINT
// =============================================================================

/**
 * GET /api/messaging/sms/{message_id}/status/
 */

// ✅ SUCCESS Response (200)
const getDeliveryStatusSuccessResponse = {
    "success": true,
    "data": {
        "message_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "delivered",
        "provider": "beem",
        "provider_message_id": "beem_12345",
        "delivery_time": "2024-01-01T10:01:30Z",
        "cost": 0.01,
        "currency": "USD",
        "recipients": [{
            "phone": "255700000001",
            "status": "delivered",
            "delivery_time": "2024-01-01T10:01:30Z",
            "error_code": null,
            "error_message": null
        }]
    }
};

// ❌ ERROR Response (404) - Message Not Found
const getDeliveryStatusNotFoundResponse = {
    "success": false,
    "message": "Message not found",
    "error": "Message with ID '550e8400-e29b-41d4-a716-446655440000' not found"
};

// =============================================================================
// 7. COMMON ERROR RESPONSES
// =============================================================================

// 401 Unauthorized
const unauthorizedResponse = {
    "detail": "Authentication credentials were not provided."
};

// 403 Forbidden
const forbiddenResponse = {
    "detail": "You do not have permission to perform this action."
};

// 404 Not Found
const notFoundResponse = {
    "detail": "Not found."
};

// 500 Internal Server Error
const internalServerErrorResponse = {
    "success": false,
    "message": "Internal server error",
    "error": "An unexpected error occurred"
};

// =============================================================================
// 8. FRONTEND INTEGRATION EXAMPLES
// =============================================================================

/**
 * Example frontend functions for SMS API integration
 */

// Send SMS
async function sendSMS(message, recipients, senderId) {
    try {
        const response = await fetch('/api/messaging/sms/send/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                recipients: recipients,
                sender_id: senderId
            })
        });

        const data = await response.json();

        if (data.success) {
            console.log('SMS sent successfully:', data.data);
            return {
                success: true,
                data: data.data
            };
        } else {
            console.error('SMS send failed:', data.message, data.errors);
            return {
                success: false,
                error: data.message,
                errors: data.errors
            };
        }
    } catch (error) {
        console.error('SMS send error:', error);
        return {
            success: false,
            error: 'Network error'
        };
    }
}

// Get SMS Balance
async function getSMSBalance() {
    try {
        const response = await fetch('/api/messaging/sms/balance/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        const data = await response.json();

        if (data.success) {
            return {
                success: true,
                balance: data.data.balance,
                currency: data.data.currency
            };
        } else {
            return {
                success: false,
                error: data.message
            };
        }
    } catch (error) {
        return {
            success: false,
            error: 'Network error'
        };
    }
}

// Get SMS Stats
async function getSMSStats() {
    try {
        const response = await fetch('/api/messaging/sms/stats/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        const data = await response.json();

        if (data.success) {
            return {
                success: true,
                stats: data.data
            };
        } else {
            return {
                success: false,
                error: data.message
            };
        }
    } catch (error) {
        return {
            success: false,
            error: 'Network error'
        };
    }
}

// Validate Phone Number
async function validatePhoneNumber(phone) {
    try {
        const response = await fetch('/api/messaging/sms/validate-phone/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone: phone
            })
        });

        const data = await response.json();

        if (data.success) {
            return {
                success: true,
                isValid: data.data.is_valid,
                formatted: data.data.formatted
            };
        } else {
            return {
                success: false,
                error: data.message,
                errors: data.errors
            };
        }
    } catch (error) {
        return {
            success: false,
            error: 'Network error'
        };
    }
}

// Test SMS Connection
async function testSMSConnection() {
    try {
        const response = await fetch('/api/messaging/sms/test-connection/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        const data = await response.json();

        if (data.success) {
            return {
                success: true,
                status: data.data.status,
                responseTime: data.data.response_time
            };
        } else {
            return {
                success: false,
                error: data.message
            };
        }
    } catch (error) {
        return {
            success: false,
            error: 'Network error'
        };
    }
}

// Get SMS Delivery Status
async function getSMSDeliveryStatus(messageId) {
    try {
        const response = await fetch(`/api/messaging/sms/${messageId}/status/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });

        const data = await response.json();

        if (data.success) {
            return {
                success: true,
                status: data.data.status,
                deliveryTime: data.data.delivery_time
            };
        } else {
            return {
                success: false,
                error: data.message
            };
        }
    } catch (error) {
        return {
            success: false,
            error: 'Network error'
        };
    }
}

// Helper function to get auth token
function getAuthToken() {
    return localStorage.getItem('authToken') || '';
}

// =============================================================================
// 9. USAGE EXAMPLES
// =============================================================================

// Example: Send SMS
async function exampleSendSMS() {
    const result = await sendSMS(
        "Hello from Mifumo WMS!",
        ["255700000001", "255700000002"],
        "MIFUMO"
    );

    if (result.success) {
        console.log('SMS sent successfully:', result.data.message_id);
    } else {
        console.error('Failed to send SMS:', result.error);
    }
}

// Example: Check Balance
async function exampleCheckBalance() {
    const result = await getSMSBalance();

    if (result.success) {
        console.log(`Balance: ${result.balance} ${result.currency}`);
    } else {
        console.error('Failed to get balance:', result.error);
    }
}

// Example: Validate Phone
async function exampleValidatePhone() {
    const result = await validatePhoneNumber("255700000001");

    if (result.success && result.isValid) {
        console.log('Phone is valid:', result.formatted);
    } else {
        console.error('Phone is invalid:', result.error);
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sendSMS,
        getSMSBalance,
        getSMSStats,
        validatePhoneNumber,
        testSMSConnection,
        getSMSDeliveryStatus
    };
}