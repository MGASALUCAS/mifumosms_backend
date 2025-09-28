"""
URL patterns for tenant management.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Tenant management
    path('', views.TenantListCreateView.as_view(), name='tenant-list-create'),
    path('<uuid:pk>/', views.TenantDetailView.as_view(), name='tenant-detail'),
    path('switch/', views.switch_tenant, name='tenant-switch'),
    
    # Domain management
    path('<uuid:tenant_id>/domains/', views.DomainListCreateView.as_view(), name='domain-list-create'),
    path('<uuid:tenant_id>/domains/<uuid:pk>/', views.DomainDetailView.as_view(), name='domain-detail'),
    
    # Membership management
    path('<uuid:tenant_id>/members/', views.MembershipListCreateView.as_view(), name='membership-list-create'),
    path('<uuid:tenant_id>/members/<uuid:pk>/', views.MembershipDetailView.as_view(), name='membership-detail'),
    
    # Invitations
    path('invite/<str:token>/', views.accept_invitation, name='accept-invitation'),
]
