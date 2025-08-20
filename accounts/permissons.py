from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    # for gerges: this one controls the edit to be restricted to the owner and anyone can read
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

class IsVerifiedUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsOwner(permissions.BasePermission):
   
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsAdminOrOwner(permissions.BasePermission):
  
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
