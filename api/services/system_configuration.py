import json

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import UserRole
from api.models.product import Product
from api.models.system_configuration import CompanyEmail
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (ProductNotFound, CompanyEmailDuplicated, CompanyEmailNotFound, )
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


