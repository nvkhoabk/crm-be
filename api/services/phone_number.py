import json
from datetime import datetime

import xlrd
from django.db.models import Q

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.data import ImportOrderRecords
from api.models.organization import UserRole
from api.models.phone_number import MainPhoneNumber, Provider, Legal, PhoneNumberClient, PhoneNumberStatus, \
    PhoneNumberMonthlyFee, PhoneNumber, PhoneNumberActivity, PhoneNumberLockHistory
from api.models.product import Product
from api.models.package import Package
from api.models.param import Param
from api.serializers.phone_number_serializer import CreatePhoneNumberRequestSerializer
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (ProductNotFound, ProductDuplicated, MainPhoneNumberDuplicated,
                                     MainPhoneNumberNotFound, ProviderNotFound, ProviderDuplicated, LegalNotFound,
                                     LegalDuplicated, PhoneNumberClientNotFound, PhoneNumberClientDuplicated,
                                     PhoneNumberStatusNotFound, PhoneNumberStatusDuplicated,
                                     PhoneNumberMonthlyFeeNotFound, PhoneNumberMonthlyFeeDuplicated,
                                     PhoneNumberNotFound, PhoneNumberDuplicated, ImportRecordNotFound, )
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError, transaction
from groups_manager.models import Group, GroupType, Member
import api.services.validate_error_code as vec
import re


class CreateMainPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return MainPhoneNumber.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise MainPhoneNumberDuplicated()


class GetMainPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return MainPhoneNumber.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except MainPhoneNumber.DoesNotExist as e:
            raise MainPhoneNumberNotFound()


class UpdateMainPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                main_phone_number = MainPhoneNumber.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                main_phone_number = MainPhoneNumber.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                main_phone_number.name = kwargs['name']

            if kwargs.get('color'):
                main_phone_number.color = kwargs['color']

            if kwargs.get('index'):
                main_phone_number.index = kwargs['index']

            if kwargs.get('choose_by_default', None) != None:
                main_phone_number.choose_by_default = kwargs['choose_by_default']

            main_phone_number.save()

            return main_phone_number
        except MainPhoneNumber.DoesNotExist:
            raise MainPhoneNumberNotFound()


class FilterMainPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = MainPhoneNumber.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

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


class DeleteMainPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            main_phone_number = MainPhoneNumber.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            main_phone_number.deleted_at = datetime.now()
            main_phone_number.save()
            return main_phone_number

        except MainPhoneNumber.DoesNotExist as e:
            raise MainPhoneNumberNotFound()


class CreateProviderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return Provider.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise ProviderDuplicated()


class GetProviderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return Provider.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except Provider.DoesNotExist as e:
            raise ProviderNotFound()


class UpdateProviderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                provider = Provider.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                provider = Provider.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                provider.name = kwargs['name']

            if kwargs.get('color'):
                provider.color = kwargs['color']

            if kwargs.get('index'):
                provider.index = kwargs['index']

            if kwargs.get('choose_by_default', None) != None:
                provider.choose_by_default = kwargs['choose_by_default']

            provider.save()

            return provider
        except Provider.DoesNotExist:
            raise ProviderNotFound()


class FilterProviderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = Provider.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

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


class DeleteProviderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            provider = Provider.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            provider.deleted_at = datetime.now()
            provider.save()
            return provider

        except Provider.DoesNotExist as e:
            raise ProviderNotFound()


class CreateLegalService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return Legal.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise LegalDuplicated()


class GetLegalService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return Legal.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except Legal.DoesNotExist as e:
            raise LegalNotFound()


class UpdateLegalService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                legal = Legal.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                legal = Legal.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                legal.name = kwargs['name']

            if kwargs.get('color'):
                legal.color = kwargs['color']

            if kwargs.get('index'):
                legal.index = kwargs['index']

            if kwargs.get('choose_by_default', None) != None:
                legal.choose_by_default = kwargs['choose_by_default']

            legal.save()

            return legal
        except Legal.DoesNotExist:
            raise LegalNotFound()


class FilterLegalService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = Legal.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

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


class DeleteLegalService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            legal = Legal.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            legal.deleted_at = datetime.now()
            legal.save()
            return legal

        except Legal.DoesNotExist as e:
            raise LegalNotFound()


