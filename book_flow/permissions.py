from rest_framework.permissions import BasePermission


class IsLibrarian(BasePermission):
    """
    Custom permission to only allow librarians to make changes.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_librarian
