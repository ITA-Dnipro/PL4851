from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_staff or user.pk == view.kwargs['id']
