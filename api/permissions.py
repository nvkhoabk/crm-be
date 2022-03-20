from rest_framework import permissions
from api.models.organization import UserRole


class SuperAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class CompanyAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.Meta:
            permission_field = obj.Meta.permission_field
            permission_class = obj.Meta.permission_class
            value = obj[permission_field]
            filter = {
                'user': request.user,
                'deleted_at__isnull': True,
                permission_class + '__id': value
            }
            if UserRole.objects.filter(**filter).first():
                return True
            else:
                return False 
        return True 
