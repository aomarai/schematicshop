"""
Middleware for checking user ban status
"""
from django.utils import timezone
from django.http import JsonResponse
from rest_framework import status


class BanCheckMiddleware:
    """
    Middleware to check if authenticated user is banned
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and banned
        if request.user.is_authenticated and hasattr(request.user, 'is_banned'):
            # Allow access to auth endpoints so users can check their ban status
            allowed_paths = [
                '/api/auth/me/',
                '/api/auth/login/',
                '/api/auth/refresh/',
                '/api/auth/register/',
                '/admin/',
            ]
            
            # Check if current path is allowed
            path_allowed = any(request.path.startswith(path) for path in allowed_paths)
            
            if not path_allowed and request.user.is_banned:
                ban_message = 'Your account has been banned.'
                
                if request.user.ban_reason:
                    ban_message += f' Reason: {request.user.ban_reason}'
                
                if request.user.ban_expires_at:
                    ban_message += f' Your ban expires at {request.user.ban_expires_at.isoformat()}'
                else:
                    ban_message += ' This is a permanent ban.'
                
                return JsonResponse(
                    {
                        'error': 'Account banned',
                        'message': ban_message,
                        'ban_expires_at': request.user.ban_expires_at.isoformat() if request.user.ban_expires_at else None
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
        
        response = self.get_response(request)
        return response
