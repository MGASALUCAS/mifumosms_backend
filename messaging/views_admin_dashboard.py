"""
Admin dashboard views for sender name requests management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models_sms import SenderNameRequest
from .serializers_sms import SenderNameRequestSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_sender_requests_dashboard(request):
    """
    Admin dashboard for sender name requests management.

    GET /api/messaging/admin/sender-requests/dashboard/

    Returns comprehensive statistics and recent requests for admin dashboard.
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get tenant from request
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all requests for the tenant
        all_requests = SenderNameRequest.objects.filter(tenant=tenant)

        # Calculate statistics
        stats = {
            'total_requests': all_requests.count(),
            'pending_requests': all_requests.filter(status='pending').count(),
            'approved_requests': all_requests.filter(status='approved').count(),
            'rejected_requests': all_requests.filter(status='rejected').count(),
            'requires_changes_requests': all_requests.filter(status='requires_changes').count(),
        }

        # Recent requests (last 10)
        recent_requests = all_requests.order_by('-created_at')[:10]
        recent_requests_data = SenderNameRequestSerializer(recent_requests, many=True).data

        # Requests by status
        status_breakdown = all_requests.values('status').annotate(count=Count('id')).order_by('status')

        # Requests by user
        user_breakdown = all_requests.values(
            'created_by__email',
            'created_by__first_name',
            'created_by__last_name'
        ).annotate(count=Count('id')).order_by('-count')

        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_activity = all_requests.filter(created_at__gte=week_ago).count()

        # Pending requests that need attention
        pending_requests = all_requests.filter(status='pending').order_by('created_at')
        pending_requests_data = SenderNameRequestSerializer(pending_requests, many=True).data

        return Response({
            'success': True,
            'data': {
                'stats': stats,
                'recent_requests': recent_requests_data,
                'status_breakdown': list(status_breakdown),
                'user_breakdown': list(user_breakdown),
                'recent_activity': recent_activity,
                'pending_requests': pending_requests_data,
                'tenant_name': tenant.name,
                'admin_user': request.user.email
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching dashboard data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_sender_requests_list(request):
    """
    Admin list view for all sender name requests with filtering and pagination.

    GET /api/messaging/admin/sender-requests/list/

    Query Parameters:
    - status: Filter by status
    - user: Filter by user email
    - search: Search in sender_name and use_case
    - page: Page number
    - page_size: Items per page
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get tenant from request
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all requests for the tenant
        queryset = SenderNameRequest.objects.filter(tenant=tenant)

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        user_filter = request.query_params.get('user')
        if user_filter:
            queryset = queryset.filter(created_by__email__icontains=user_filter)

        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(sender_name__icontains=search_query) |
                Q(use_case__icontains=search_query)
            )

        # Order by creation date
        queryset = queryset.order_by('-created_at')

        # Simple pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size

        total_count = queryset.count()
        requests = queryset[start:end]

        # Serialize data
        requests_data = SenderNameRequestSerializer(requests, many=True).data

        return Response({
            'success': True,
            'data': {
                'results': requests_data,
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'has_next': end < total_count,
                'has_previous': page > 1
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching requests list: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_bulk_update_requests(request):
    """
    Admin bulk update for sender name requests.

    POST /api/messaging/admin/sender-requests/bulk-update/

    Request Body:
    {
        "request_ids": ["uuid1", "uuid2", ...],
        "status": "approved",
        "admin_notes": "Bulk approval after review"
    }
    """
    try:
        # Check if user is admin
        if not request.user.is_staff:
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get tenant from request
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({
                'success': False,
                'message': 'No tenant found. Please contact support.'
            }, status=status.HTTP_400_BAD_REQUEST)

        request_ids = request.data.get('request_ids', [])
        new_status = request.data.get('status')
        admin_notes = request.data.get('admin_notes', '')

        if not request_ids or not new_status:
            return Response({
                'success': False,
                'message': 'request_ids and status are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update requests
        updated_count = 0
        for request_id in request_ids:
            try:
                sender_request = SenderNameRequest.objects.get(
                    id=request_id,
                    tenant=tenant
                )
                sender_request.status = new_status
                sender_request.admin_notes = admin_notes
                sender_request.reviewed_by = request.user
                sender_request.reviewed_at = timezone.now()
                sender_request.save()
                updated_count += 1
            except SenderNameRequest.DoesNotExist:
                continue

        return Response({
            'success': True,
            'message': f'Successfully updated {updated_count} requests',
            'data': {
                'updated_count': updated_count,
                'total_requested': len(request_ids)
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error updating requests: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
