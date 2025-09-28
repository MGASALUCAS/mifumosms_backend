"""
Custom permissions for multi-tenant access control.
"""
from rest_framework import permissions
from tenants.models import Membership


class IsTenantMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the current tenant.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
        
        try:
            membership = Membership.objects.get(
                tenant=request.tenant,
                user=request.user,
                status='active'
            )
            return True
        except Membership.DoesNotExist:
            return False


class IsTenantOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the current tenant.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
        
        try:
            membership = Membership.objects.get(
                tenant=request.tenant,
                user=request.user,
                status='active'
            )
            return membership.role == 'owner'
        except Membership.DoesNotExist:
            return False


class IsTenantAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin or owner of the current tenant.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request, 'tenant') or not request.tenant:
            return False
        
        try:
            membership = Membership.objects.get(
                tenant=request.tenant,
                user=request.user,
                status='active'
            )
            return membership.role in ['owner', 'admin']
        except Membership.DoesNotExist:
            return False