class CreatePhoneNumberClientService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return PhoneNumberClient.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise PhoneNumberClientDuplicated()


class GetPhoneNumberClientService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return PhoneNumberClient.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except PhoneNumberClient.DoesNotExist as e:
            raise PhoneNumberClientNotFound()


class UpdatePhoneNumberClientService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                phone_number_client = PhoneNumberClient.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                phone_number_client = PhoneNumberClient.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                phone_number_client.name = kwargs['name']

            if kwargs.get('color'):
                phone_number_client.color = kwargs['color']

            if kwargs.get('index'):
                phone_number_client.index = kwargs['index']

            if kwargs.get('choose_by_default', None) != None:
                phone_number_client.choose_by_default = kwargs['choose_by_default']

            phone_number_client.save()

            return phone_number_client
        except PhoneNumberClient.DoesNotExist:
            raise PhoneNumberClientNotFound()


class FilterPhoneNumberClientService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumberClient.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

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


class DeletePhoneNumberClientService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            phone_number_client = PhoneNumberClient.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            phone_number_client.deleted_at = datetime.now()
            phone_number_client.save()
            return phone_number_client

        except PhoneNumberClient.DoesNotExist as e:
            raise PhoneNumberClientNotFound()


class CreatePhoneNumberStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return PhoneNumberStatus.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise PhoneNumberStatusDuplicated()


class GetPhoneNumberStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return PhoneNumberStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except PhoneNumberStatus.DoesNotExist as e:
            raise PhoneNumberStatusNotFound()


class UpdatePhoneNumberStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                phone_number_status = PhoneNumberStatus.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                phone_number_status = PhoneNumberStatus.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                phone_number_status.name = kwargs['name']

            if kwargs.get('color'):
                phone_number_status.color = kwargs['color']

            if kwargs.get('index'):
                phone_number_status.index = kwargs['index']

            if kwargs.get('choose_by_default', None) != None:
                phone_number_status.choose_by_default = kwargs['choose_by_default']

            phone_number_status.save()

            return phone_number_status
        except PhoneNumberStatus.DoesNotExist:
            raise PhoneNumberStatusNotFound()


class FilterPhoneNumberStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumberStatus.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

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


class DeletePhoneNumberStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            phone_number_status = PhoneNumberStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            phone_number_status.deleted_at = datetime.now()
            phone_number_status.save()
            return phone_number_status

        except PhoneNumberStatus.DoesNotExist as e:
            raise PhoneNumberStatusNotFound()


class CreatePhoneNumberMonthlyFeeService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return PhoneNumberMonthlyFee.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise PhoneNumberMonthlyFeeDuplicated()


class GetPhoneNumberMonthlyFeeService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return PhoneNumberMonthlyFee.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except PhoneNumberMonthlyFee.DoesNotExist as e:
            raise PhoneNumberMonthlyFeeNotFound()


class UpdatePhoneNumberMonthlyFeeService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                phone_number_montly_fee = PhoneNumberMonthlyFee.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                phone_number_montly_fee = PhoneNumberMonthlyFee.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('on_net_fee'):
                phone_number_montly_fee.on_net_fee = kwargs['on_net_fee']

            if kwargs.get('off_net_fee'):
                phone_number_montly_fee.off_net_fee = kwargs['off_net_fee']

            if kwargs.get('billing_month'):
                phone_number_montly_fee.billing_month = kwargs['billing_month']

            if kwargs.get('payment_date'):
                phone_number_montly_fee.billing_month = kwargs['payment_date']

            phone_number_montly_fee.save()

            return phone_number_montly_fee
        except PhoneNumberMonthlyFee.DoesNotExist:
            raise PhoneNumberMonthlyFeeNotFound()


class FilterPhoneNumberMonthlyFeeService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumberMonthlyFee.objects.filter(company_id=user_roles.first().company_id,
                                                         deleted_at__isnull=True)

        filters = ['phone_number_id']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'phone_number_id':
                query_set = query_set.filter(
                    phone_number_id=value,
                )

        return query_set


class DeletePhoneNumberMonthlyFeeService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            phone_number_montly_fee = PhoneNumberMonthlyFee.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            phone_number_montly_fee.deleted_at = datetime.now()
            phone_number_montly_fee.save()
            return phone_number_montly_fee

        except PhoneNumberMonthlyFee.DoesNotExist as e:
            raise PhoneNumberMonthlyFeeNotFound()


class CreatePhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return PhoneNumber.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise PhoneNumberDuplicated()


class GetPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return PhoneNumber.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id,
                deleted_at__isnull=True
            )
        except PhoneNumber.DoesNotExist as e:
            raise PhoneNumberNotFound()


class UpdatePhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                phone_number = PhoneNumber.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                phone_number = PhoneNumber.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('main_phone_number_id'):
                phone_number.main_phone_number_id = kwargs['main_phone_number_id']

            if kwargs.get('provider_id'):
                phone_number.provider_id = kwargs['provider_id']

            if kwargs.get('legal_id'):
                phone_number.legal_id = kwargs['legal_id']

            if kwargs.get('phone_number_client_id'):
                phone_number.phone_number_client_id = kwargs['phone_number_client_id']

            if kwargs.get('phone_number_status_id'):
                phone_number.phone_number_status_id = kwargs['phone_number_status_id']

            if kwargs.get('pickup_date'):
                phone_number.pickup_date = kwargs['pickup_date']

            if kwargs.get('brand'):
                phone_number.brand = kwargs['brand']

            if kwargs.get('lock_provider'):
                phone_number.lock_provider = kwargs['lock_provider']

            if kwargs.get('lock_count'):
                phone_number.lock_count = kwargs['lock_count']

            if kwargs.get('phone_number_avg_age'):
                phone_number.phone_number_avg_age = kwargs['phone_number_avg_age']

            if kwargs.get('cancel_date'):
                phone_number.cancel_date = kwargs['cancel_date']

            if kwargs.get('init_fee'):
                phone_number.init_fee = kwargs['init_fee']

            if kwargs.get('operate_fee'):
                phone_number.operate_fee = kwargs['operate_fee']

            if kwargs.get('open_fee'):
                phone_number.open_fee = kwargs['open_fee']

            if kwargs.get('other_fee'):
                phone_number.other_fee = kwargs['other_fee']

            if kwargs.get('init_payment_date'):
                phone_number.init_payment_date = kwargs['init_payment_date']

            if kwargs.get('open_payment_date'):
                phone_number.open_payment_date = kwargs['open_payment_date']

            if kwargs.get('operate_payment_date'):
                phone_number.operate_payment_date = kwargs['operate_payment_date']

            if kwargs.get('other_payment_date'):
                phone_number.other_payment_date = kwargs['other_payment_date']

            if kwargs.get('note', None) is not None:
                phone_number.note = kwargs['note']

            if phone_number.has_changed:
                PhoneNumberActivity.objects.create(phone_number=phone_number, company=phone_number.company,
                                                   user_id=request.user.id, diff=phone_number.diff)

            phone_number.save()

            return phone_number
        except PhoneNumber.DoesNotExist:
            raise PhoneNumberNotFound()


class FilterPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumber.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

        params = dict(kwargs.get('filter', []))

        if 'pickup_date_from' in params and 'pickup_date_to' in params and params['pickup_date_from'] and params[
            'pickup_date_to']:
            query_set = query_set.filter(pickup_date__gte=params['pickup_date_from'],
                                         pickup_date__lte=params['pickup_date_to'])

        if 'lock_date_from' in params and 'lock_date_to' in params and params['lock_date_from'] and params[
            'lock_date_to']:
            lock_id_list = PhoneNumberLockHistory.objects.filter(company_id=user_roles.first().company_id,
                                                                 deleted_at__isnull=True,
                                                                 confirm_lock_date__gte=params['lock_date_from'],
                                                                 confirm_lock_date__lte=params[
                                                                     'lock_date_to']).values_list(
                'phone_number_id', flat=True)
            query_set = query_set.filter(id__in=lock_id_list)

        if 'cancel_date_from' in params and 'cancel_date_to' in params and params['cancel_date_from'] and params[
            'cancel_date_to']:
            query_set = query_set.filter(cancel_date__gte=params['cancel_date_from'],
                                         cancel_date__lte=params['cancel_date_to'])

        if 'payment_date_from' in params and 'payment_date_to' in params and params['payment_date_from'] and params[
            'payment_date_to']:
            query_set = query_set.filter(
                Q(init_payment_date__gte=params['payment_date_from'], init_payment_date__lte=params[
                    'payment_date_to']) |
                Q(open_payment_date__gte=params['payment_date_from'], open_payment_date__lte=params[
                    'payment_date_to']) |
                Q(operate_payment_date__gte=params['payment_date_from'], operate_payment_date__lte=params[
                    'payment_date_to']) |
                Q(other_payment_date__gte=params['payment_date_from'], other_payment_date__lte=params[
                    'payment_date_to']))

            monthly_fee_id_list = PhoneNumberMonthlyFee.objects.filter(company_id=user_roles.first().company_id,
                                                                       deleted_at__isnull=True,
                                                                       payment_date__gte=params['payment_date_from'],
                                                                       payment_date__lte=params[
                                                                           'payment_date_to']).values_list(
                'phone_number_id', flat=True)
            query_set = query_set.filter(id__in=monthly_fee_id_list)

        filters = ['phone_number', 'main_phone_number_id_list', 'provider_id_list', 'legal_id_list',
                   'phone_number_client_list', 'phone_number_status_id_list', 'phone_number_avg_age', 'lock_count']
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'phone_number':
                query_set = query_set.filter(
                    phone_number__icontains=value,
                )

            if key == 'main_phone_number_id_list' and value is not None and value:
                if None in value:
                    query_set = query_set.filter(
                        Q(main_phone_number_id__isnull=True) | Q(main_phone_number_id__in=value))
                else:
                    query_set = query_set.filter(main_phone_number_id__in=value)

            if key == 'provider_id_list' and value is not None and value:
                query_set = query_set.filter(provider_id__in=value)

            if key == 'legal_id_list' and value is not None and value:
                query_set = query_set.filter(legal_id__in=value)

            if key == 'phone_number_client_list' and value is not None and value:
                query_set = query_set.filter(phone_number_client_id__in=value)

            if key == 'phone_number_status_id_list' and value is not None and value:
                query_set = query_set.filter(phone_number_status_id__in=value)

            if key == 'lock_count' and value:
                if value <= 5:
                    query_set = query_set.filter(
                        lock_count=value,
                    )
                else:
                    query_set = query_set.filter(
                        lock_count__gt=5,
                    )

        return query_set


class DeletePhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            phone_number = PhoneNumber.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            phone_number.deleted_at = datetime.now()
            phone_number.save()
            return phone_number

        except PhoneNumber.DoesNotExist as e:
            raise PhoneNumberNotFound()


class FilterPhoneNumberActivityService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumberActivity.objects.filter(company_id=user_roles.first().company_id,
                                                       deleted_at__isnull=True)

        filters = ['phone_number_id']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'phone_number_id':
                query_set = query_set.filter(
                    phone_number_id=value,
                ).order_by('-id')

        return query_set


class ImportPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        record = ImportOrderRecords.objects.create(
            **kwargs
        )

        with record.file.open('r') as excel_file:
            workbook = xlrd.open_workbook(excel_file.path, encoding_override='utf-8')
            worksheet = workbook.sheet_by_index(0)
            num_rows = worksheet.nrows - 1
            curr_row = 0
            rows = []
            while curr_row < num_rows:
                curr_row += 1
                row = worksheet.row(curr_row)
                data_record = self.rowParser(row)
                error_codes = self.validate_data(data_record, kwargs['company_id'])
                if error_codes:
                    data_record['error_codes'] = error_codes
                    data_record['row_number'] = curr_row
                    rows.append(data_record)

        return {
            'id': record.id,
            'rows': rows
        }

    def rowParser(self, rows):
        return {
            'id': '' if str(rows[0].value).strip() == '' else str(int(rows[0].value)),
            'phone_number': str(rows[1].value).strip(),
            'main_phone_number': str(rows[2].value).strip(),
            'provider': str(rows[3].value).strip(),
            'legal': str(rows[4].value).strip(),
            'phone_number_client': str(rows[5].value).strip(),
            'phone_number_status': str(rows[6].value).strip(),
            'pickup_date': str(rows[7].value).strip(),
            'cancel_date': str(rows[8].value).strip(),
            'init_fee': str(rows[8].value).strip(),
            'operate_fee': str(rows[8].value).strip(),
            'open_fee': str(rows[8].value).strip(),
            'other_fee': str(rows[8].value).strip(),
            'init_payment_date': str(rows[8].value).strip(),
            'open_payment_date': str(rows[8].value).strip(),
            'operate_payment_date': str(rows[8].value).strip(),
            'other_payment_date': str(rows[8].value).strip(),
            'note': str(rows[8].value).strip()
        }

    def validate_data(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_id(data))
        error_codes.extend(self.validate_phone_format(data))
        error_codes.extend(self.validate_existed_phone(data, company_id))
        error_codes.extend(self.validate_main_phone_number(data, company_id))
        error_codes.extend(self.validate_provider(data, company_id))
        error_codes.extend(self.validate_legal(data, company_id))
        error_codes.extend(self.validate_phone_number_client(data, company_id))
        error_codes.extend(self.validate_phone_number_status(data, company_id))
        error_codes.extend(self.validate_date(data))
        error_codes.extend(self.validate_fee(data))
        return error_codes

    def validate_id(self, row):
        error_codes = []
        id_str = str(row['id']).strip()
        if id_str == '':
            error_codes.append(vec.IdIsEmpty.code)

        if not id_str.isnumeric():
            error_codes.append(vec.IdIsNotNumeric.code)

        return error_codes

    def validate_phone_format(self, row):
        phone = str(row['phone']).strip()
        if phone == '':
            return [vec.InvalidPhoneFormat.code]

        phone.replace(' ', '')
        phone.replace('.', '')
        phone.replace('+', '')
        path = r'([\+84|84|0]+(3|5|7|8|9|1[2|6|8|9]))+([0-9]{8})\b'

        if re.match(path, phone):
            return []

        return [vec.InvalidPhoneFormat.code]

    def validate_existed_phone(self, row, company_id):
        phone = str(row['phone_number']).strip()

        entity = PhoneNumber.objects.filter(phone_number=phone, company_id=company_id, deleted_at__isnull=True).first()
        if entity is None:
            return [vec.PhoneNumberDuplicated.code]

        return []

    def validate_main_phone_number(self, row, company_id):
        error_codes = []
        main_phone_number = str(row['main_phone_number']).strip()
        entity = MainPhoneNumber.objects.filter(name__iexact=main_phone_number,
                                                company_id=company_id).first()

        if entity is None:
            error_codes.append(vec.MainPhoneNumberNotFound.code)

        return error_codes

    def validate_provider(self, row, company_id):
        provider = str(row['provider']).strip()
        entity = Provider.objects.filter(name__iexact=provider,
                                         company_id=company_id).first()

        if entity is None:
            return [vec.ProviderNotFound.code]

        return []

    def validate_legal(self, row, company_id):
        legal = str(row['legal']).strip()
        entity = Legal.objects.filter(name__iexact=legal,
                                      company_id=company_id).first()

        if entity is None:
            return [vec.LegalNotFound.code]

        return []

    def validate_phone_number_client(self, row, company_id):
        phone_number_client = str(row['phone_number_client']).strip()
        entity = PhoneNumberClient.objects.filter(name__iexact=phone_number_client,
                                      company_id=company_id).first()

        if entity is None:
            return [vec.PhoneNumberClientNotFound.code]

        return []

    def validate_phone_number_status(self, row, company_id):
        phone_number_status = str(row['phone_number_status']).strip()
        entity = PhoneNumberStatus.objects.filter(name__iexact=phone_number_status,
                                                  company_id=company_id).first()

        if entity is None:
            return [vec.PhoneNumberStatusNotFound.code]

        return []

    def validate_date_format_YYYYMMDD(self, date_text):
        try:
            if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
                raise ValueError
            return True
        except ValueError:
            return False

    def validate_date(self, row):
        error_codes = []
        pickup_date = str(row['pickup_date']).strip()
        cancel_date = str(row['cancel_date']).strip()
        init_payment_date = str(row['init_payment_date']).strip()
        operate_payment_date = str(row['operate_payment_date']).strip()

        if not self.validate_date_format_YYYYMMDD(pickup_date):
            error_codes.append(vec.PickupDateWrongFormat.code)
        if not self.validate_date_format_YYYYMMDD(cancel_date):
            error_codes.append(vec.CancelDateWrongFormat.code)
        if not self.validate_date_format_YYYYMMDD(init_payment_date):
            error_codes.append(vec.InitPaymentDateWrongFormat.code)
        if not self.validate_date_format_YYYYMMDD(operate_payment_date):
            error_codes.append(vec.OperatePaymentDateWrongFormat.code)

        open_payment_date = str(row['open_payment_date']).strip()
        if open_payment_date and self.validate_date_format_YYYYMMDD(open_payment_date) == False:
            error_codes.append(vec.OpenPaymentDateWrongFormat.code)

        other_payment_date = str(row['other_payment_date']).strip()
        if other_payment_date and self.validate_date_format_YYYYMMDD(other_payment_date) == False:
            error_codes.append(vec.OpenPaymentDateWrongFormat.code)

        return error_codes

    def validate_fee(self, row):
        error_codes = []
        init_fee = str(row['init_fee']).strip()
        operate_fee = str(row['operate_fee']).strip()
        if init_fee == '':
            error_codes.append(vec.InitFeeIsEmpty.code)

        if not init_fee.isnumeric():
            error_codes.append(vec.InitFeeIsNotNumeric.code)

        if int(init_fee) == 0:
            error_codes.append(vec.InitFeeIsZero.code)

        if operate_fee == '':
            error_codes.append(vec.OperateFeeIsEmpty.code)

        if not operate_fee.isnumeric():
            error_codes.append(vec.OperateFeeIsNotNumeric.code)

        if int(operate_fee) == 0:
            error_codes.append(vec.OperateFeeIsZero.code)

        return error_codes


