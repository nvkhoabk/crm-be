import json
from api.common.base_service import BaseService
from api.common.cookies import Cookies
from django.contrib.auth import authenticate, login, logout

from api.models.call_center import CallAgent, CallCenter
from api.services import exceptions
from api.models.organization import UserRole, Permission, TokenUserStatus
from api.const import MODULES, Const, CALL_AGENT_STATUS
from rest_framework_simplejwt.tokens import RefreshToken


class AuthLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        from rest_framework_simplejwt.authentication import JWTAuthentication
        auth = JWTAuthentication()
        validated_token = auth.get_validated_token(args[0])
        user = auth.get_user(validated_token)
        TokenUserStatus.objects.filter(user=user).delete()
        TokenUserStatus.objects.create(user=user, current_token=args[0])


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
            'id': user.id
        }

        user_roles = UserRole.objects.filter(
            user=user,
            deleted_at__isnull=True,
        )

        roles = []
        company_id = 0
        company = None
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
            company_id = company.id
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
            response['menu'] = [MODULES.COMPANY_MANAGEMENT, MODULES.ADMIN_MANAGEMENT,
                                MODULES.CALL_CENTER_LIST_MANAGEMENT, MODULES.PARAM_CONFIG]
        elif len(response['roles']) == 1 and response['roles'][0]['role'] is None \
                and response['roles'][0]['department'] is None:
            response['menu'] = [MODULES.USER_MANAGEMENT, MODULES.DATA_MANAGEMENT, MODULES.ACCOUNTING,
                                MODULES.PRODUCT_AND_WAREHOUSE, MODULES.MARKETING,
                                MODULES.SYSTEM_CONFIGURATION, MODULES.REPORT, MODULES.PHONE_NUMBER_MANAGER,
                                MODULES.PHONE_NUMBER_TECHNICAL]

            call_center = CallCenter.objects.filter(company_id=company_id, deleted_at__isnull=True).order_by(
                '-id').first()

            if call_center is not None and call_center.is_enable:
                response['menu'].append(MODULES.CALL_CENTER_MANAGEMENT)
            else:
                response['menu'].append(MODULES.CALL_CENTER_ABOUT)
        else:
            for role in roles:
                for permission in role['edit_permissions']:
                    if permission not in response['menu']:
                        response['menu'].append(permission)
                for permission in role['read_permissions']:
                    if permission not in response['menu']:
                        response['menu'].append(permission)

        # Sale user can view phone number manager
        if MODULES.DATA_MANAGEMENT_FOR_SALE in response['menu']:
            response['menu'].append(MODULES.PHONE_NUMBER_MANAGER)

        response['phone_number'] = True
        if company and not company.enable_phone_number_management:
            response['phone_number'] = False
            if MODULES.PHONE_NUMBER_MANAGER in response['menu']:
                response['menu'].remove(MODULES.PHONE_NUMBER_MANAGER)
            if MODULES.PHONE_NUMBER_TECHNICAL in response['menu']:
                response['menu'].remove(MODULES.PHONE_NUMBER_TECHNICAL)

        response['call_center'] = {
            'ext': None,
            'secret': None,
            'sip_server': None
        }


        try:
            if CallCenter.objects.filter(company_id=company_id, deleted_at__isnull=True, is_enable=True):
                call_agents = CallAgent.objects.filter(user_id=user, deleted_at__isnull=True,
                                                       status=CALL_AGENT_STATUS.ACTIVE)
                if len(call_agents) > 0:
                    call_agent = call_agents[0]
                    response['call_center']['ext'] = call_agent.name
                    response['call_center']['secret'] = call_agent.secret
                    response['call_center']['sip_server'] = Const.SIP_SERVER
                    response['call_center']['tenant'] = call_agent.tenant
        except CallAgent.DoesNotExist:
            pass

        return response
