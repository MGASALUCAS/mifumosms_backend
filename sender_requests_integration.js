/**
 * Sender Name Requests API Integration
 *
 * This file provides ready-to-use JavaScript functions for integrating
 * sender name requests functionality into your existing web page.
 *
 * Usage:
 * 1. Include this file in your HTML
 * 2. Call the functions as needed
 * 3. Customize the UI elements to match your design
 */

class SenderRequestsAPI {
    constructor(baseURL = 'http://127.0.0.1:8000/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('accessToken');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('accessToken', token);
    }

    // Get authentication headers
    getHeaders(includeContentType = true) {
        const headers = {
            'Authorization': `Bearer ${this.token}`
        };

        if (includeContentType) {
            headers['Content-Type'] = 'application/json';
        }

        return headers;
    }

    // Handle API response
    async handleResponse(response) {
        const data = await response.json();

        if (response.ok) {
            return {
                success: true,
                data: data.data || data,
                message: data.message
            };
        } else {
            return {
                success: false,
                message: data.message || data.detail || 'An error occurred',
                errors: data.errors || null
            };
        }
    }

    // 1. Submit Sender Name Request
    async submitRequest(formData) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/submit/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                },
                body: formData
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }

    // 2. Get User Requests
    async getRequests(page = 1, status = null, search = null) {
        try {
            let url = `${this.baseURL}/messaging/sender-requests/?page=${page}`;

            if (status) url += `&status=${status}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;

            const response = await fetch(url, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }

    // 3. Get Request Details
    async getRequestDetails(requestId) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/${requestId}/`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }

    // 4. Update Request
    async updateRequest(requestId, updateData) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/${requestId}/update/`, {
                method: 'PUT',
                headers: this.getHeaders(),
                body: JSON.stringify(updateData)
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }

    // 5. Delete Request
    async deleteRequest(requestId) {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/${requestId}/delete/`, {
                method: 'DELETE',
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }

    // 6. Get Statistics
    async getStatistics() {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/stats/`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }

    // 7. Get Admin Dashboard
    async getAdminDashboard() {
        try {
            const response = await fetch(`${this.baseURL}/messaging/sender-requests/admin/dashboard/`, {
                headers: this.getHeaders()
            });

            return await this.handleResponse(response);
        } catch (error) {
            return {
                success: false,
                message: 'Network error: ' + error.message
            };
        }
    }
}

// Initialize the API
const senderRequestsAPI = new SenderRequestsAPI();

// Utility Functions for UI Integration

/**
 * Create FormData for file upload
 */
function createFormData(senderName, useCase, files = []) {
    const formData = new FormData();
    formData.append('sender_name', senderName);
    formData.append('use_case', useCase);

    files.forEach(file => {
        formData.append('supporting_documents', file);
    });

    return formData;
}

/**
 * Validate sender name
 */
function validateSenderName(senderName) {
    if (!senderName) return 'Sender name is required';
    if (senderName.length > 11) return 'Sender name cannot exceed 11 characters';
    if (!/^[a-zA-Z0-9]+$/.test(senderName)) return 'Sender name must contain only alphanumeric characters';
    return null;
}

/**
 * Validate use case
 */
function validateUseCase(useCase) {
    if (!useCase) return 'Use case is required';
    if (useCase.length < 10) return 'Use case must be at least 10 characters long';
    if (useCase.length > 1000) return 'Use case cannot exceed 1000 characters';
    return null;
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status) {
    const statusClasses = {
        'pending': 'status-pending',
        'approved': 'status-approved',
        'rejected': 'status-rejected',
        'requires_changes': 'status-requires-changes'
    };

    const statusLabels = {
        'pending': 'Pending',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'requires_changes': 'Requires Changes'
    };

    return `<span class="status-badge ${statusClasses[status]}">${statusLabels[status]}</span>`;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Example Usage Functions

/**
 * Example: Submit a new request
 */
async function submitNewRequest() {
    const senderName = document.getElementById('senderName').value;
    const useCase = document.getElementById('useCase').value;
    const fileInput = document.getElementById('fileInput');

    // Validate inputs
    const senderNameError = validateSenderName(senderName);
    if (senderNameError) {
        showError(senderNameError);
        return;
    }

    const useCaseError = validateUseCase(useCase);
    if (useCaseError) {
        showError(useCaseError);
        return;
    }

    // Create form data
    const files = Array.from(fileInput.files);
    const formData = createFormData(senderName, useCase, files);

    // Show loading
    showLoading(true);

    // Submit request
    const result = await senderRequestsAPI.submitRequest(formData);

    // Hide loading
    showLoading(false);

    if (result.success) {
        showSuccess('Request submitted successfully!');
        // Clear form
        document.getElementById('senderName').value = '';
        document.getElementById('useCase').value = '';
        fileInput.value = '';
        // Refresh requests list
        loadUserRequests();
    } else {
        showError(result.message);
    }
}

/**
 * Example: Load user requests
 */
async function loadUserRequests(page = 1) {
    showLoading(true);

    const result = await senderRequestsAPI.getRequests(page);

    showLoading(false);

    if (result.success) {
        displayRequests(result.data.results);
        updatePagination(result.data);
    } else {
        showError(result.message);
    }
}

/**
 * Example: Load statistics
 */
async function loadStatistics() {
    const result = await senderRequestsAPI.getStatistics();

    if (result.success) {
        displayStatistics(result.data);
    } else {
        showError(result.message);
    }
}

/**
 * Example: Load admin dashboard
 */
async function loadAdminDashboard() {
    const result = await senderRequestsAPI.getAdminDashboard();

    if (result.success) {
        displayAdminDashboard(result.data);
    } else {
        showError(result.message);
    }
}

// UI Helper Functions (customize these for your design)

function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

function showSuccess(message) {
    // Customize this to match your UI
    alert('Success: ' + message);
}

function showError(message) {
    // Customize this to match your UI
    alert('Error: ' + message);
}

function displayRequests(requests) {
    const container = document.getElementById('requestsList');
    if (!container) return;

    if (requests.length === 0) {
        container.innerHTML = '<p>No requests found</p>';
        return;
    }

    const html = requests.map(request => `
        <div class="request-item">
            <h3>${request.sender_name}</h3>
            <p>${getStatusBadge(request.status)}</p>
            <p>${request.use_case.substring(0, 100)}...</p>
            <p>Created: ${formatDate(request.created_at)}</p>
            <button onclick="viewRequest('${request.id}')">View Details</button>
            ${request.status === 'pending' ?
			`<button onclick="editRequest('${request.id}')">Edit</button>` :
			''
		}
        </div>
    `).join('');

    container.innerHTML = html;
}

function displayStatistics(stats) {
    const container = document.getElementById('statsContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="stat-item">
            <h3>${stats.total_requests}</h3>
            <p>Total Requests</p>
        </div>
        <div class="stat-item">
            <h3>${stats.pending_requests}</h3>
            <p>Pending</p>
        </div>
        <div class="stat-item">
            <h3>${stats.approved_requests}</h3>
            <p>Approved</p>
        </div>
        <div class="stat-item">
            <h3>${stats.rejected_requests}</h3>
            <p>Rejected</p>
        </div>
    `;
}

function displayAdminDashboard(data) {
    const container = document.getElementById('adminContainer');
    if (!container) return;

    container.innerHTML = `
        <h2>Admin Dashboard</h2>
        <p>Welcome, ${data.admin_user}! Managing requests for ${data.tenant_name}</p>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>${data.stats.total_requests}</h3>
                <p>Total Requests</p>
            </div>
            <div class="stat-card">
                <h3>${data.stats.pending_requests}</h3>
                <p>Pending Review</p>
            </div>
            <div class="stat-card">
                <h3>${data.stats.approved_requests}</h3>
                <p>Approved</p>
            </div>
            <div class="stat-card">
                <h3>${data.stats.rejected_requests}</h3>
                <p>Rejected</p>
            </div>
        </div>

        <h3>Recent Requests</h3>
        <div id="adminRequestsList"></div>
    `;

    // Display recent requests
    if (data.recent_requests && data.recent_requests.length > 0) {
        const requestsList = document.getElementById('adminRequestsList');
        const html = data.recent_requests.map(request => `
            <div class="admin-request-item">
                <h4>${request.sender_name}</h4>
                <p>${getStatusBadge(request.status)}</p>
                <p>User: ${request.created_by ? request.created_by.email : 'Unknown'}</p>
                <p>Created: ${formatDate(request.created_at)}</p>
                <button onclick="viewRequest('${request.id}')">View</button>
                ${request.status === 'pending' ?
				`<button onclick="approveRequest('${request.id}')">Approve</button>
                     <button onclick="rejectRequest('${request.id}')">Reject</button>` :
				''
			}
            </div>
        `).join('');

        requestsList.innerHTML = html;
    }
}

function updatePagination(data) {
    const container = document.getElementById('pagination');
    if (!container) return;

    if (data.total_pages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    if (data.has_previous) {
        html += `<button onclick="loadUserRequests(${data.page - 1})">Previous</button>`;
    }

    for (let i = 1; i <= data.total_pages; i++) {
        html += `<button class="${i === data.page ? 'active' : ''}" onclick="loadUserRequests(${i})">${i}</button>`;
    }

    if (data.has_next) {
        html += `<button onclick="loadUserRequests(${data.page + 1})">Next</button>`;
    }

    container.innerHTML = html;
}

// Action Functions

async function viewRequest(requestId) {
    const result = await senderRequestsAPI.getRequestDetails(requestId);

    if (result.success) {
        // Display request details in modal or new page
        console.log('Request details:', result.data);
        // Implement your UI for displaying request details
    } else {
        showError(result.message);
    }
}

async function editRequest(requestId) {
    // Implement edit functionality
    console.log('Edit request:', requestId);
}

async function approveRequest(requestId) {
    // Implement approve functionality
    console.log('Approve request:', requestId);
}

async function rejectRequest(requestId) {
    // Implement reject functionality
    console.log('Reject request:', requestId);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    if (!senderRequestsAPI.token) {
        // Redirect to login or show login form
        console.log('User not authenticated');
        return;
    }

    // Load initial data
    loadUserRequests();
    loadStatistics();
});

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SenderRequestsAPI,
        senderRequestsAPI
    };
}