from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import User

class IsVerified(BasePermission):
    
    def has_permission(self, request, view):
        email=request.data["email"]
        
        # email=request.user.email
        try:
            user=User.objects.get(email=email)
            if user.is_verified==1:
                return True
            raise PermissionDenied
        except User.DoesNotExist:
            raise PermissionDenied("No User found with this email")
        