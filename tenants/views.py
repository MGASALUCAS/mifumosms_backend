"""
Views for tenant management.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

from .models import Tenant, Domain, Membership
from .serializers import (
    TenantSerializer, TenantCreateSerializer, DomainSerializer,
    MembershipSerializer, MembershipCreateSerializer, TenantSwitchSerializer
)
from core.permissions import IsTenantMember, IsTenantOwner, IsTenantAdmin

User = get_user_model()


class TenantListCreateView(generics.ListCreateAPIView):
    """List user's tenants or create a new tenant."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TenantCreateSerializer
        return TenantSerializer
    
    def get_queryset(self):
        """Return tenants where user is a member."""
        if not self.request.user.is_authenticated:
            return Tenant.objects.none()
        return Tenant.objects.filter(
            memberships__user=self.request.user,
            memberships__status='active'
        ).distinct()
    
    def perform_create(self, serializer):
        """Create tenant and make user the owner."""
        tenant = serializer.save()
        
        # Create membership for the creator as owner
        Membership.objects.create(
            tenant=tenant,
            user=self.request.user,
            role='owner',
            status='active',
            joined_at=timezone.now()
        )
        
        # Create default domain
        Domain.objects.create(
            tenant=tenant,
            domain=f"{tenant.subdomain}.mifumo.local",
            is_primary=True,
            verified=True
        )


class TenantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a tenant."""
    
    permission_classes = [IsAuthenticated, IsTenantMember]
    serializer_class = TenantSerializer
    
    def get_queryset(self):
        """Return tenants where user is a member."""
        if not self.request.user.is_authenticated:
            return Tenant.objects.none()
        return Tenant.objects.filter(
            memberships__user=self.request.user,
            memberships__status='active'
        ).distinct()


class DomainListCreateView(generics.ListCreateAPIView):
    """List tenant's domains or add a new domain."""
    
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = DomainSerializer
    
    def get_queryset(self):
        """Return domains for the current tenant."""
        return Domain.objects.filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        """Create domain for the current tenant."""
        serializer.save(tenant=self.request.tenant)


class DomainDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a domain."""
    
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = DomainSerializer
    
    def get_queryset(self):
        """Return domains for the current tenant."""
        return Domain.objects.filter(tenant=self.request.tenant)


class MembershipListCreateView(generics.ListCreateAPIView):
    """List tenant's memberships or invite a new member."""
    
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MembershipCreateSerializer
        return MembershipSerializer
    
    def get_queryset(self):
        """Return memberships for the current tenant."""
        return Membership.objects.filter(tenant=self.request.tenant).select_related('user', 'invited_by')
    
    def get_serializer_context(self):
        """Add tenant and request to serializer context."""
        context = super().get_serializer_context()
        context['tenant'] = self.request.tenant
        return context
    
    def perform_create(self, serializer):
        """Create membership and send invitation email."""
        membership = serializer.save()
        
        # Send invitation email
        self.send_invitation_email(membership)
    
    def send_invitation_email(self, membership):
        """Send invitation email to the new member."""
        tenant = self.request.tenant
        inviter = self.request.user
        
        # Generate invitation token
        token = get_random_string(32)
        membership.invitation_token = token
        membership.save()
        
        # Create invitation URL
        invitation_url = f"{settings.BASE_URL}/invite/{token}"
        
        subject = f"You're invited to join {tenant.name} on Mifumo"
        message = f"""
        Hi there,
        
        {inviter.get_full_name() or inviter.email} has invited you to join {tenant.name} on Mifumo WMS.
        
        Click the link below to accept the invitation:
        {invitation_url}
        
        If you don't have an account yet, you'll be able to create one after clicking the link.
        
        Best regards,
        The Mifumo Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [membership.user.email],
            fail_silently=False,
        )


class MembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a membership."""
    
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    serializer_class = MembershipSerializer
    
    def get_queryset(self):
        """Return memberships for the current tenant."""
        return Membership.objects.filter(tenant=self.request.tenant)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_tenant(request):
    """Switch the current tenant context."""
    serializer = TenantSwitchSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        tenant_id = serializer.validated_data['tenant_id']
        tenant = get_object_or_404(Tenant, id=tenant_id)
        
        # Update user's current tenant preference (could be stored in session or user profile)
        request.session['current_tenant_id'] = str(tenant_id)
        
        return Response({
            'message': f'Switched to {tenant.name}',
            'tenant': TenantSerializer(tenant).data
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invitation(request, token):
    """Accept a tenant invitation."""
    try:
        membership = Membership.objects.get(
            invitation_token=token,
            status='pending'
        )
        
        membership.status = 'active'
        membership.joined_at = timezone.now()
        membership.invitation_token = None
        membership.save()
        
        return Response({
            'message': f'Successfully joined {membership.tenant.name}',
            'tenant': TenantSerializer(membership.tenant).data
        })
    
    except Membership.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired invitation'},
            status=status.HTTP_400_BAD_REQUEST
        )
