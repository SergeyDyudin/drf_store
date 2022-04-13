from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action == 'list':
            return bool(request.user.is_authenticated and request.user.is_staff)   # TODO:
        if view.action == 'change_password':
            return bool(request.user.is_authenticated)  # TODO:
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if view.action in ('retrieve', 'update', 'partial_update', 'change_password'):
            return bool(obj == request.user or request.user.is_staff)  # TODO:
        if view.action == 'destroy':
            return bool(request.user.is_staff)  # TODO:

        if request.user.is_staff:
            return True
        if view.action in ('retrieve', 'update', 'partial_update', 'change_password'):
            return bool(obj == request.user)

        return False
