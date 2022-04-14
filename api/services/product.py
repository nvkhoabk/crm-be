import json

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import UserRole
from api.models.product import Product
from api.models.package import Package
from api.models.param import Param
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (ProductNotFound, ProductDuplicated, )
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError, transaction
from groups_manager.models import Group, GroupType, Member


class CreateProductService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return Product.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise ProductDuplicated()


class GetProductService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return Product.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except Product.DoesNotExist as e:
            raise ProductNotFound()


class UpdateProductService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                product = Product.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                product = Product.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                product.name = kwargs['name']

            if kwargs.get('description'):
                product.description = kwargs['description']

            if kwargs.get('price'):
                product.price = kwargs['price']

            if kwargs.get('payment_method'):
                product.payment_method = kwargs['payment_method']

            if kwargs.get('period_fee'):
                product.period_fee = kwargs['period_fee']

            if kwargs.get('date_in_month_payment'):
                product.date_in_month_payment = kwargs['date_in_month_payment']

            if kwargs.get('number_of_date_notify'):
                product.number_of_date_notify = kwargs['number_of_date_notify']

            if kwargs.get('company_id'):
                product.company_id = kwargs['company_id']

            product.save()

            return product
        except Product.DoesNotExist:
            raise ProductNotFound()
    

class FilterProductService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = Product.objects.filter(company_id=user_roles.first().company_id)

        filters = ['name', 'payment_method']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name':
                query_set = query_set.filter(
                    name__icontains=value,
                )

            if key == 'payment_method' and value is not None:
                query_set = query_set.filter(payment_method=value)


        return query_set


class DeleteProductService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return Product.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except Product.DoesNotExist as e:
            raise ProductNotFound()
