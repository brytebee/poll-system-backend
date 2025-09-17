from rest_framework import permissions

class IsPollOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a poll to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner of the poll
        return obj.created_by == request.user

class CanVotePermission(permissions.BasePermission):
    """
    Custom permission for voting
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if poll can accept votes
        if not obj.can_vote:
            return False
        
        # Anonymous polls allow anyone to vote
        if obj.is_anonymous:
            return True
        
        # Non-anonymous polls require authentication
        return request.user.is_authenticated

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Generic permission for owner-based access
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check for owner attribute (works with created_by, user, etc.)
        owner_field = getattr(view, 'owner_field', 'created_by')
        owner = getattr(obj, owner_field, None)
        
        return owner == request.user
