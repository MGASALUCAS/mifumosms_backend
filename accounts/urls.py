"""
URL patterns for user authentication and management.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

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

    # Email verification
    path('verify-email/', views.verify_email, name='verify-email'),

    # API key management
    path('api-key/generate/', views.generate_api_key, name='generate-api-key'),
    path('api-key/revoke/', views.revoke_api_key, name='revoke-api-key'),

    # Admin lookup endpoints
    path('lookup/users/', views.user_lookup, name='user-lookup'),
]
