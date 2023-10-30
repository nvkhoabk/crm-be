import json

import xlrd

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import MODULES, PARAM_KEY
from api.models.data import Customer, ImportOrderRecords
from api.models.organization import Company, Department, Permission, Role, UserRole
from api.models.package import Package
from api.models.param import Param
from api.models.system_configuration import DataStatus, DataSource, DataSubStatus
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (ManageCompanyNotFound,
                                     ManageCompanyDuplicated,
                                     ManageParamDuplicated,
                                     ManageParamNotFound,
                                     ManageDepartmentDuplicated,
                                     ManageDepartmentNotFound,
                                     ManageDepartmentNotEmpty,
                                     ManagePermissionDuplicated,
                                     ManagePermissionNotFound,
                                     ManageRoleDuplicated,
                                     ManageRoleNotFound,
                                     ManageUserDuplicated,
                                     ManageUserNotFound, ManagePackageDuplicated, ManagePackageNotFound,
                                     ManageCustomerNotFound, ManageCustomerDuplicated, )
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError, transaction
from groups_manager.models import Group, GroupType, Member


User = get_user_model()


class CreateParamService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Param.objects.create(
                key=kwargs['key'],
                value=kwargs['value'],
            )
        except IntegrityError as e:
            raise ManageParamDuplicated()


class GetParamService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Param.objects.get(
                pk=kwargs['id'],
            )
        except Param.DoesNotExist:
            raise ManageParamNotFound()


class UpdateParamService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            param = Param.objects.get(pk=kwargs['id'])
            param.value = kwargs['value']
            param.save()
            return param
        except Param.DoesNotExist:
            raise ManageParamNotFound()
        except IntegrityError as e:
            raise ManageParamDuplicated()


class FilterParamService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Param.objects.filter(deleted_at__isnull=True)
        filters = ['key', 'value', 'group']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'key':
                query_set = query_set.filter(
                    key__icontains=value,
                )
            if key == 'value':
                query_set = query_set.filter(
                    value__icontains=value,
                )
            if key == 'group':
                query_set = query_set.filter(
                    group__icontains=value,
                )
        return query_set


class CreatePackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Package.objects.create(
                company_id=kwargs['company_id'],
                viettel=kwargs['viettel'],
                vinaphone=kwargs['vinaphone'],
                mobifone=kwargs['mobifone'],
                other=kwargs['other']
            )
        except IntegrityError as e:
            raise ManagePackageDuplicated()


class GetPackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if kwargs.get('id') is not None:
                return Package.objects.get(
                    pk=kwargs['id'], deleted_at__isnull=True
                )
            else:
                try:
                    general_package = Param.objects.get(key=PARAM_KEY.GENERAL_PACKAGE)
                except Param.DoesNotExist:
                    data = '{"viettel": [{"endAt": 0, "unitPrice": 0}], "vinaphone": [{"endAt": 0, "unitPrice": 0}], "mobifone": [{"endAt": 0, "unitPrice": 0}], "other": [{"endAt": 0, "unitPrice": 0}]}'

                    general_package = Param.objects.create(key=PARAM_KEY.GENERAL_PACKAGE,
                                                           value=data,
                                                           group='GENERAL_PACKAGE',
                                                           description='GENERAL_PACKAGE')
                config_price = json.loads(general_package.value)
                package = Package(viettel=json.dumps(config_price['viettel']),
                                  vinaphone=json.dumps(config_price['vinaphone']),
                                  mobifone=json.dumps(config_price['mobifone']),
                                  other=json.dumps(config_price['other']))
                return package
        except Package as e:
            raise ManagePackageNotFound()


class UpdatePackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if kwargs.get('id') is not None:
                package = Package.objects.get(
                    pk=kwargs.get('id'),
                )

                package.company_id = kwargs['company_id']
                package.viettel = kwargs['viettel']
                package.vinaphone = kwargs['vinaphone']
                package.mobifone = kwargs['mobifone']
                package.other = kwargs['other']
                package.save()

                return package
            else:
                try:
                    general_package = Param.objects.get(key=PARAM_KEY.GENERAL_PACKAGE)
                except Param.DoesNotExist:
                    data = '{"viettel": [{"endAt": 0, "unitPrice": 0}], "vinaphone": [{"endAt": 0, "unitPrice": 0}], "mobifone": [{"endAt": 0, "unitPrice": 0}], "other": [{"endAt": 0, "unitPrice": 0}]}'

                    general_package = Param.objects.create(key=PARAM_KEY.GENERAL_PACKAGE,
                                                           value=data,
                                                           group='GENERAL_PACKAGE',
                                                           description='GENERAL_PACKAGE')
                config_price = json.loads(general_package.value)
                config_price['viettel'] = json.loads(kwargs['viettel'])
                config_price['vinaphone'] = json.loads(kwargs['vinaphone'])
                config_price['mobifone'] = json.loads(kwargs['mobifone'])
                config_price['other'] = json.loads(kwargs['other'])

                general_package.value = json.dumps(config_price)
                general_package.save()

        except Package.DoesNotExist:
            raise ManagePackageNotFound()
        except IntegrityError as e:
            raise ManagePackageDuplicated()


class FilterPackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Package.objects.all()

        filters = ['company_name', ]
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if value is None:
                continue
            if key not in filters:
                continue

            if key == 'company_name':
                query_set = query_set.filter(
                    company__name__icontains=value,
                    deleted_at__isnull=True
                )

        return query_set


class DeletePackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Package.objects.get(
                pk=kwargs['id'],
            ).delete()
        except Package.DoesNotExist as e:
            raise ManagePackageNotFound()


class CreateCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        with transaction.atomic():
            try:
                company = Company.objects.create(
                    **kwargs
                )

                DataStatus.objects.create(
                    company_id=company.id,
                    name='Đã xác nhận',
                    color='#CC6633',
                    index=0,
                    choose_by_default=False
                )
                data_status = DataStatus.objects.create(
                    company_id=company.id,
                    name='Chưa xác nhận',
                    color='#a3ce71',
                    index=1,
                    choose_by_default=True
                )
                DataSubStatus.objects.create(
                    company_id=company.id,
                    data_status_id=data_status.id,
                    name='Chưa xử lý',
                    color='#f59da9',
                    index=0,
                    choose_by_default=True
                )
                DataStatus.objects.create(
                    company_id=company.id,
                    name='Đã hủy',
                    color='#7a7980',
                    index=3,
                    choose_by_default=False
                )
                DataSource.objects.create(
                    company_id=company.id,
                    name='Facebook',
                    index=0,
                    choose_by_default=False
                )
                DataSource.objects.create(
                    company_id=company.id,
                    name='Zalo',
                    index=1,
                    choose_by_default=False
                )
                DataSource.objects.create(
                    company_id=company.id,
                    name='Web',
                    index=3,
                    choose_by_default=True
                )
                # Create group permission
                company_group = Group.objects.create(
                    name=utils.get_company_group_name(company.id))
                company_admins = Group.objects.create(name=utils.get_company_admins_group(company.id),
                                                      parent=company_group)
                company_admins.assign_object(company)
                return company
            except IntegrityError as e:
                raise ManageCompanyDuplicated()


class GetCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Company.objects.get(
                pk=kwargs['id']
            )
        except Company.DoesNotExists:
            raise ManageCompanyNotFound()


class UpdateCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['id'])
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()

        try:
            Company.objects.filter(pk=kwargs['id']).update(**kwargs)
        except IntegrityError as e:
            raise ManageCreateCompanyDuplicated()

        return Company.objects.get(pk=kwargs['id'])


class DeleteCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        id = kwargs['id']
        with transaction.atomic():
            try:
                return Company.objects.get(
                    id=id,
                ).delete()
            except Company.DoesNotExist as e:
                raise ManageCompanyNotFound()


class FilterCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Company.objects.all()

        filters = ['name', 'type', 'owner', 'phone']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name':
                query_set = query_set.filter(
                    name__icontains=value,
                )
            if key == 'type':
                query_set = query_set.filter(
                    type__icontains=value,
                )
            if key == 'owner':
                query_set = query_set.filter(
                    owner__icontains=value,
                )
            if key == 'phone':
                query_set = query_set.filter(
                    phone__icontains=value,
                )

        return query_set


class CreateDepartmentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        company_id = kwargs['company_id']
        department_name = kwargs['department_name']

        utils.has_company_permisison(request.user, company_id=company_id)

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()

        if Department.objects.filter(
            company__id=company_id,
            department_name=department_name,
        ).first():
            raise ManageDepartmentDuplicated()

        return Department.objects.create(
            company=company,
            department_name=department_name,
        )


class GetDepartmentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, department_id=kwargs['id'])
        try:
            return Department.objects.get(pk=kwargs['id'])
        except Department.DoesNotExist:
            raise ManageDepartmentNotFound()


class UpdateDepartmentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, department_id=kwargs['id'])
        try:
            department = Department.objects.get(pk=kwargs['id'])
            department.department_name = kwargs['department_name']
            department.save()
            return department
        except Department.DoesNotExist:
            raise ManageDepartmentNotFound()


class FilterDepartmentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Department.objects.all()

        filters = ['company_id', 'department_id', 'department_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id':
                utils.has_company_permisison(request.user, company_id=value)
                query_set = query_set.filter(
                    company__id=value,
                )
            if key == 'department_id':
                query_set = query_set.filter(
                    pk=value,
                )
            if key == 'department_name':
                query_set = query_set.filter(
                    department_name__icontains=value,
                )

        return query_set


class DeleteDepartmentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, department_id=kwargs['id'])
        try:
            if UserRole.objects.filter(department_id=kwargs['id'], user__is_active=True):
                raise ManageDepartmentNotEmpty()

            return Department.objects.get(
                id=kwargs['id'],
            ).delete()
        except Department.DoesNotExist as e:
            raise ManageDepartmentNotFound()


class CreateRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        company_id = kwargs['company_id']
        department_id = kwargs['department_id']
        role_name = kwargs['role_name']

        utils.has_company_permisison(request.user, company_id=company_id)

        if Role.objects.filter(
            company__id=company_id,
            department__id=department_id,
            role_name=role_name,
        ).first():
            raise ManageRoleDuplicated()

        try:
            department = Department.objects.get(pk=department_id)
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise ManageDepartmentNotFound()

        return Role.objects.create(
            company=company,
            department=department,
            role_name=role_name,
        )


class GetRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, role_id=kwargs['id'])

        try:
            return Role.objects.get(pk=kwargs['id'])
        except Role.DoesNotExist:
            raise ManageRoleNotFound()


class UpdateRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, role_id=kwargs['id'])
        try:
            role = Role.objects.get(pk=kwargs['id'])
            role.role_name = kwargs['role_name']
            role.save()
            return role
        except Role.DoesNotExist:
            raise ManageRoleNotFound()


class FilterRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Role.objects.all()

        filters = ['company_id', 'department_id', 'role_id', 'role_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id':
                utils.has_company_permisison(request.user, company_id=value)
                query_set = query_set.filter(
                    company__id=value,
                )

            if key == 'department_id' and value is not None:
                query_set = query_set.filter(
                    department__id=value,
                )
            if key == 'role_id' and value is not None:
                query_set = query_set.filter(
                    pk=value,
                )
            if key == 'role_name':
                query_set = query_set.filter(
                    role_name__icontains=value,
                )

        return query_set


class DeleteRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, role_id=kwargs['id'])
        try:
            return Role.objects.get(
                id=kwargs['id'],
            ).delete()
        except Role.DoesNotExist as e:
            raise ManageRoleNotFound()


class CreatePermissionService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, company_id=kwargs['company_id'])
        try:
            company = Company.objects.get(pk=kwargs['company_id'])
            department = Department.objects.get(pk=kwargs['department_id'])
            role = Role.objects.get(pk=kwargs['role_id'])
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()
        except Department.DoesNotExist:
            raise ManageDepartmentNotFound()
        except Role.DoesNotExist:
            raise ManageRoleNotFound()

        try:
            return Permission.objects.create(
                company=company,
                department=department,
                role=role,
                edit_permissions=json.dumps(kwargs['edit_permissions']),
                read_permissions=json.dumps(kwargs['read_permissions']),
            )
        except IntegrityError as e:
            raise ManagePermissionDuplicated()


