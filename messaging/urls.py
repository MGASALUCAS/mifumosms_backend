"""
URL patterns for messaging functionality.
Optimized for frontend integration.
"""
from django.urls import path, include
from . import views, views_dashboard, views_campaign, views_activity

urlpatterns = [
    # Core messaging endpoints (used by frontend)
    # Contacts - more specific paths MUST come before less specific ones
    path('contacts/bulk-import/', views.ContactBulkImportView.as_view(), name='contact-bulk-import'),
    path('contacts/bulk-edit/', views.ContactBulkEditView.as_view(), name='contact-bulk-edit'),
    path('contacts/bulk-delete/', views.ContactBulkDeleteView.as_view(), name='contact-bulk-delete'),
    path('contacts/bulk-add-tags/', views.ContactBulkAddTagsView.as_view(), name='contact-bulk-add-tags'),
    path('contacts/import/', views.ContactImportView.as_view(), name='contact-import'),
    path('contacts/<uuid:contact_id>/opt-in/', views.contact_opt_in, name='contact-opt-in'),
    path('contacts/<uuid:contact_id>/opt-out/', views.contact_opt_out, name='contact-opt-out'),
    path('contacts/', views.ContactListCreateView.as_view(), name='contact-list-create'),
    path('contacts/<uuid:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),

    # Segments
    path('segments/', views.SegmentListCreateView.as_view(), name='segment-list-create'),
    path('segments/<uuid:pk>/', views.SegmentDetailView.as_view(), name='segment-detail'),
    path('segments/<uuid:segment_id>/update-count/', views.segment_update_count, name='segment-update-count'),

    # Templates
    path('templates/', views.TemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<uuid:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),
    path('templates/<uuid:template_id>/toggle-favorite/', views.template_toggle_favorite, name='template-toggle-favorite'),
    path('templates/<uuid:template_id>/increment-usage/', views.template_increment_usage, name='template-increment-usage'),
    path('templates/<uuid:template_id>/approve/', views.template_approve, name='template-approve'),
    path('templates/<uuid:template_id>/reject/', views.template_reject, name='template-reject'),
    path('templates/<uuid:template_id>/variables/', views.template_variables, name='template-variables'),
    path('templates/<uuid:template_id>/copy/', views.template_copy, name='template-copy'),
    path('templates/statistics/', views.template_statistics, name='template-statistics'),

    # Conversations
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<uuid:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),

    # Messages
    path('messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<uuid:pk>/', views.MessageDetailView.as_view(), name='message-detail'),

    # Smart Campaign Management
    path('campaigns/', views_campaign.CampaignListView.as_view(), name='campaign-list-create'),
    path('campaigns/summary/', views_campaign.user_campaigns_summary, name='campaign-summary'),
    path('campaigns/<uuid:pk>/', views_campaign.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<uuid:campaign_id>/start/', views_campaign.start_campaign, name='campaign-start'),
    path('campaigns/<uuid:campaign_id>/pause/', views_campaign.pause_campaign, name='campaign-pause'),
    path('campaigns/<uuid:campaign_id>/cancel/', views_campaign.cancel_campaign, name='campaign-cancel'),
    path('campaigns/<uuid:campaign_id>/analytics/', views_campaign.campaign_analytics, name='campaign-analytics'),
    path('campaigns/<uuid:campaign_id>/duplicate/', views_campaign.duplicate_campaign, name='campaign-duplicate'),
    path('campaigns/<uuid:campaign_id>/permissions/', views_campaign.campaign_permissions, name='campaign-permissions'),

    # Analytics
    path('analytics/overview/', views.analytics_overview, name='analytics-overview'),

    # Purchase History - moved to billing/history/ for better organization
    # Use /api/billing/history/purchases/ instead

    # Dashboard
    path('dashboard/overview/', views_dashboard.dashboard_overview, name='dashboard-overview'),
    path('dashboard/metrics/', views_dashboard.dashboard_metrics, name='dashboard-metrics'),
    path('dashboard/comprehensive/', views_dashboard.dashboard_comprehensive, name='dashboard-comprehensive'),

    # Activity & Performance
    path('activity/recent/', views_activity.recent_activity, name='recent-activity'),
    path('performance/overview/', views_activity.performance_overview, name='performance-overview'),
    path('activity/statistics/', views_activity.activity_statistics, name='activity-statistics'),

    # Sender IDs (for frontend compatibility)
    path('sender-ids/', views.sender_ids_list, name='sender-ids-list'),
    path('sender-ids/request/', views.request_sender_id, name='sender-ids-request'),
    path('sender-ids/<uuid:pk>/', views.sender_id_detail, name='sender-id-detail'),
    path('sender-ids/<uuid:pk>/status/', views.sender_id_status, name='sender-id-status'),
]

# Include SMS URLs
urlpatterns += [
    path('sms/', include('messaging.urls_sms')),
]

# Include Sender Name Request URLs
urlpatterns += [
    path('sender-requests/', include('messaging.urls_sender_requests')),
]

# Include Sender ID Request URLs (for frontend compatibility)
urlpatterns += [
    path('sender-id-requests/', include('messaging.urls_sender_id_requests')),
]
