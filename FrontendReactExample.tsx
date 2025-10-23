import React, { useState, useEffect, useCallback } from 'react';
import { 
  DashboardOverviewResponse, 
  RecentActivityResponse, 
  PerformanceOverviewResponse,
  SenderStatsResponse,
  SMSBalance,
  UseDashboardReturn,
  UseActivityReturn,
  UseSenderStatsReturn
} from './frontend-types';

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8001/api';

// API Client
class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setToken(token: string) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Authentication
  async login(email: string, password: string) {
    return this.request<{
      message: string;
      tokens: { access: string; refresh: string };
      user: any;
    }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  // Dashboard
  async getDashboardOverview() {
    return this.request<DashboardOverviewResponse>('/messaging/dashboard/overview/');
  }

  async getDashboardMetrics() {
    return this.request<any>('/messaging/dashboard/metrics/');
  }

  // Activity
  async getRecentActivity() {
    return this.request<RecentActivityResponse>('/messaging/activity/recent/');
  }

  // Performance
  async getPerformanceOverview() {
    return this.request<PerformanceOverviewResponse>('/messaging/performance/overview/');
  }

  // Sender IDs
  async getSenderStats() {
    return this.request<SenderStatsResponse>('/messaging/sender-requests/stats/');
  }

  // Billing
  async getSMSBalance() {
    return this.request<SMSBalance>('/billing/sms/balance/');
  }
}

// Create API client instance
const apiClient = new APIClient(API_BASE_URL);

// Custom Hooks
export const useDashboard = (): UseDashboardReturn => {
  const [dashboardData, setDashboardData] = useState<DashboardOverviewResponse['data'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getDashboardOverview();
      setDashboardData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return {
    dashboardData,
    loading,
    error,
    refetch: fetchDashboardData,
  };
};

export const useActivity = (): UseActivityReturn => {
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [liveCount, setLiveCount] = useState(0);

  const fetchActivities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getRecentActivity();
      setActivities(response.data.activities);
      setHasMore(response.data.has_more);
      setTotalCount(response.data.total_count);
      setLiveCount(response.data.live_count);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch activities');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActivities();
  }, [fetchActivities]);

  return {
    activities,
    loading,
    error,
    hasMore,
    totalCount,
    liveCount,
    refetch: fetchActivities,
  };
};

export const useSenderStats = (): UseSenderStatsReturn => {
  const [stats, setStats] = useState<SenderStatsResponse['data'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getSenderStats();
      setStats(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sender stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
};

// Components
export const DashboardOverview: React.FC = () => {
  const { dashboardData, loading, error } = useDashboard();

  if (loading) return <div className="loading">Loading dashboard...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!dashboardData) return <div>No data available</div>;

  return (
    <div className="dashboard-overview">
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Messages</h3>
          <div className="metric-value">{dashboardData.metrics.total_messages}</div>
        </div>
        <div className="metric-card">
          <h3>Active Contacts</h3>
          <div className="metric-value">{dashboardData.metrics.active_contacts}</div>
        </div>
        <div className="metric-card">
          <h3>Sender IDs</h3>
          <div className="metric-value">{dashboardData.metrics.sender_ids_this_month}</div>
        </div>
        <div className="metric-card">
          <h3>SMS Credits</h3>
          <div className="metric-value">{dashboardData.metrics.current_credits}</div>
        </div>
      </div>

      <div className="recent-campaigns">
        <h3>Recent Campaigns</h3>
        {dashboardData.recent_campaigns.map(campaign => (
          <div key={campaign.id} className="campaign-item">
            <h4>{campaign.name}</h4>
            <p>Status: {campaign.status}</p>
            <p>Sent: {campaign.sent} | Delivered: {campaign.delivered}</p>
            <p>Created: {campaign.created_at_human}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export const ActivityFeed: React.FC = () => {
  const { activities, loading, error, liveCount } = useActivity();

  if (loading) return <div className="loading">Loading activities...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="activity-feed">
      <div className="activity-header">
        <h3>Recent Activity</h3>
        {liveCount > 0 && <span className="live-badge">Live ({liveCount})</span>}
      </div>
      
      {activities.map(activity => (
        <div 
          key={activity.id} 
          className={`activity-item ${activity.is_live ? 'live' : ''}`}
        >
          <div className="activity-content">
            <h4>{activity.title}</h4>
            <p>{activity.description}</p>
            <span className="time-ago">{activity.time_ago}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

export const SenderIDStats: React.FC = () => {
  const { stats, loading, error } = useSenderStats();

  if (loading) return <div className="loading">Loading sender stats...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!stats) return <div>No data available</div>;

  return (
    <div className="sender-stats">
      <div className="stat-card">
        <h3>Sender IDs</h3>
        <div className="stat-number">{stats.active_stats.total_active}</div>
        <p>Approved sender names</p>
      </div>
      
      <div className="stat-card">
        <h3>Total Requests</h3>
        <div className="stat-number">{stats.stats.total_requests}</div>
        <p>All time requests</p>
      </div>

      <div className="stat-card">
        <h3>Approved</h3>
        <div className="stat-number">{stats.stats.approved_requests}</div>
        <p>Approved requests</p>
      </div>
    </div>
  );
};

export const PerformanceOverview: React.FC = () => {
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPerformance = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getPerformanceOverview();
        setPerformanceData(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch performance data');
      } finally {
        setLoading(false);
      }
    };

    fetchPerformance();
  }, []);

  if (loading) return <div className="loading">Loading performance data...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!performanceData) return <div>No data available</div>;

  return (
    <div className="performance-overview">
      <h3>Performance Overview</h3>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h4>Total Messages</h4>
          <div className="metric-value">{performanceData.metrics.total_messages}</div>
        </div>
        <div className="metric-card">
          <h4>Delivery Rate</h4>
          <div className="metric-value">{performanceData.metrics.delivery_rate}%</div>
        </div>
        <div className="metric-card">
          <h4>Response Rate</h4>
          <div className="metric-value">{performanceData.metrics.response_rate}%</div>
        </div>
        <div className="metric-card">
          <h4>Active Conversations</h4>
          <div className="metric-value">{performanceData.metrics.active_conversations}</div>
        </div>
      </div>

      {performanceData.coming_soon && (
        <div className="coming-soon">
          <p>Analytics charts coming soon</p>
        </div>
      )}
    </div>
  );
};

// Main Dashboard Component
export const Dashboard: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if user is already logged in (check localStorage, etc.)
    const token = localStorage.getItem('auth_token');
    if (token) {
      apiClient.setToken(token);
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = async (email: string, password: string) => {
    try {
      const response = await apiClient.login(email, password);
      apiClient.setToken(response.tokens.access);
      localStorage.setItem('auth_token', response.tokens.access);
      setUser(response.user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Mifumo WMS Dashboard</h1>
        <p>Welcome, {user?.first_name} {user?.last_name}</p>
      </header>

      <div className="dashboard-content">
        <div className="dashboard-grid">
          <div className="dashboard-section">
            <DashboardOverview />
          </div>
          
          <div className="dashboard-section">
            <SenderIDStats />
          </div>
          
          <div className="dashboard-section">
            <ActivityFeed />
          </div>
          
          <div className="dashboard-section">
            <PerformanceOverview />
          </div>
        </div>
      </div>
    </div>
  );
};

// Login Form Component
interface LoginFormProps {
  onLogin: (email: string, password: string) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onLogin(email, password);
  };

  return (
    <div className="login-form">
      <h2>Login to Mifumo WMS</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Dashboard;
