import json

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import UserRole
from api.models.product import Product
from api.models.system_configuration import CompanyEmail, DataStatus
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (ProductNotFound, CompanyEmailDuplicated, CompanyEmailNotFound,
                                     DataStatusDuplicated, DataStatusNotFound, )
from django.db import IntegrityError


class CreateCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return CompanyEmail.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise CompanyEmailDuplicated()


class GetCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return CompanyEmail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except CompanyEmail.DoesNotExist as e:
            raise CompanyEmailNotFound()


class UpdateCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                email = CompanyEmail.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                email = CompanyEmail.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('email'):
                email.email = kwargs['email']

            if kwargs.get('password'):
                email.password = kwargs['password']

            email.save()

            return email
        except CompanyEmail.DoesNotExist:
            raise CompanyEmailNotFound()
    

class FilterCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = CompanyEmail.objects.filter(company_id=user_roles.first().company_id)

        filters = ['email']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'email':
                query_set = query_set.filter(
                    email__icontains=value,
                )

        return query_set


class DeleteCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return CompanyEmail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except CompanyEmail.DoesNotExist as e:
            raise CompanyEmailNotFound()


class CreateDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return DataStatus.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise DataStatusDuplicated()


class GetDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return DataStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except DataStatus.DoesNotExist as e:
            raise DataStatusNotFound()


class UpdateDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                result = DataStatus.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                result = DataStatus.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                result.name = kwargs['name']

            result.save()

            return result
        except DataStatus.DoesNotExist:
            raise DataStatusNotFound()


class FilterDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = DataStatus.objects.filter(company_id=user_roles.first().company_id)

        filters = ['name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name':
                query_set = query_set.filter(
                    name__icontains=value,
                )

        return query_set


class DeleteDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return DataStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except DataStatus.DoesNotExist as e:
            raise DataStatusNotFound()