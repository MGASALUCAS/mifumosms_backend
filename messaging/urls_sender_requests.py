"""
URLs for sender ID request system.
"""
from django.urls import path
from . import views_sender_requests

app_name = 'sender_id_requests'

urlpatterns = [
    # Sender ID Request URLs
    path('requests/', views_sender_requests.SenderIDRequestListCreateView.as_view(), name='request-list-create'),
    path('requests/<uuid:pk>/', views_sender_requests.SenderIDRequestDetailView.as_view(), name='request-detail'),
    path('requests/<uuid:pk>/review/', views_sender_requests.SenderIDRequestReviewView.as_view(), name='request-review'),
    
    # Sender ID Usage URLs
    path('usage/', views_sender_requests.SenderIDUsageListCreateView.as_view(), name='usage-list-create'),
    path('usage/<uuid:usage_id>/detach/', views_sender_requests.detach_sender_id, name='usage-detach'),
    
    # Utility URLs
    path('available/', views_sender_requests.available_sender_ids, name='available-sender-ids'),
    path('request-default/', views_sender_requests.request_default_sender_id, name='request-default'),
    path('status/', views_sender_requests.sender_id_request_status, name='request-status'),
]