class GetPermissionService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, permission_id=kwargs['id'])
        try:
            return Permission.objects.get(pk=kwargs['id'])
        except Permission.DoesNotExist:
            raise ManagePermissionNotFound()


class UpdatePermissionService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, permission_id=kwargs['id'])
        try:
            permission = Permission.objects.get(pk=kwargs['id'])
            permission.edit_permissions = json.dumps(
                kwargs['edit_permissions'])
            permission.read_permissions = json.dumps(
                kwargs['read_permissions'])
            permission.save()
        except Permission.DoesNotExist:
            raise ManagePermissionNotFound()


class FilterPermissionService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Permission.objects.all()

        filters = ['company_id', 'department_id', 'role_id', 'permission_id']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id':
                utils.has_company_permisison(request.user, company_id=value)
                query_set = query_set.filter(
                    company__id=value,
                )
            if key == 'department_id' and value is not None:
                query_set = query_set.filter(
                    department__id=value,
                )
            if key == 'role_id' and value is not None:
                query_set = query_set.filter(
                    role__id=value,
                )
            if key == 'permission_id':
                query_set = query_set.filter(
                    pk=value,
                )

        return query_set


class DeletePermissionService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        utils.has_company_permisison(request.user, permission_id=kwargs['id'])
        try:
            return Permission.objects.get(
                id=kwargs['id'],
            ).delete()
        except Permission.DoesNotExist as e:
            raise ManagePermissionNotFound()


class CreateUserService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            company = Company.objects.get(pk=kwargs['company_id'])
            group_admins = Group.objects.get(name=utils.get_company_admins_group(kwargs['company_id']))
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()

        if not request.user.is_superuser and kwargs.get('roles'):
            # Check if user has company permission
            try:
                member = Member.objects.get(django_user=request.user)
            except Member.DoesNotExist:
                raise PermissionDenied()
            if not member.has_perm('change_company', company):
                raise PermissionDenied()
        elif not request.user.is_superuser:
            raise PermissionDenied()

        with transaction.atomic():
            if User.objects.filter(username=kwargs['username']).first():
                raise ManageUserDuplicated()

            user = User.objects.create_user(
                username=kwargs['username'],
                password=kwargs['password'],
            )
            if not kwargs.get('department_id') and not kwargs.get('role_id'):
                # Add admin user to group admin
                member = Member.objects.create(username=user.username, django_user=user)
                group_admins.add_member(member)

            for roles in kwargs.get('roles', []):
                try:
                    if roles.get('department_id'):
                        department = Department.objects.get(
                            pk=roles['department_id'])
                    if roles.get('role_id'):
                        role = Role.objects.get(pk=roles['role_id'])
                except Department.DoesNotExist:
                    raise ManageDepartmentNotFound()
                except Role.DoesNotExist:
                    raise ManageRoleNotFound()

                # Role
                UserRole.objects.create(
                    company=company,
                    department=department if roles.get('department_id') else None,
                    role=role if roles.get('role_id') else None,
                    user=user,
                )

            if len(kwargs.get('roles', [])) == 0:
                UserRole.objects.create(
                    company=company,
                    user=user,
                )

            return user


