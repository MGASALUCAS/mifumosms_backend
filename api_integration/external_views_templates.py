"""
External Templates API views for integrations.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .utils import format_api_response


@api_view(['GET'])
def list_templates(request):
    """List templates."""
    if not hasattr(request, 'auth') or not request.auth:
        return Response(format_api_response(
            success=False,
            message="Authentication required"
        ), status=status.HTTP_401_UNAUTHORIZED)
    
    # Get account
    if hasattr(request.auth, 'api_account'):
        account = request.auth.api_account
    else:
        account = request.auth
    
    # For now, return empty list as templates are not implemented yet
    return Response(format_api_response(
        success=True,
        data={
            'templates': [],
            'total': 0
        },
        message="Templates retrieved successfully"
    ))


@api_view(['POST'])
def create_template(request):
    """Create a template."""
    return Response(format_api_response(
        success=False,
        message="Templates feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET'])
def get_template(request, template_id):
    """Get a template."""
    return Response(format_api_response(
        success=False,
        message="Templates feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['PUT'])
def update_template(request, template_id):
    """Update a template."""
    return Response(format_api_response(
        success=False,
        message="Templates feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['DELETE'])
def delete_template(request, template_id):
    """Delete a template."""
    return Response(format_api_response(
        success=False,
        message="Templates feature not implemented yet",
        error_code="NOT_IMPLEMENTED"
    ), status=status.HTTP_501_NOT_IMPLEMENTED)

