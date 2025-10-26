"""
URL patterns for user authentication and management.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import settings_api

urlpatterns = [
    # Authentication
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/detail/', views.UserProfileDetailView.as_view(), name='user-profile-detail'),
    
    # User settings (based on screenshot)
    path('settings/profile/', views.UserProfileSettingsView.as_view(), name='user-profile-settings'),
    path('settings/preferences/', views.UserPreferencesView.as_view(), name='user-preferences'),
    path('settings/notifications/', views.UserNotificationsView.as_view(), name='user-notifications'),
    path('settings/security/', views.UserSecurityView.as_view(), name='user-security'),

    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', views.password_reset_request, name='password-reset'),
    path('password/reset/confirm/', views.password_reset_confirm, name='password-reset-confirm'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),

    # SMS verification
    path('sms/send-code/', views.send_verification_code, name='send-verification-code'),
    path('sms/verify-code/', views.verify_phone_code, name='verify-phone-code'),
    path('sms/forgot-password/', views.forgot_password_sms, name='forgot-password-sms'),
    path('sms/reset-password/', views.reset_password_sms, name='reset-password-sms'),
    path('sms/confirm-account/', views.confirm_account_sms, name='confirm-account-sms'),
    
    # SMS verification links
    path('sms/send-verification-link/', views.send_verification_link_sms, name='send-verification-link-sms'),
    path('sms/verify-account-link/', views.verify_account_link, name='verify-account-link'),
    path('sms/resend-verification-link/', views.resend_verification_link, name='resend-verification-link'),

    # Email verification
    path('verify-email/', views.verify_email, name='verify-email'),

    # API key management
    path('api-key/generate/', views.generate_api_key, name='generate-api-key'),
    path('api-key/revoke/', views.revoke_api_key, name='revoke-api-key'),

    # Admin lookup endpoints
    path('lookup/users/', views.user_lookup, name='user-lookup'),

    # User Settings API (moved from api_integration)
    path('settings/', settings_api.get_api_settings, name='get_settings'),
    path('usage/', settings_api.get_api_usage, name='get_usage'),
    
    # API Key management
    path('keys/create/', settings_api.create_api_key, name='create_key'),
    path('keys/<str:key_id>/revoke/', settings_api.revoke_api_key, name='revoke_key'),
    path('keys/<str:key_id>/regenerate/', settings_api.regenerate_api_key, name='regenerate_key'),
    
    # Webhook management
    path('webhooks/create/', settings_api.create_webhook, name='create_webhook'),
    path('webhooks/<str:webhook_id>/toggle/', settings_api.toggle_webhook, name='toggle_webhook'),
    path('webhooks/<str:webhook_id>/delete/', settings_api.delete_webhook, name='delete_webhook'),
]