class ConfirmImportPhoneNumberService(ImportPhoneNumberService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        try:
            record = ImportOrderRecords.objects.get(
                pk=kwargs.get('id')
            )

            create_phone_number_service = CreatePhoneNumberService()

            with record.file.open('r') as excel_file:
                workbook = xlrd.open_workbook(excel_file.path, encoding_override='utf-8')
                worksheet = workbook.sheet_by_index(0)
                num_rows = worksheet.nrows - 1
                curr_row = 0
                while curr_row < num_rows:
                    curr_row += 1
                    row = worksheet.row(curr_row)
                    data_record = self.rowParser(row)
                    error_codes = self.validate_data(data_record, kwargs['company_id'])
                    if not error_codes:
                        main_phone_number = MainPhoneNumber.objects.filter(name=data_record['main_phone_number'],
                                                                deleted_at__isnull=True,
                                                                company_id=kwargs['company_id']).first()
                        provider = Provider.objects.filter(name=data_record['provider'],
                                                                           deleted_at__isnull=True,
                                                                           company_id=kwargs['company_id']).first()
                        legal = Legal.objects.filter(name=data_record['legal'],
                                                                           deleted_at__isnull=True,
                                                                           company_id=kwargs['company_id']).first()
                        phone_number_client = PhoneNumberClient.objects.filter(name=data_record['phone_number_client'],
                                                                           deleted_at__isnull=True,
                                                                           company_id=kwargs['company_id']).first()
                        phone_number_status = PhoneNumberStatus.objects.filter(name=data_record['phone_number_status'],
                                                                           deleted_at__isnull=True,
                                                                           company_id=kwargs['company_id']).first()
                        phone_number = PhoneNumber(
                            phone_number=data_record['phone_number'],
                            main_phone_number=phone_number,
                            provider=provider,
                            legal=legal,
                            phone_number_client=phone_number_client,
                            phone_number_status=phone_number_status,
                            pickup_date=data_record['pickup_date'],
                            brand=data_record['brand'],
                            lock_provider=data_record['lock_provider'],
                            cancel_date=data_record['cancel_date'],
                            init_fee=data_record['init_fee'],
                            operate_fee=data_record['operate_fee'],
                            open_fee=data_record['open_fee'],
                            other_fee=data_record['other_fee'],
                            init_payment_date=data_record['init_payment_date'],
                            open_payment_date=data_record['open_payment_date'],
                            operate_payment_date=data_record['operate_payment_date'],
                            other_payment_date=data_record['other_payment_date'],
                            note=data_record['note'],
                            company_id=kwargs['company_id'],
                            created_at=datetime.today().date())

                        create_phone_number_service.serve(request, cookies, *args,
                                                          **CreatePhoneNumberRequestSerializer(phone_number).data)

        except ImportOrderRecords.DoesNotExist:
            raise ImportRecordNotFound