class GetUserService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            user = User.objects.get(pk=kwargs['id'])
        except User.DoesNotExists:
            raise ManageUserNotFound()

        utils.has_company_permisison(request.user, target_user=user)
        response = {
            'is_superuser': user.is_superuser,
            'username': user.username,
            'status': user.is_active
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


class FilterUserService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user_role_query = UserRole.objects.all()
        query_set = User.objects.all()

        filters = ['company_id', 'department_id', 'role_id', 'username']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id':
                utils.has_company_permisison(request.user, company_id=value)
                user_role_query = user_role_query.filter(
                    company__id=value,
                )
            if key == 'department_id':
                user_role_query = user_role_query.filter(
                    department__id=value,
                )
            if key == 'role_id':
                user_role_query = user_role_query.filter(
                    role__id=value,
                )
            if key == 'username':
                user_role_query = user_role_query.filter(
                    user__username__icontains=value,
                )

        query_set = query_set.filter(
            id__in=user_role_query.values_list('user__id', flat=True),
        )

        return query_set


class FilterSaleUserService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        permissions = Permission.objects.filter(
            edit_permissions__icontains=MODULES.DATA_MANAGEMENT_FOR_SALE) | Permission.objects.filter(
            read_permissions__icontains=MODULES.DATA_MANAGEMENT_FOR_SALE)
        roles = Role.objects.filter(id__in=permissions.values_list('role__id', flat=True))
        user_roles = UserRole.objects.filter(**filter)
        user_roles = UserRole.objects.filter(company_id=user_roles.first().company_id,
                                             role_id__in=roles.values_list('id', flat=True))

        users = User.objects.filter(id__in=user_roles.values_list('user__id', flat=True))
        return users


class UpdateUserService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        with transaction.atomic():
            try:
                user = User.objects.get(pk=kwargs['id'])
            except User.DoesNotExist:
                raise ManageUserNotFound()

            utils.has_company_permisison(request.user, target_user=user)

            if kwargs.get('username'):
                user.username = kwargs['username']

            if kwargs.get('password'):
                user.set_password(kwargs['password'])

            if kwargs.get('status') is not None:
                user.is_active = kwargs['status']

            if kwargs.get('roles', []):
                UserRole.objects.filter(
                    user=user,
                ).delete()

            try:
                company = Company.objects.get(pk=kwargs['company_id'])
            except Company.DoesNotExist:
                raise ManageCompanyNotFound()

            for roles in kwargs.get('roles', []):
                try:
                    if roles.get('department_id'):
                        department = Department.objects.get(
                            pk=roles['department_id'])
                    if roles.get('role_id'):
                        role = Role.objects.get(pk=roles['role_id'])
                except Department.DoesNotExist:
                    raise ManageDepartmentNotFound()
                except Role.DoesNotExist:
                    raise ManageRoleNotFound()

                # Role
                UserRole.objects.create(
                    company=company,
                    department=department if roles.get('department_id') else None,
                    role=role if roles.get('role_id') else None,
                    user=user,
                )

            user.save()
            return user


class DeleteUserService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs['id'])
            utils.has_company_permisison(request.user, target_user=user)
            user.delete()
        except User.DoesNotExist as e:
            raise ManageUserNotFound()


class CreateCustomerService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return Customer.objects.create(
                name=kwargs['name'],
                phone=kwargs['phone'],
                address=kwargs['address'],
                email=kwargs['email'],
                company_id=user_roles.first().company_id
            )
        except IntegrityError as e:
            raise ManageCustomerDuplicated()


class GetCustomerService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Customer.objects.get(
                pk=kwargs['id'],
            )
        except Customer.DoesNotExist:
            raise ManageCustomerNotFound()


class UpdateCustomerService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            customer = Customer.objects.get(pk=kwargs['id'])
            customer.name = kwargs['name']
            customer.phone = kwargs['phone']
            customer.address = kwargs['address']
            customer.save()
            return customer
        except Customer.DoesNotExist:
            raise ManageCustomerNotFound()
        except IntegrityError as e:
            raise ManageCustomerDuplicated()


class FilterCustomerService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }

        user_roles = UserRole.objects.filter(**filter)

        query_set = Customer.objects.filter(company_id=user_roles.first().company_id)
        filters = ['name', 'phone', 'address']
        customers = dict(kwargs.get('filter', []))
        for key, value in customers.items():
            if key not in filters:
                continue

            if key == 'name':
                query_set = query_set.filter(
                    name__icontains=value,
                )
            if key == 'phone':
                query_set = query_set.filter(
                    phone__icontains=value,
                )
            if key == 'address':
                query_set = query_set.filter(
                    address__icontains=value,
                )
        return query_set

