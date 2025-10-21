/**
 * Mifumo SMS Frontend SDK
 * A comprehensive JavaScript SDK for integrating with Mifumo SMS Backend API
 */

class MifumoSDK {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL || process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
    this.accessToken = null;
    this.refreshToken = null;
    this.onTokenRefresh = options.onTokenRefresh || null;
    this.autoRefresh = options.autoRefresh !== false;
    
    // Set up automatic token refresh
    if (this.autoRefresh) {
      this.setupTokenRefresh();
    }
  }

  // Authentication Methods
  async login(email, password) {
    const response = await this.request('/accounts/login/', 'POST', {
      email,
      password
    });
    
    if (response.success) {
      this.setTokens(response.access, response.refresh);
      return response;
    }
    throw new Error(response.error || 'Login failed');
  }

  async register(userData) {
    const response = await this.request('/accounts/register/', 'POST', userData);
    
    if (response.success) {
      this.setTokens(response.access, response.refresh);
      return response;
    }
    throw new Error(response.error || 'Registration failed');
  }

  async logout() {
    try {
      await this.request('/accounts/logout/', 'POST');
    } finally {
      this.clearTokens();
    }
  }

  // Token Management
  setTokens(access, refresh) {
    this.accessToken = access;
    this.refreshToken = refresh;
    localStorage.setItem('mifumo_access_token', access);
    localStorage.setItem('mifumo_refresh_token', refresh);
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('mifumo_access_token');
    localStorage.removeItem('mifumo_refresh_token');
  }

  loadTokens() {
    this.accessToken = localStorage.getItem('mifumo_access_token');
    this.refreshToken = localStorage.getItem('mifumo_refresh_token');
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.request('/accounts/token/refresh/', 'POST', {
      refresh: this.refreshToken
    }, false); // Don't use auth header for refresh

    if (response.access) {
      this.accessToken = response.access;
      localStorage.setItem('mifumo_access_token', response.access);
      
      if (this.onTokenRefresh) {
        this.onTokenRefresh(response.access);
      }
      
      return response.access;
    }
    throw new Error('Token refresh failed');
  }

  setupTokenRefresh() {
    // Refresh token 5 minutes before expiry
    setInterval(async () => {
      if (this.accessToken && this.refreshToken) {
        try {
          await this.refreshAccessToken();
        } catch (error) {
          console.warn('Token refresh failed:', error);
          this.clearTokens();
        }
      }
    }, 55 * 60 * 1000); // 55 minutes
  }

  // SMS Packages
  async getSMSPackages() {
    return this.request('/billing/sms/packages/');
  }

  async getSMSPackage(id) {
    return this.request(`/billing/sms/packages/${id}/`);
  }

  // SMS Balance & Usage
  async getSMSBalance() {
    return this.request('/billing/sms/balance/');
  }

  async getUsageStatistics() {
    return this.request('/billing/sms/usage/statistics/');
  }

  async getUsageRecords(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/billing/sms/usage/records/?${params}`);
  }

  // Payment Methods
  async getPaymentProviders() {
    return this.request('/billing/payments/providers/');
  }

  async purchasePackage(packageId, paymentMethod) {
    return this.request('/billing/payments/initiate/', 'POST', {
      package_id: packageId,
      mobile_money_provider: paymentMethod
    });
  }

  async calculateCustomPricing(credits) {
    return this.request('/billing/payments/custom-sms/calculate/', 'POST', {
      credits
    });
  }

  async initiateCustomPurchase(credits, paymentMethod) {
    return this.request('/billing/payments/custom-sms/initiate/', 'POST', {
      credits,
      mobile_money_provider: paymentMethod
    });
  }

  async checkPaymentStatus(orderId) {
    return this.request(`/billing/payments/verify/${orderId}/`);
  }

  async getPaymentProgress(transactionId) {
    return this.request(`/billing/payments/transactions/${transactionId}/progress/`);
  }

  async cancelPayment(transactionId) {
    return this.request(`/billing/payments/transactions/${transactionId}/cancel/`, 'POST');
  }

  async getActivePayments() {
    return this.request('/billing/payments/active/');
  }

  // SMS Sending
  async sendSMS(recipients, message, senderId) {
    return this.request('/messaging/sms/send/', 'POST', {
      recipients: Array.isArray(recipients) ? recipients : [recipients],
      message,
      sender_id: senderId
    });
  }

  async getSMSHistory(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/messaging/sms/messages/?${params}`);
  }

  async getSMSMessage(id) {
    return this.request(`/messaging/sms/messages/${id}/`);
  }

  async getDeliveryReports(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/messaging/sms/delivery-reports/?${params}`);
  }

  // Sender ID Management
  async getSenderIDs() {
    return this.request('/messaging/sender-ids/');
  }

  async requestSenderID(senderId, businessName, contactPhone, purpose = 'Marketing and notifications') {
    return this.request('/messaging/sender-ids/request/', 'POST', {
      requested_sender_id: senderId,
      business_name: businessName,
      contact_phone: contactPhone,
      purpose
    });
  }

  async getSenderIDStatus(requestId) {
    return this.request(`/messaging/sender-ids/${requestId}/status/`);
  }

  async updateSenderID(id, data) {
    return this.request(`/messaging/sender-ids/${id}/`, 'PUT', data);
  }

  async deleteSenderID(id) {
    return this.request(`/messaging/sender-ids/${id}/`, 'DELETE');
  }

  // Tenant Management
  async getTenantProfile() {
    return this.request('/tenants/profile/');
  }

  async updateTenantProfile(data) {
    return this.request('/tenants/profile/', 'PUT', data);
  }

  async getTenantMembers() {
    return this.request('/tenants/members/');
  }

  async inviteMember(email, role = 'member') {
    return this.request('/tenants/members/invite/', 'POST', {
      email,
      role
    });
  }

  async updateMemberRole(memberId, role) {
    return this.request(`/tenants/members/${memberId}/`, 'PUT', {
      role
    });
  }

  async removeMember(memberId) {
    return this.request(`/tenants/members/${memberId}/`, 'DELETE');
  }

  // Billing & Analytics
  async getBillingOverview() {
    return this.request('/billing/overview/');
  }

  async getPurchaseHistory(filters = {}) {
    const params = new URLSearchParams(filters);
    return this.request(`/billing/sms/purchases/history/?${params}`);
  }

  async getPurchase(id) {
    return this.request(`/billing/sms/purchases/${id}/`);
  }

  async getBillingPlans() {
    return this.request('/billing/plans/');
  }

  async getSubscription() {
    return this.request('/billing/subscription/');
  }

  // User Profile
  async getUserProfile() {
    return this.request('/accounts/profile/');
  }

  async updateUserProfile(data) {
    return this.request('/accounts/profile/', 'PUT', data);
  }

  // Utility Methods
  async request(endpoint, method = 'GET', data = null, useAuth = true) {
    const url = `${this.baseURL}${endpoint}`;
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      }
    };

    if (useAuth && this.accessToken) {
      options.headers.Authorization = `Bearer ${this.accessToken}`;
    }

    if (data && method !== 'GET') {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      const result = await response.json();

      if (response.status === 401 && useAuth && this.refreshToken) {
        // Try to refresh token and retry
        try {
          await this.refreshAccessToken();
          options.headers.Authorization = `Bearer ${this.accessToken}`;
          const retryResponse = await fetch(url, options);
          return await retryResponse.json();
        } catch (refreshError) {
          this.clearTokens();
          throw new Error('Authentication failed');
        }
      }

      if (!response.ok) {
        throw new Error(result.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return result;
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Polling Methods
  pollPaymentStatus(orderId, onUpdate, onComplete, onError, interval = 5000) {
    const poll = async () => {
      try {
        const status = await this.checkPaymentStatus(orderId);
        onUpdate(status.data);

        if (status.data.status === 'completed') {
          onComplete(status.data);
          return;
        } else if (status.data.status === 'failed' || status.data.status === 'cancelled') {
          onError(status.data);
          return;
        }

        setTimeout(poll, interval);
      } catch (error) {
        onError(error);
      }
    };

    poll();
  }

  pollBalance(onUpdate, interval = 30000) {
    const poll = async () => {
      try {
        const balance = await this.getSMSBalance();
        onUpdate(balance.data);
      } catch (error) {
        console.warn('Balance polling failed:', error);
      }
    };

    poll(); // Initial call
    return setInterval(poll, interval);
  }

  // Validation Helpers
  validatePhoneNumber(phone) {
    const phoneRegex = /^(\+255|0)[0-9]{9}$/;
    return phoneRegex.test(phone);
  }

  formatPhoneNumber(phone) {
    // Convert 0XXXXXXXXX to +255XXXXXXXXX
    if (phone.startsWith('0')) {
      return '+255' + phone.substring(1);
    }
    return phone;
  }

  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Error Handling
  handleError(error, context = '') {
    console.error(`Mifumo SDK Error${context ? ` in ${context}` : ''}:`, error);
    
    if (error.message.includes('Authentication failed')) {
      this.clearTokens();
      // Redirect to login or trigger login modal
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    return {
      success: false,
      error: error.message,
      context
    };
  }
}

// React Hook for using the SDK
export const useMifumoSDK = (baseURL, options) => {
  const [sdk] = useState(() => new MifumoSDK(baseURL, options));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load tokens on mount
    sdk.loadTokens();
    if (sdk.accessToken) {
      setIsAuthenticated(true);
      // Optionally load user profile
      sdk.getUserProfile()
        .then(response => setUser(response.user))
        .catch(err => console.warn('Failed to load user profile:', err));
    }
  }, [sdk]);

  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await sdk.login(email, password);
      setIsAuthenticated(true);
      setUser(response.user);
      return response;
    } catch (err) {
      const error = sdk.handleError(err, 'login');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await sdk.logout();
    } finally {
      setIsAuthenticated(false);
      setUser(null);
      setLoading(false);
    }
  };

  return {
    sdk,
    isAuthenticated,
    user,
    loading,
    error,
    login,
    logout,
    setError
  };
};

// Export the SDK class
export default MifumoSDK;

// Usage Examples:

/*
// Basic usage
const sdk = new MifumoSDK('https://api.mifumo.com');

// Login
const response = await sdk.login('user@example.com', 'password');

// Send SMS
const smsResponse = await sdk.sendSMS('+255123456789', 'Hello!', 'MIFUMO');

// Get packages
const packages = await sdk.getSMSPackages();

// Purchase package
const purchase = await sdk.purchasePackage('package-id', 'vodacom');

// Poll payment status
sdk.pollPaymentStatus(
  purchase.data.order_id,
  (status) => console.log('Payment status:', status.status),
  (completed) => console.log('Payment completed!'),
  (error) => console.error('Payment failed:', error)
);

// React Hook usage
function App() {
  const { sdk, isAuthenticated, user, login, logout } = useMifumoSDK();
  
  if (!isAuthenticated) {
    return <LoginForm onLogin={login} />;
  }
  
  return <Dashboard user={user} sdk={sdk} onLogout={logout} />;
}
*/
