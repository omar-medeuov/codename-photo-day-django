"""
Custom permissions for the todos app.

This module contains custom permission classes for Todo access control.
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.

    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        """Check if the requesting user is the owner of the object."""
        return obj.user == request.user
