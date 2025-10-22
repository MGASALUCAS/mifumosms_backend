"""
Views for sender ID request system.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .models_sender_requests import SenderIDRequest, SenderIDUsage
from .models_sms import SMSSenderID
from .serializers_sender_requests import (
    SenderIDRequestSerializer, SenderIDRequestCreateSerializer,
    SenderIDRequestReviewSerializer, SenderIDUsageSerializer,
    SenderIDUsageCreateSerializer
)
from billing.models import SMSPackage
from .services.sms_service import SMSService


class SenderIDRequestListCreateView(generics.ListCreateAPIView):
    """List sender ID requests or create a new request."""
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SenderIDRequestCreateSerializer
        return SenderIDRequestSerializer
    
    def get_queryset(self):
        """Return sender ID requests for the current tenant."""
        tenant = getattr(self.request.user, 'tenant', None)
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
        tenant = getattr(self.request.user, 'tenant', None)
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
        tenant = getattr(self.request.user, 'tenant', None)
        if not tenant:
            return SenderIDRequest.objects.none()
        
        return SenderIDRequest.objects.filter(tenant=tenant)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SenderIDRequestCreateSerializer
        return SenderIDRequestSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to return JSON response instead of 204."""
        instance = self.get_object()
        sender_id = instance.requested_sender_id
        self.perform_destroy(instance)
        
        return Response({
            'success': True,
            'message': f'Sender ID request "{sender_id}" has been deleted successfully',
            'deleted_id': str(instance.id)
        }, status=status.HTTP_200_OK)


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
            # If a non-default sender is approved, end default sender usage
            if instance.request_type != 'default':
                try:
                    # Detach any active default sender usage
                    default_usage = (
                        SenderIDUsage.objects
                        .filter(
                            tenant=instance.tenant,
                            is_active=True,
                            sender_id_request__requested_sender_id='Taarifa-SMS'
                        )
                        .first()
                    )
                    if default_usage:
                        default_usage.is_active = False
                        default_usage.detached_at = timezone.now()
                        default_usage.save(update_fields=['is_active', 'detached_at'])

                    # Optionally cancel any pending default sender request
                    pending_default = (
                        SenderIDRequest.objects
                        .filter(
                            tenant=instance.tenant,
                            requested_sender_id='Taarifa-SMS',
                            status='pending'
                        )
                        .first()
                    )
                    if pending_default:
                        pending_default.status = 'cancelled'
                        pending_default.save(update_fields=['status'])
                except Exception:
                    # Non-fatal: do not block approval on cleanup failures
                    pass
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
    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        return Response(
            {"error": "No tenant found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get approved sender ID requests (local)
    approved_requests = list(SenderIDRequest.objects.filter(
        tenant=tenant,
        status='approved'
    ).values('id', 'requested_sender_id', 'sample_content'))

    # Also include any active SMSSenderID records (e.g., auto-created for admins)
    active_sender_ids = list(SMSSenderID.objects.filter(
        tenant=tenant,
        status='active'
    ).values('sender_id', 'sample_content'))

    # Merge into a unified list of available sender IDs (dedupe by name)
    seen = set()
    unified = []
    for item in approved_requests:
        sid = item.get('requested_sender_id')
        if sid and sid not in seen:
            unified.append({'requested_sender_id': sid, 'sample_content': item.get('sample_content', '')})
            seen.add(sid)
    for item in active_sender_ids:
        sid = item.get('sender_id')
        if sid and sid not in seen:
            unified.append({'requested_sender_id': sid, 'sample_content': item.get('sample_content', '')})
            seen.add(sid)

    # Fetch active sender IDs from Beem for visibility
    beem_ids = []
    try:
        service = SMSService(tenant_id=str(tenant.id))
        provider_result = service.get_sender_ids(status='active')
        if provider_result.get('success'):
            # Normalize to a lean structure
            beem_ids = [
                {
                    'senderid': item.get('senderid'),
                    'status': item.get('status'),
                    'id': item.get('id')
                }
                for item in provider_result.get('sender_ids', [])
                if (item or {}).get('status') == 'active'
            ]
    except Exception as e:
        # Non-fatal: just omit provider list on errors
        beem_ids = []

    return Response({
    "available_sender_ids": unified,
        "provider": {
            "name": "Beem Africa",
            "active_sender_ids": beem_ids
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_default_sender_id(request):
    """Request to use the default sender ID (Taarifa-SMS)."""
    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        return Response(
            {"error": "No tenant found for this user"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Note: SMS purchase is now optional - users can request sender ID first
    
    # Idempotent behavior: if a PENDING exists, return it; if APPROVED exists, inform
    existing_request = SenderIDRequest.objects.filter(
        tenant=tenant,
        requested_sender_id='Taarifa-SMS'
    ).order_by('-created_at').first()

    if existing_request:
        if existing_request.status == 'pending':
            return Response(
                {
                    "success": True,
                    "message": "Default sender ID request already pending",
                    "sender_id_request": SenderIDRequestSerializer(existing_request).data
                },
                status=status.HTTP_200_OK
            )
        if existing_request.status == 'approved':
            return Response(
                {
                    "success": True,
                    "message": "Default sender ID already approved",
                    "sender_id_request": SenderIDRequestSerializer(existing_request).data
                },
                status=status.HTTP_200_OK
            )
    
    # Create request for default sender ID
    request_data = {
        'request_type': 'default',
        'requested_sender_id': 'Taarifa-SMS',
        'sample_content': 'A test use case for the sender name purposely used for information transfer.',
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
        
        # Do NOT auto-approve; leave as pending for admin review
        return Response(
            {
                "message": "Default sender ID request submitted and pending approval",
                "sender_id_request": SenderIDRequestSerializer(sender_id_request).data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_default_sender_id(request):
    """Cancel default sender ID usage/request for current tenant.
    - If an active usage exists for default sender, mark usage inactive (detach).
    - If a pending/approved request exists, mark it as cancelled when appropriate.
    """
    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        return Response(
            {"success": False, "message": "User is not associated with any tenant"},
            status=status.HTTP_400_BAD_REQUEST
        )

    DEFAULT_SENDER = 'Taarifa-SMS'

    # Detach any active usage of default sender
    usage = (
        SenderIDUsage.objects
        .filter(tenant=tenant, is_active=True, sender_id_request__requested_sender_id=DEFAULT_SENDER)
        .select_related('sender_id_request')
        .first()
    )
    if usage:
        usage.is_active = False
        usage.detached_at = timezone.now()
        usage.save()

    # Cancel latest non-cancelled request for default sender if pending
    latest_req = (
        SenderIDRequest.objects
        .filter(tenant=tenant, requested_sender_id=DEFAULT_SENDER)
        .order_by('-created_at')
        .first()
    )
    if latest_req and latest_req.status == 'pending':
        latest_req.status = 'cancelled'
        latest_req.save(update_fields=['status'])

    return Response({
        'success': True,
        'message': 'Default sender ID has been cancelled/detached successfully'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def detach_sender_id(request, usage_id):
    """Detach sender ID from SMS package."""
    tenant = getattr(request.user, 'tenant', None)
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
    tenant = getattr(request.user, 'tenant', None)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def default_sender_overview(request):
    """
    Frontend-friendly overview for default sender ID CTA.
    GET /api/messaging/sender-requests/default/overview/
    """
    from messaging.models_sms import SMSSenderID
    tenant = getattr(request.user, 'tenant', None)
    if not tenant:
        return Response({
            'success': False,
            'message': 'User is not associated with any tenant'
        }, status=status.HTTP_400_BAD_REQUEST)

    DEFAULT_SENDER = 'Taarifa-SMS'

    latest_req = (
        SenderIDRequest.objects
        .filter(tenant=tenant, requested_sender_id=DEFAULT_SENDER)
        .order_by('-created_at')
        .first()
    )

    active_usage = (
        SenderIDUsage.objects
        .filter(tenant=tenant, is_active=True)
        .select_related('sender_id_request')
        .first()
    )

    current_sender_id = None
    if active_usage and getattr(active_usage, 'sender_id_request', None):
        current_sender_id = getattr(active_usage.sender_id_request, 'requested_sender_id', None)
    else:
        # Fallback: if tenant has any active SMSSenderID, use the first as current
        active_sender = SMSSenderID.objects.filter(tenant=tenant, status='active').first()
        if active_sender:
            current_sender_id = active_sender.sender_id

    can_request = True
    reason = None
    is_available = False
    
    # Check if default sender ID is available
    if current_sender_id == DEFAULT_SENDER:
        is_available = True
        can_request = False
        reason = 'Default sender already attached.'
    elif latest_req and latest_req.status == 'approved':
        is_available = True
        can_request = False
        reason = 'Default sender already approved.'
    elif latest_req and latest_req.status == 'pending':
        can_request = False
        reason = 'Request already pending.'
    else:
        # Check if there's an active SMSSenderID for the default sender
        active_default = SMSSenderID.objects.filter(
            tenant=tenant,
            sender_id=DEFAULT_SENDER,
            status='active'
        ).first()
        
        if active_default:
            is_available = True
            can_request = False
            reason = 'Default sender already available.'

    credits = 0
    needs_purchase = False
    try:
        from billing.models import SMSBalance
        bal = SMSBalance.objects.filter(tenant=tenant).first()
        credits = getattr(bal, 'credits', 0) if bal else 0
        needs_purchase = (credits or 0) <= 0
    except Exception:
        pass

    return Response({
        'success': True,
        'data': {
            'default_sender': DEFAULT_SENDER,
            'current_sender_id': current_sender_id,
            'active_request': SenderIDRequestSerializer(latest_req).data if latest_req else None,
            'is_available': is_available,
            'can_request': can_request,
            'reason': reason,
            'balance': {
                'credits': credits,
                'needs_purchase': needs_purchase
            },
            'actions': {
                'request_default_url': '/api/messaging/sender-id-requests/request-default/',
                'status_url': '/api/messaging/sender-id-requests/status/',
                'available_url': '/api/messaging/sender-id-requests/available/',
                'purchase_url': '/api/billing/sms/purchase/'
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def refresh_sender_requests(request):
    """
    Refresh sender ID requests data for the frontend.
    GET /api/messaging/sender-requests/refresh/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all requests for the tenant
        requests = SenderIDRequest.objects.filter(tenant=tenant).order_by('-created_at')
        
        # Calculate statistics
        stats = {
            'total_requests': requests.count(),
            'pending_requests': requests.filter(status='pending').count(),
            'approved_requests': requests.filter(status='approved').count(),
            'rejected_requests': requests.filter(status='rejected').count(),
            'cancelled_requests': requests.filter(status='cancelled').count(),
        }
        
        return Response({
            'success': True,
            'data': {
                'stats': stats,
                'requests': SenderIDRequestSerializer(requests, many=True).data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to refresh sender requests',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sender_requests_stats(request):
    """
    Get statistics for sender ID requests and active sender IDs.
    GET /api/messaging/sender-requests/stats/
    """
    try:
        # Get tenant
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Import SMSSenderID model
        from messaging.models_sms import SMSSenderID
        
        # Get all requests for the tenant
        all_requests = SenderIDRequest.objects.filter(tenant=tenant)
        
        # Get all active SMS sender IDs for the tenant
        active_sms_sender_ids = SMSSenderID.objects.filter(tenant=tenant, status='active')
        
        # Calculate statistics for requests
        request_stats = {
            'total_requests': all_requests.count(),
            'pending_requests': all_requests.filter(status='pending').count(),
            'approved_requests': all_requests.filter(status='approved').count(),
            'rejected_requests': all_requests.filter(status='rejected').count(),
            'requires_changes_requests': all_requests.filter(status='requires_changes').count(),
        }
        
        # Calculate statistics for active sender IDs
        active_stats = {
            'total_active': active_sms_sender_ids.count(),
            'active_sender_ids': list(active_sms_sender_ids.values('id', 'sender_id', 'status', 'created_at'))
        }
        
        # Combined statistics (what frontend expects)
        stats = {
            'total_requests': request_stats['total_requests'] + active_stats['total_active'],
            'pending_requests': request_stats['pending_requests'],
            'approved_requests': request_stats['approved_requests'] + active_stats['total_active'],  # Include active SMS sender IDs
            'rejected_requests': request_stats['rejected_requests'],
            'requires_changes_requests': request_stats['requires_changes_requests'],
        }
        
        # Recent requests (last 5)
        recent_requests = all_requests.order_by('-created_at')[:5]
        recent_requests_data = SenderIDRequestSerializer(recent_requests, many=True).data
        
        return Response({
            'success': True,
            'data': {
                'stats': stats,
                'request_stats': request_stats,
                'active_stats': active_stats,
                'recent_requests': recent_requests_data
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to get sender request statistics',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_sender_request(request, pk):
    """
    Delete a sender ID request.
    DELETE /api/messaging/sender-requests/{id}/delete/
    """
    try:
        tenant = getattr(request.user, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'User is not associated with any tenant'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the sender request
        sender_request = SenderIDRequest.objects.get(
            pk=pk,
            tenant=tenant
        )
        
        sender_id = sender_request.requested_sender_id
        sender_request.delete()
        
        return Response({
            'success': True,
            'message': f'Sender ID request "{sender_id}" has been deleted successfully',
            'deleted_id': str(pk)
        }, status=status.HTTP_200_OK)
        
    except SenderIDRequest.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Sender ID request not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Failed to delete sender ID request',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        serializer = SenderIDRequestCreateSerializer(data=request.data, context={'request': request, 'tenant': tenant})
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