"""
URL patterns for sender name request functionality.
"""
from django.urls import path
from . import views_sender_requests, views_admin_dashboard

urlpatterns = [
    # Sender Name Request Management
    path('', views_sender_requests.get_sender_name_requests, name='sender-request-list'),
    path('submit/', views_sender_requests.submit_sender_name_request, name='sender-request-submit'),
    path('stats/', views_sender_requests.get_sender_name_request_stats, name='sender-request-stats'),
    path('<uuid:request_id>/', views_sender_requests.get_sender_name_request, name='sender-request-detail'),
    path('<uuid:request_id>/update/', views_sender_requests.update_sender_name_request, name='sender-request-update'),
    path('<uuid:request_id>/delete/', views_sender_requests.delete_sender_name_request, name='sender-request-delete'),

    # Admin Dashboard
    path('admin/dashboard/', views_sender_requests.admin_sender_requests_dashboard, name='admin-sender-request-dashboard'),
]
