"""
URL patterns for messaging functionality.
"""
from django.urls import path, include
from . import views

urlpatterns = [
    # Contacts
    path('contacts/', views.ContactListCreateView.as_view(), name='contact-list-create'),
    path('contacts/<uuid:pk>/', views.ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/bulk-import/', views.ContactBulkImportView.as_view(), name='contact-bulk-import'),
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
    
    # Campaigns
    path('campaigns/', views.CampaignListCreateView.as_view(), name='campaign-list-create'),
    path('campaigns/<uuid:pk>/', views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<uuid:campaign_id>/start/', views.campaign_start, name='campaign-start'),
    path('campaigns/<uuid:campaign_id>/pause/', views.campaign_pause, name='campaign-pause'),
    path('campaigns/<uuid:campaign_id>/cancel/', views.campaign_cancel, name='campaign-cancel'),
    
    # Flows
    path('flows/', views.FlowListCreateView.as_view(), name='flow-list-create'),
    path('flows/<uuid:pk>/', views.FlowDetailView.as_view(), name='flow-detail'),
    path('flows/<uuid:flow_id>/activate/', views.flow_activate, name='flow-activate'),
    path('flows/<uuid:flow_id>/deactivate/', views.flow_deactivate, name='flow-deactivate'),
    
    # AI Features
    path('ai/suggest-reply/<uuid:conversation_id>/', views.ai_suggest_reply, name='ai-suggest-reply'),
    path('ai/summarize/<uuid:conversation_id>/', views.ai_summarize_conversation, name='ai-summarize'),
    
    # Analytics
    path('analytics/overview/', views.analytics_overview, name='analytics-overview'),
]

# Include SMS URLs
urlpatterns += [
    path('sms/', include('messaging.urls_sms')),
]
