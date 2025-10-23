// TypeScript interfaces for Mifumo WMS API responses

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined?: string;
  last_login?: string;
}

export interface LoginResponse {
  message: string;
  tokens: {
    access: string;
    refresh: string;
  };
  user: User;
}

export interface DashboardMetrics {
  total_messages: number;
  total_sms_messages: number;
  active_contacts: number;
  campaign_success_rate: number;
  sms_delivery_rate: number;
  current_credits: number;
  total_purchased: number;
  sender_ids_this_month: number;
}

export interface RecentCampaign {
  id: string;
  name: string;
  type: string;
  status: string;
  sent: number;
  delivered: number;
  opened: number;
  progress: number;
  created_at: string;
  created_at_human: string;
}

export interface MessageStats {
  today: number;
  this_week: number;
  this_month: number;
  growth_rate: number;
}

export interface SMSStats {
  today: number;
  this_month: number;
  delivery_rate: number;
}

export interface ContactStats {
  total: number;
  active: number;
  new_this_month: number;
  growth_rate: number;
}

export interface BillingStats {
  current_credits: number;
  total_purchased: number;
  credits_used: number;
}

export interface DashboardOverviewResponse {
  success: boolean;
  data: {
    metrics: DashboardMetrics;
    recent_campaigns: RecentCampaign[];
    message_stats: MessageStats;
    sms_stats: SMSStats;
    contact_stats: ContactStats;
    billing_stats: BillingStats;
    last_updated: string;
  };
}

export interface DashboardMetricsData {
  message_volume: {
    today: number;
    this_week: number;
    this_month: number;
    last_month: number;
    growth_rate: number;
  };
  contact_growth: {
    total: number;
    new_this_month: number;
    growth_rate: number;
  };
  campaign_performance: {
    total_campaigns: number;
    completed_campaigns: number;
    success_rate: number;
  };
  sms_usage: {
    total_sent: number;
    delivered: number;
    failed: number;
    delivery_rate: number;
  };
}

export interface DashboardMetricsResponse {
  success: boolean;
  data: DashboardMetricsData;
}

export interface ActivityMetadata {
  conversation_id?: string;
  contact_name: string;
  conversation_subject?: string;
  message_id?: string;
  campaign_id?: string;
  campaign_name?: string;
  delivery_rate?: number;
  sent_count?: number;
  delivered_count?: number;
  contact_id?: string;
  phone?: string;
}

export interface Activity {
  id: string;
  type: 'message_sent' | 'conversation_reply' | 'campaign_completed' | 'contact_added' | 'campaign_started';
  title: string;
  description: string;
  timestamp: string;
  time_ago: string;
  is_live: boolean;
  metadata: ActivityMetadata;
}

export interface RecentActivityResponse {
  success: boolean;
  data: {
    activities: Activity[];
    has_more: boolean;
    total_count: number;
    live_count: number;
  };
}

export interface PerformanceMetrics {
  total_messages: number;
  delivery_rate: number;
  response_rate: number;
  active_conversations: number;
  campaign_success_rate: number;
}

export interface ChartData {
  labels: string[];
  data: number[];
}

export interface PerformanceCharts {
  message_volume: ChartData;
  delivery_rates: ChartData;
}

export interface PerformanceOverviewResponse {
  success: boolean;
  data: {
    metrics: PerformanceMetrics;
    charts: PerformanceCharts;
    coming_soon: boolean;
  };
}

export interface SenderIDStats {
  total_requests: number;
  pending_requests: number;
  approved_requests: number;
  rejected_requests: number;
  requires_changes_requests: number;
}

export interface ActiveSenderID {
  id: string;
  sender_id: string;
  status: string;
  created_at: string;
}

export interface ActiveStats {
  total_active: number;
  active_sender_ids: ActiveSenderID[];
}

export interface SenderIDRequest {
  id: string;
  tenant: string;
  user: number;
  request_type: string;
  requested_sender_id: string;
  sample_content: string;
  status: string;
  reviewed_by: number | null;
  reviewed_at: string | null;
  rejection_reason: string;
  sms_package: string | null;
  created_at: string;
  updated_at: string;
  user_email: string;
  user_id: number;
  tenant_name: string;
  sender_name: string;
  use_case: string;
}

export interface SenderStatsResponse {
  success: boolean;
  data: {
    stats: SenderIDStats;
    request_stats: SenderIDStats;
    active_stats: ActiveStats;
    recent_requests: SenderIDRequest[];
  };
}

export interface SMSBalance {
  id: string;
  tenant: string;
  credits: number;
  total_purchased: number;
  total_used: number;
  last_updated: string;
  created_at: string;
}

export interface Contact {
  id: string;
  name: string;
  phone_e164: string;
  email: string;
  attributes: Record<string, any>;
  tags: string[];
  opt_in_at: string | null;
  opt_out_at: string | null;
  opt_out_reason: string;
  is_active: boolean;
  last_contacted_at: string | null;
  is_opted_in: boolean;
  created_by: string;
  created_by_id: number;
  created_at: string;
  updated_at: string;
}

export interface ContactsListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Contact[];
}

export interface APIError {
  success?: boolean;
  message?: string;
  detail?: string;
  error?: string;
}

// API Client Types
export interface APIClientConfig {
  baseURL: string;
  token?: string;
}

export interface APIResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

// Hook return types
export interface UseDashboardReturn {
  dashboardData: DashboardOverviewResponse['data'] | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface UseActivityReturn {
  activities: Activity[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  totalCount: number;
  liveCount: number;
  refetch: () => Promise<void>;
}

export interface UseSenderStatsReturn {
  stats: SenderStatsResponse['data'] | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface UseContactsReturn {
  contacts: Contact[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  hasNext: boolean;
  hasPrevious: boolean;
  refetch: () => Promise<void>;
  loadMore: () => Promise<void>;
}
