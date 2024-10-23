from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, recipe):
        return (
            True if request.method in permissions.SAFE_METHODS
            else recipe.author == request.user
        )
