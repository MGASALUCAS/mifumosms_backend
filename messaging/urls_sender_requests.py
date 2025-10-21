"""
URLs for sender ID request system.
"""
from django.urls import path
from . import views_sender_requests

app_name = 'sender_id_requests'

urlpatterns = [
    # Sender ID Request URLs - Root level for frontend compatibility
    path('', views_sender_requests.SenderIDRequestListCreateView.as_view(), name='request-list-create'),
    path('submit/', views_sender_requests.submit_sender_request, name='request-submit'),
    path('<uuid:pk>/', views_sender_requests.SenderIDRequestDetailView.as_view(), name='request-detail'),
    path('<uuid:pk>/delete/', views_sender_requests.delete_sender_request, name='request-delete'),
    path('<uuid:pk>/review/', views_sender_requests.SenderIDRequestReviewView.as_view(), name='request-review'),
    
    # Sender ID Usage URLs
    path('usage/', views_sender_requests.SenderIDUsageListCreateView.as_view(), name='usage-list-create'),
    path('usage/<uuid:usage_id>/detach/', views_sender_requests.detach_sender_id, name='usage-detach'),
    
    # Utility URLs
    path('available/', views_sender_requests.available_sender_ids, name='available-sender-ids'),
    path('default/overview/', views_sender_requests.default_sender_overview, name='default-sender-overview'),
    path('request-default/', views_sender_requests.request_default_sender_id, name='request-default'),
    path('cancel-default/', views_sender_requests.cancel_default_sender_id, name='cancel-default'),
    path('status/', views_sender_requests.sender_id_request_status, name='request-status'),
    path('stats/', views_sender_requests.sender_requests_stats, name='request-stats'),
    path('refresh/', views_sender_requests.refresh_sender_requests, name='request-refresh'),
]