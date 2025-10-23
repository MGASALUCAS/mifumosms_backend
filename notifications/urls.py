"""
URL patterns for notification endpoints.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Notification CRUD
    path('', views.NotificationListCreateView.as_view(), name='notification-list-create'),
    path('<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    
    # Notification actions
    path('stats/', views.notification_stats, name='notification-stats'),
    path('<uuid:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_read, name='mark-all-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
    path('recent/', views.recent_notifications, name='recent-notifications'),
    path('real/', views.get_real_notifications, name='get-real-notifications'),
    
    # Notification settings
    path('settings/', views.NotificationSettingsView.as_view(), name='notification-settings'),
    
    # System notifications (admin only)
    path('system/create/', views.create_system_notification, name='create-system-notification'),
    path('system/health-check/', views.system_health_check, name='system-health-check'),
    path('system/report-problem/', views.report_problem, name='report-problem'),
    path('system/cleanup/', views.cleanup_notifications, name='cleanup-notifications'),
    path('templates/', views.notification_templates, name='notification-templates'),
    
    # SMS Credit notifications
    path('sms-credit/test/', views.test_sms_credit_notification, name='test-sms-credit-notification'),
]
