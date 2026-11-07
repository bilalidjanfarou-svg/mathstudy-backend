from rest_framework.permissions import BasePermission


class EstCreateur(BasePermission):
    """Créateurs et administrateurs."""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role in ('creator', 'admin'))


class EstAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == 'admin')