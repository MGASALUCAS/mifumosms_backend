"""
Enhanced team management views for tenant memberships.
"""
from rest_framework import generics, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.db import transaction

from .models import Tenant, Membership
from .serializers import (
    MembershipSerializer, MembershipCreateSerializer
)
from .team_serializers import (
    MembershipUpdateSerializer, TeamStatsSerializer
)
from core.permissions import IsTenantMember, IsTenantOwner, IsTenantAdmin

User = get_user_model()


class BaseTenantViewMixin:
    """Ensure request.tenant is set from the URL param before permissions run."""

    def dispatch(self, request, *args, **kwargs):
        """Set tenant before any processing."""
        tenant_id = kwargs.get('tenant_id')
        if tenant_id:
            request.tenant = get_object_or_404(Tenant, id=tenant_id)
            # Also set session for consistency
            request.session['current_tenant_id'] = str(tenant_id)
        return super().dispatch(request, *args, **kwargs)


class TeamListView(BaseTenantViewMixin, generics.ListAPIView):
    """List all team members for the current tenant."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = MembershipSerializer
    
    def list(self, request, *args, **kwargs):
        """Override list to add debug logging."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Team list request for tenant: {self.request.tenant}")
        logger.info(f"Tenant ID: {self.request.tenant.id}")
        logger.info(f"User: {self.request.user.email}")
        
        # Get queryset
        queryset = self.filter_queryset(self.get_queryset())
        logger.info(f"Found {queryset.count()} members")
        
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Serialized data: {serializer.data}")
        
        return Response(serializer.data)
    
    def get_queryset(self):
        """Return memberships for the current tenant."""
        return Membership.objects.filter(
            tenant=self.request.tenant
        ).select_related('user', 'invited_by').order_by('-joined_at', '-invited_at')


class TeamInviteView(BaseTenantViewMixin, generics.CreateAPIView):
    """Invite a new team member."""
    
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = MembershipCreateSerializer
    
    def get_serializer_context(self):
        """Add tenant and request to serializer context."""
        context = super().get_serializer_context()
        context['tenant'] = self.request.tenant
        return context
    
    def create(self, request, *args, **kwargs):
        """Override create to add better error logging."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Creating invitation with data: {request.data}")
        logger.info(f"Tenant: {self.request.tenant}")
        logger.info(f"User: {self.request.user}")
        
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            # Return the validation error with proper format
            logger.error(f"Validation error: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Error creating invitation: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def perform_create(self, serializer):
        """Create membership and send invitation email."""
        membership = serializer.save()
        
        # Generate invitation token
        token = get_random_string(32)
        membership.invitation_token = token
        membership.save()
        
        # Send invitation email
        self.send_invitation_email(membership, token)
    
    def send_invitation_email(self, membership, token):
        """Send invitation email to the new member."""
        import logging
        logger = logging.getLogger(__name__)
        
        tenant = self.request.tenant
        inviter = self.request.user
        
        # Create invitation URL
        invitation_url = f"{settings.BASE_URL}/invite/{token}"
        
        subject = f"You're invited to join {tenant.name} on Mifumo"
        message = f"""
        Hi there,
        
        {inviter.get_full_name() or inviter.email} has invited you to join {tenant.name} on Mifumo WMS.
        
        Your role will be: {membership.get_role_display()}
        
        Click the link below to accept the invitation:
        {invitation_url}
        
        If you don't have an account yet, you'll be able to create one after clicking the link.
        
        Best regards,
        The Mifumo Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [membership.user.email],
                fail_silently=True,
            )
            logger.info(f"Invitation email sent to {membership.user.email}")
        except Exception as e:
            logger.error(f"Failed to send invitation email to {membership.user.email}: {str(e)}")
            # Don't raise - membership is still created, user just won't receive email


class TeamMemberDetailView(BaseTenantViewMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or remove a team member."""
    
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MembershipUpdateSerializer
        return MembershipSerializer
    
    def get_queryset(self):
        """Return memberships for the current tenant."""
        return Membership.objects.filter(tenant=self.request.tenant)
    
    def perform_update(self, serializer):
        """Update membership with validation."""
        membership = self.get_object()
        
        # Prevent non-owners from changing owner roles
        if membership.role == 'owner' and self.request.user != membership.user:
            if not self.request.user.memberships.filter(
                tenant=self.request.tenant, 
                role='owner'
            ).exists():
                return Response(
                    {'error': 'Only owners can modify other owners'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Remove team member with validation."""
        # Prevent removing the last ACTIVE owner (not pending)
        if instance.role == 'owner' and instance.status == 'active':
            active_owner_count = Membership.objects.filter(
                tenant=self.request.tenant,
                role='owner',
                status='active'
            ).count()
            
            if active_owner_count <= 1:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'error': 'Cannot remove the last active owner'})
        
        # Prevent non-owners from removing active owners
        if instance.role == 'owner' and instance.status == 'active' and self.request.user != instance.user:
            if not self.request.user.memberships.filter(
                tenant=self.request.tenant, 
                role='owner',
                status='active'
            ).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Only active owners can remove other active owners')
        
        # Safe to delete (pending owners can always be deleted by admins)
        instance.delete()


