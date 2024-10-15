from rest_framework.permissions import BasePermission


class IsStaffOrReadOnly(BasePermission):
    """If request.user is stuff - allow to create records in DB."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsStaff(BasePermission):
    """Only for moderation history viewset."""

    def has_permission(self, request, view):
        return request.user.is_staff
