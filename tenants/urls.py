"""
URL patterns for tenant management.
"""
from django.urls import path
from . import views, team_views

urlpatterns = [
    # Tenant management
    path('', views.TenantListCreateView.as_view(), name='tenant-list-create'),
    path('<uuid:pk>/', views.TenantDetailView.as_view(), name='tenant-detail'),
    path('switch/', views.switch_tenant, name='tenant-switch'),
    
    # Domain management
    path('<uuid:tenant_id>/domains/', views.DomainListCreateView.as_view(), name='domain-list-create'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/', views.DomainDetailView.as_view(), name='domain-detail'),
    
    # Legacy membership management (kept for backward compatibility)
    path('<uuid:tenant_id>/members/', views.MembershipListCreateView.as_view(), name='membership-list-create'),
    path('<uuid:tenant_id>/members/<uuid:pk>/', views.MembershipDetailView.as_view(), name='membership-detail'),
    
    # Enhanced team management
    path('<uuid:tenant_id>/team/', team_views.TeamListView.as_view(), name='team-list'),
    path('<uuid:tenant_id>/team/invite/', team_views.TeamInviteView.as_view(), name='team-invite'),
    path('<uuid:tenant_id>/team/stats/', team_views.TeamStatsView.as_view(), name='team-stats'),
    path('<uuid:tenant_id>/team/<uuid:pk>/', team_views.TeamMemberDetailView.as_view(), name='team-member-detail'),
    path('<uuid:tenant_id>/team/<uuid:pk>/suspend/', team_views.suspend_member, name='team-member-suspend'),
    path('<uuid:tenant_id>/team/<uuid:pk>/activate/', team_views.activate_member, name='team-member-activate'),
    path('<uuid:tenant_id>/team/<uuid:pk>/resend-invitation/', team_views.resend_invitation, name='team-resend-invitation'),
    path('<uuid:tenant_id>/team/<uuid:pk>/transfer-ownership/', team_views.transfer_ownership, name='team-transfer-ownership'),
    
    # Invitations
    path('invite/<str:token>/accept/', team_views.accept_invitation, name='accept-invitation'),
    path('invite/<str:token>/reject/', team_views.reject_invitation, name='reject-invitation'),
]
