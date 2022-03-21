from api.common.base_service import BaseService
from api.common.cookies import Cookies
from django.contrib.auth import authenticate, login, logout
from api.services import exceptions
from api.models.organization import UserRole, Permission


class AuthLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user = authenticate(**kwargs)
        if user is None:
            raise exceptions.AuthLoginInvalid()
        login(request, user)
        return user


class AuthLogoutService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_authenticated:
            raise exceptions.AuthLogoutNotLoggedIn()
        logout(request)


class AuthGetUserInfoService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user = request.user

        response = {
            'is_superuser': user.is_superuser,
            'username': user.username,
        }

        user_roles = UserRole.objects.filter(
            user=user,
            deleted_at__isnull=True,
        )

        roles = []

        for position in user_roles:
            data = {
                'company': None,
                'department': None,
                'role': None,
                'edit_permissions': [],
                'read_permissions': [],
            }

            company = position.company
            data['company'] = {
                'id': company.id,
                'name': company.name,
            }

            department = position.department
            if department:
                data['department'] = {
                    'id': department.id,
                    'department_name': department.department_name,
                }
                
            role = position.role
            if role:
                data['role'] = {
                    'id': role.id,
                    'role_name': role.role_name,
                }

                try:
                    permission_obj = Permission.objects.get(
                        company=company,
                        department=department,
                        role=role,
                    )
                    data['edit_permissions'] = json.loads(permission_obj.edit_permissions)
                    data['read_permissions'] = json.loads(permission_obj.read_permissions)
                except Permission.DoesNotExist:
                    pass

            roles.append(data)
        
        response['roles'] = roles
        return response
