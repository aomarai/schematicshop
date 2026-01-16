"""
Custom permissions for moderation
"""
from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Permission to check if user is a moderator (staff member)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Permission to allow moderators to edit, others to read only
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_staff
