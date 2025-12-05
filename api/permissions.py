from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/view it.
    Admins have full access.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # BUT we only want them to see their OWN data.
        
        # 1. Superusers (Admins) can do anything
        if request.user.is_superuser:
            return True

        # 2. For FarmProfile, check if the user matches the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
            
        # 3. For objects linked to a Farm (like FieldPlot), check the farm's owner
        if hasattr(obj, 'farm'):
            return obj.farm.user == request.user
            
        # 4. For objects linked to a Plot (like SensorReading), check the plot -> farm -> owner
        if hasattr(obj, 'plot'):
            return obj.plot.farm.user == request.user

        return False