class TeamStatsView(BaseTenantViewMixin, generics.RetrieveAPIView):
    """Get team statistics for the current tenant."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = TeamStatsSerializer
    
    def get_object(self):
        """Return team statistics."""
        tenant = self.request.tenant
        
        stats = {
            'total_members': Membership.objects.filter(tenant=tenant).count(),
            'active_members': Membership.objects.filter(
                tenant=tenant, status='active'
            ).count(),
            'pending_members': Membership.objects.filter(
                tenant=tenant, status='pending'
            ).count(),
            'suspended_members': Membership.objects.filter(
                tenant=tenant, status='suspended'
            ).count(),
            'owners': Membership.objects.filter(
                tenant=tenant, role='owner', status='active'
            ).count(),
            'admins': Membership.objects.filter(
                tenant=tenant, role='admin', status='active'
            ).count(),
            'agents': Membership.objects.filter(
                tenant=tenant, role='agent', status='active'
            ).count(),
        }
        
        return stats


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invitation(request, token):
    """Accept a tenant invitation."""
    try:
        membership = Membership.objects.get(
            invitation_token=token,
            status='pending'
        )
        
        # Check if user is already a member
        if membership.user == request.user:
            membership.status = 'active'
            membership.joined_at = timezone.now()
            membership.invitation_token = None
            membership.save()
            
            return Response({
                'message': f'Successfully joined {membership.tenant.name}',
                'tenant': {
                    'id': str(membership.tenant.id),
                    'name': membership.tenant.name,
                    'subdomain': membership.tenant.subdomain
                },
                'role': membership.role
            })
        else:
            return Response(
                {'error': 'This invitation is not for your account'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired invitation'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_invitation(request, token):
    """Reject a tenant invitation."""
    try:
        membership = Membership.objects.get(
            invitation_token=token,
            status='pending'
        )
        
        if membership.user == request.user:
            membership.delete()
            return Response({
                'message': 'Invitation rejected successfully'
            })
        else:
            return Response(
                {'error': 'This invitation is not for your account'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired invitation'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_invitation(request, tenant_id, pk):
    """Resend invitation email to a pending member."""
    # Set tenant from URL before checking permissions
    request.tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Now check permissions manually
    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        membership_check = Membership.objects.get(
            tenant=request.tenant,
            user=request.user,
            status='active'
        )
        if membership_check.role not in ['owner', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    except Membership.DoesNotExist:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        membership = Membership.objects.get(
            id=pk,
            tenant=request.tenant,
            status='pending'
        )
        
        # Generate new invitation token
        token = get_random_string(32)
        membership.invitation_token = token
        membership.save()
        
        # Send invitation email
        tenant = request.tenant
        inviter = request.user
        
        invitation_url = f"{settings.BASE_URL}/invite/{token}"
        
        subject = f"Reminder: You're invited to join {tenant.name} on Mifumo"
        message = f"""
        Hi there,
        
        This is a reminder that {inviter.get_full_name() or inviter.email} has invited you to join {tenant.name} on Mifumo WMS.
        
        Your role will be: {membership.get_role_display()}
        
        Click the link below to accept the invitation:
        {invitation_url}
        
        If you don't have an account yet, you'll be able to create one after clicking the link.
        
        Best regards,
        The Mifumo Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [membership.user.email],
                fail_silently=True,
            )
            return Response({
                'message': 'Invitation resent successfully'
            })
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to resend invitation email: {str(e)}")
            return Response({
                'message': 'Member invited successfully, but email could not be sent. Please share the invitation link manually.'
            })
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Membership not found or not pending'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def suspend_member(request, tenant_id, pk):
    """Suspend a team member."""
    request.tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Check permissions manually
    try:
        membership_check = Membership.objects.get(
            tenant=request.tenant,
            user=request.user,
            status='active'
        )
        if membership_check.role not in ['owner', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    except Membership.DoesNotExist:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        membership = Membership.objects.get(
            id=pk,
            tenant=request.tenant
        )
        
        # Prevent suspending owners
        if membership.role == 'owner':
            return Response(
                {'error': 'Cannot suspend owners'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        membership.status = 'suspended'
        membership.save()
        
        return Response({
            'message': f'{membership.user.get_full_name()} has been suspended'
        })
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Membership not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_member(request, tenant_id, pk):
    """Activate a suspended team member."""
    request.tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Check permissions manually
    try:
        membership_check = Membership.objects.get(
            tenant=request.tenant,
            user=request.user,
            status='active'
        )
        if membership_check.role not in ['owner', 'admin']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    except Membership.DoesNotExist:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    try:
        membership = Membership.objects.get(
            id=pk,
            tenant=request.tenant,
            status='suspended'
        )
        
        membership.status = 'active'
        membership.save()
        
        return Response({
            'message': f'{membership.user.get_full_name()} has been activated'
        })
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Suspended membership not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer_ownership(request, tenant_id, pk):
    """Transfer ownership to another member."""
    request.tenant = get_object_or_404(Tenant, id=tenant_id)
    
    # Check if user is owner
    try:
        membership_check = Membership.objects.get(
            tenant=request.tenant,
            user=request.user,
            role='owner',
            status='active'
        )
    except Membership.DoesNotExist:
        return Response({'error': 'Only owners can transfer ownership'}, status=status.HTTP_403_FORBIDDEN)
    try:
        new_owner_membership = Membership.objects.get(
            id=pk,
            tenant=request.tenant,
            status='active'
        )
        
        # Get current owner membership
        current_owner_membership = Membership.objects.get(
            user=request.user,
            tenant=request.tenant,
            role='owner'
        )
        
        with transaction.atomic():
            # Transfer ownership
            current_owner_membership.role = 'admin'
            current_owner_membership.save()
            
            new_owner_membership.role = 'owner'
            new_owner_membership.save()
        
        return Response({
            'message': f'Ownership transferred to {new_owner_membership.user.get_full_name()}'
        })
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Membership not found'},
            status=status.HTTP_404_NOT_FOUND
        )
