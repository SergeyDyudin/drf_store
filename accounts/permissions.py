from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        MAP_ACTION_TO_CONDITIONS = {
            'list': request.user.is_authenticated and request.user.is_staff,
            'create': True,
            'retrieve': True,
            'update': True,
            'partial_update': True,
            'destroy': True,
        }

        return bool(MAP_ACTION_TO_CONDITIONS.get(view.action))

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        MAP_ACTION_TO_CONDITIONS = {
            'retrieve': obj == request.user or request.user.is_staff,
            'update': obj == request.user or request.user.is_staff,
            'partial_update': obj == request.user or request.user.is_staff,
            'destroy': request.user.is_staff,
        }

        return bool(MAP_ACTION_TO_CONDITIONS.get(view.action))
