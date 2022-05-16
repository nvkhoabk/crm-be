from rest_framework import permissions
from rest_framework.utils import json

from api.models.organization import UserRole, User, Permission


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


class ModulePermission(permissions.BasePermission):
    MODULE_NAME = ''

    def has_module_permission(self, permission_obj):
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }

        user_roles = UserRole.objects.filter(**filter)
        # Admin company can access to all api
        first_user_role = user_roles.first()
        if first_user_role.department_id is None and first_user_role.role_id is None:
            return True

        for position in user_roles:
            company = position.company
            department = position.department
            role = position.role
            if role:
                try:
                    permission_obj = Permission.objects.get(
                        company=company,
                        department=department,
                        role=role,
                    )
                    if self.has_module_permission(permission_obj):
                        return True

                except Permission.DoesNotExist:
                    pass

        return False


class ModuleReadPermission(ModulePermission):
    def has_module_permission(self, permission_obj):
        if self.MODULE_NAME in json.loads(permission_obj.read_permissions):
            return True

        # Edit permission is treated as Read Permission
        if self.MODULE_NAME in json.loads(permission_obj.edit_permissions):
            return True

        return False


class ModuleEditPermission(ModulePermission):
    def has_module_permission(self, permission_obj):
        return self.MODULE_NAME in json.loads(permission_obj.edit_permissions)


class ProductReadPermission(ModuleReadPermission):
    MODULE_NAME = 'PRODUCT_AND_WAREHOUSE'


class ProductEditPermission(ModuleEditPermission):
    MODULE_NAME = 'PRODUCT_AND_WAREHOUSE'


class CallCenterAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        secret = request.GET.get('secret', None)
        return secret == 'Crm1ty@1305Fri'
