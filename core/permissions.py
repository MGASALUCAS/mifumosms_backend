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


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow users to view all objects but only edit their own.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the owner
        return obj.created_by == request.user


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners to access their objects.
    """

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class CanEditCampaign(permissions.BasePermission):
    """
    Permission to check if user can edit a campaign.
    Users can only edit campaigns they created and only if they're in draft status.
    """

    def has_object_permission(self, request, view, obj):
        # Only the owner can edit
        if obj.created_by != request.user:
            return False

        # Only allow editing if campaign is in draft status
        if obj.status != 'draft':
            return False

        return True


class CanStartCampaign(permissions.BasePermission):
    """
    Permission to check if user can start a campaign.
    """

    def has_object_permission(self, request, view, obj):
        # Only the owner can start
        if obj.created_by != request.user:
            return False

        # Check if campaign can be started
        return obj.can_start


class CanPauseCampaign(permissions.BasePermission):
    """
    Permission to check if user can pause a campaign.
    """

    def has_object_permission(self, request, view, obj):
        # Only the owner can pause
        if obj.created_by != request.user:
            return False

        # Check if campaign can be paused
        return obj.can_pause


class CanCancelCampaign(permissions.BasePermission):
    """
    Permission to check if user can cancel a campaign.
    """

    def has_object_permission(self, request, view, obj):
        # Only the owner can cancel
        if obj.created_by != request.user:
            return False

        # Check if campaign can be cancelled
        return obj.can_cancel
