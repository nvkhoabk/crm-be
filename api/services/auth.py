import json
from api.common.base_service import BaseService
from api.common.cookies import Cookies
from django.contrib.auth import authenticate, login, logout

from api.models.call_center import CallAgent
from api.services import exceptions
from api.models.organization import UserRole, Permission
from api.const import MODULES, Const


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
        response['menu'] = []

        if user.is_superuser:
            response['menu'] = [MODULES.COMPANY_MANAGEMENT, MODULES.ADMIN_MANAGEMENT]
        elif len(response['roles']) == 1 and response['roles'][0]['role'] is None and response['roles'][0][
            'department'] is None:
            response['menu'] = [MODULES.USER_MANAGEMENT, MODULES.PRODUCT_AND_WAREHOUSE]
        else:
            for role in roles:
                for permission in role['edit_permissions']:
                    if permission not in response['menu']:
                        response['menu'].append(permission)
                for permission in role['read_permissions']:
                    if permission not in response['menu']:
                        response['menu'].append(permission)

        response['call_center'] = {
            'ext': None,
            'secret': None,
            'sip_server': None
        }

        try:
            call_agents = CallAgent.objects.filter(user_id=user, deleted_at__isnull=True)
            if len(call_agents) > 0:
                call_agent = call_agents[0]
                response['call_center']['ext'] = call_agent.name
                response['call_center']['secret'] = call_agent.secret
                response['call_center']['sip_server'] = Const.SIP_SERVER
        except CallAgent.DoesNotExist:
            pass

        return response
