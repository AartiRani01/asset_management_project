from rest_framework.permissions import BasePermission

class GroupBasedPermission(BasePermission):
    """
    Custom permission class to allow access based on user groups.
    """

    message = "You do not have permission to access this API"

    def has_permission(self, request, view):
        """
        This method checks whether the user has permission
        to access the given API view.
        """

        # Get the currently logged-in user
        user = request.user

        # If user is not authenticated (not logged in), deny access
        if not user.is_authenticated:
            return False

        # If user belongs to MANAGER group, allow full access
        if user.groups.filter(name="MANAGER").exists():
            return True

        # Get allowed_groups from the view (if defined)
        # Example: allowed_groups = ["CEO", "MANAGER" , "OPERATOR"]
        allowed_groups = getattr(view, 'allowed_groups', [])

        # Check if user belongs to any allowed group
        if user.groups.filter(name__in=allowed_groups).exists():
            return True

        # If none of the above conditions match, deny access
        return False

#from rest_framework.permissions import BasePermission


# class GroupBasedPermission(BasePermission):
#     message = "You do not have permission to access this API."

#     def has_permission(self, request, view):

#         if not request.user or not request.user.is_authenticated:
#             return False

#         allowed_groups = getattr(view, 'allowed_groups', None)

#         if not allowed_groups:
#             return True  # if no group restriction

#         user_groups = request.user.groups.values_list('name', flat=True)

#         return any(group in user_groups for group in allowed_groups)