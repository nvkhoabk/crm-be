from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import Company, Department, Role
from api.models.param import Param
from api.models.package import Package
from api.services.exceptions import (ManageCreateCompanyDuplicated,
                                     ManageCreateParamDuplicated,
                                     ManageCompanyNotFound,
                                     ManageDepartmentNotFound,
                                     ManageRoleNotFound)
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError


class CreateOrUpdateParamService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Param.objects.get_or_create(
                key=kwargs['key'],
                defaults={
                    'value': kwargs['value'],
                }
            )
        except IntegrityError as e:
            raise ManageCreateParamDuplicated()


class FilterParamService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Param.objects.all()
        return query_set


class CreateOrUpdatePackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            package, _ = Package.objects.get_or_create(
                pk=kwargs.get('id'),
                defaults={
                    'name': kwargs['name'],
                    'price': kwargs['price'],
                }
            )
            return package
        except IntegrityError as e:
            raise ManageCreatePackageDuplicated()


class FilterPackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Package.objects.all()

        filters = ['name', ]
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name':
                query_set = query_set.filter(
                    name__icontains=value,
                )

        return query_set


class DeletePackageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Package.objects.get(
                pk=kwargs['id'],
            ).delete()
        except Package.DoesNotExist as e:
            raise ManageDeletePackageNotFound()


class CreateCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Company.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise ManageCreateCompanyDuplicated()


class UpdateCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['id'])
        except Company.DoesNotExist:
            raise ManageDeleteCompanyNotFound()

        try:
            Company.objects.filter(pk=kwargs['id']).update(**kwargs)
        except IntegrityError as e:
            raise ManageCreateCompanyDuplicated()

        return Company.objects.get(pk=kwargs['id'])


class DeleteCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        id = kwargs['id']

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

        if Department.objects.filter(
            company__id=company_id,
            department_name=department_name,
        ).first():
            raise ManageDepartmentNotFound()        

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()
        
        return Department.objects.create(
            company=company,
            department_name=department_name,
        )


class UpdateDepartmentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
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

        filters = ['company_id', 'id', 'department_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id':
                query_set = query_set.filter(
                    company__id=value,
                )
            if key == 'id':
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
        try:
            return Department.objects.get(
                id=kwargs['id'],
            ).delete()
        except Department.DoesNotExist as e:
            raise ManageDepartmentNotFound()
    

class CreateRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        department_id = kwargs['department_id']
        role_name = kwargs['role_name']

        if Role.objects.filter(
            department__id=department_id,
            role_name=role_name,
        ).first():
            raise ManageRoleNotFound()
        
        try:
            department = Department.objects.get(pk=department_id)
        except Company.DoesNotExist:
            raise ManageDepartmentNotFound()
        
        return Role.objects.create(
            department=department,
            role_name=role_name,
        )
    

class UpdateRoleService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
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

        filters = ['department_id', 'id', 'role_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'department_id':
                query_set = query_set.filter(
                    department__id=value,
                )
            if key == 'id':
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
        try:
            return Role.objects.get(
                id=kwargs['id'],
            ).delete()
        except Role.DoesNotExist as e:
            raise ManageRoleNotFound()
