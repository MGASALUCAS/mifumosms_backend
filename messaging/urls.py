"""
URL patterns for messaging functionality.
Optimized for frontend integration.
"""
from django.urls import path, include
from . import views, views_dashboard, views_campaign

urlpatterns = [
    # Core messaging endpoints (used by frontend)
    # Contacts
    path('contacts/', views.ContactListCreateView.as_view(), name='contact-list-create'),
    path('contacts/<uuid:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/bulk-import/', views.ContactBulkImportView.as_view(), name='contact-bulk-import'),
    path('contacts/import/', views.ContactImportView.as_view(), name='contact-import'),
    path('contacts/<uuid:contact_id>/opt-in/', views.contact_opt_in, name='contact-opt-in'),
    path('contacts/<uuid:contact_id>/opt-out/', views.contact_opt_out, name='contact-opt-out'),

    # Segments
    path('segments/', views.SegmentListCreateView.as_view(), name='segment-list-create'),
    path('segments/<uuid:pk>/', views.SegmentDetailView.as_view(), name='segment-detail'),
    path('segments/<uuid:segment_id>/update-count/', views.segment_update_count, name='segment-update-count'),

    # Templates
    path('templates/', views.TemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<uuid:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),

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

    # Dashboard
    path('dashboard/overview/', views_dashboard.dashboard_overview, name='dashboard-overview'),
    path('dashboard/metrics/', views_dashboard.dashboard_metrics, name='dashboard-metrics'),
]

# Include SMS URLs
urlpatterns += [
    path('sms/', include('messaging.urls_sms')),
]
