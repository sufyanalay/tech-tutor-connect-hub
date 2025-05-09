
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsSameUserOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow users to edit their own profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the user themselves
        return obj == request.user


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
        
        
class IsTeacher(permissions.BasePermission):
    """
    Allows access only to teachers.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'teacher')
        
        
class IsTechnician(permissions.BasePermission):
    """
    Allows access only to technicians.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'technician')
        
        
class IsStudent(permissions.BasePermission):
    """
    Allows access only to students.
    """
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'student')
