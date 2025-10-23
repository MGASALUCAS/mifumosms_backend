"""
URL patterns for user authentication and management.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import views_security

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
    
    # Security endpoints
    path('security/change-password/', views_security.change_password, name='change-password'),
    path('security/2fa/status/', views_security.two_factor_status, name='2fa-status'),
    path('security/2fa/enable/', views_security.enable_2fa, name='enable-2fa'),
    path('security/2fa/disable/', views_security.disable_2fa, name='disable-2fa'),
    path('security/2fa/verify/', views_security.verify_2fa, name='verify-2fa'),
    path('security/sessions/', views_security.UserSessionListView.as_view(), name='user-sessions'),
    path('security/sessions/<uuid:session_id>/terminate/', views_security.terminate_session, name='terminate-session'),
    path('security/sessions/terminate-all-others/', views_security.terminate_all_other_sessions, name='terminate-all-other-sessions'),
    path('security/events/', views_security.SecurityEventListView.as_view(), name='security-events'),
    path('security/summary/', views_security.security_summary, name='security-summary'),
]
