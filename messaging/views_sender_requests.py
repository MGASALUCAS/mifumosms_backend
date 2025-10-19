"""
Views for sender ID request system.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models_sender_requests import SenderIDRequest, SenderIDUsage
from .serializers_sender_requests import (
    SenderIDRequestSerializer, SenderIDRequestCreateSerializer,
    SenderIDRequestReviewSerializer, SenderIDUsageSerializer,
    SenderIDUsageCreateSerializer
)
from billing.models import SMSPackage


class SenderIDRequestListCreateView(generics.ListCreateAPIView):
    """List sender ID requests or create a new request."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SenderIDRequestCreateSerializer
        return SenderIDRequestSerializer
    
    def get_queryset(self):
        """Return sender ID requests for the current tenant."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return SenderIDRequest.objects.none()
        
        return SenderIDRequest.objects.filter(tenant=tenant).order_by('-created_at')
    
    def get_serializer_context(self):
        """Add tenant to serializer context."""
        context = super().get_serializer_context()
        context['tenant'] = getattr(self.request, 'tenant', None)
        return context
    
    def perform_create(self, serializer):
        """Create a new sender ID request."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            raise ValueError("No tenant found for this user")
        
        serializer.save(
            tenant=tenant,
            user=self.request.user
        )


class SenderIDRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a sender ID request."""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return sender ID requests for the current tenant."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return SenderIDRequest.objects.none()
        
        return SenderIDRequest.objects.filter(tenant=tenant)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SenderIDRequestCreateSerializer
        return SenderIDRequestSerializer


class SenderIDRequestReviewView(generics.UpdateAPIView):
    """Review sender ID requests (admin only)."""
    
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = SenderIDRequestReviewSerializer
    
    def get_queryset(self):
        """Return all pending sender ID requests."""
        return SenderIDRequest.objects.filter(status='pending').order_by('-created_at')
    
    def perform_update(self, serializer):
        """Review the sender ID request."""
        instance = self.get_object()
        
        if serializer.validated_data['status'] == 'approved':
            instance.approve(self.request.user)
        else:
            instance.reject(
                self.request.user,
                serializer.validated_data.get('rejection_reason', '')
            )


class SenderIDUsageListCreateView(generics.ListCreateAPIView):
    """List sender ID usage or attach sender ID to SMS package."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SenderIDUsageCreateSerializer
        return SenderIDUsageSerializer
    
    def get_queryset(self):
        """Return sender ID usage for the current tenant."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return SenderIDUsage.objects.none()
        
        return SenderIDUsage.objects.filter(tenant=tenant).order_by('-attached_at')
    
    def perform_create(self, serializer):
        """Attach sender ID to SMS package."""
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            raise ValueError("No tenant found for this user")
        
        serializer.save(tenant=tenant)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_sender_ids(request):
    """Get available sender IDs for the current tenant."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return Response(
            {"error": "No tenant found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get approved sender ID requests
    approved_requests = SenderIDRequest.objects.filter(
        tenant=tenant,
        status='approved'
    ).values('id', 'requested_sender_id', 'sample_content')
    
    return Response({
        "available_sender_ids": list(approved_requests)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_default_sender_id(request):
    """Request to use the default sender ID (Taarifa-SMS)."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return Response(
            {"error": "No tenant found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Note: SMS purchase is now optional - users can request sender ID first
    
    # Check if default sender ID request already exists
    existing_request = SenderIDRequest.objects.filter(
        tenant=tenant,
        requested_sender_id='Taarifa-SMS'
    ).exclude(status='rejected').first()
    
    if existing_request:
        return Response(
            {"error": "A request for the default sender ID already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create request for default sender ID
    request_data = {
        'request_type': 'default',
        'requested_sender_id': 'Taarifa-SMS',
        'sample_content': 'A test use case for the sender name purposely used for information transfer.',
        'business_justification': 'Requesting to use the default sender ID for SMS messaging.'
    }
    
    serializer = SenderIDRequestCreateSerializer(
        data=request_data,
        context={'tenant': tenant}
    )
    
    if serializer.is_valid():
        sender_id_request = serializer.save(
            tenant=tenant,
            user=request.user
        )
        
        # Auto-approve default sender ID requests
        sender_id_request.approve(request.user)
        
        return Response(
            {
                "message": "Default sender ID request approved and created successfully",
                "sender_id_request": SenderIDRequestSerializer(sender_id_request).data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detach_sender_id(request, usage_id):
    """Detach sender ID from SMS package."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return Response(
            {"error": "No tenant found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        usage = SenderIDUsage.objects.get(
            id=usage_id,
            tenant=tenant,
            is_active=True
        )
        
        usage.detach()
        
        return Response(
            {"message": "Sender ID detached from SMS package successfully"},
            status=status.HTTP_200_OK
        )
    
    except SenderIDUsage.DoesNotExist:
        return Response(
            {"error": "Sender ID usage not found"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sender_id_request_status(request):
    """Get the status of sender ID requests for the current tenant."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return Response(
            {"error": "No tenant found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get all requests for this tenant
    requests = SenderIDRequest.objects.filter(tenant=tenant).order_by('-created_at')
    
    # Get SMS balance info
    sms_balance = tenant.sms_balance if hasattr(tenant, 'sms_balance') else None
    
    return Response({
        "sms_balance": {
            "credits": sms_balance.credits if sms_balance else 0,
            "total_purchased": sms_balance.total_purchased if sms_balance else 0,
            "can_request_sender_id": True  # Users can always request sender IDs now
        },
        "sender_id_requests": SenderIDRequestSerializer(requests, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_sender_request(request):
    """
    Submit a new sender ID request.
    This endpoint is provided for frontend compatibility.
    POST /api/messaging/sender-requests/submit/
    """
    try:
        # Get tenant
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use the serializer to validate and create
        serializer = SenderIDRequestCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            sender_request = serializer.save(tenant=tenant, user=request.user)
            return Response({
                'success': True,
                'message': 'Sender ID request submitted successfully',
                'data': SenderIDRequestSerializer(sender_request).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to submit sender ID request',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)