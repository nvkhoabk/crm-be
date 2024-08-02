import json
from datetime import datetime, date as date_type
from pytz import timezone
import pandas as pd
import xlrd
from django.db.models import Q

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import IMPORT_TYPE, PHONE_NUMBER_PROVIDER
from api.models.data import ImportOrderRecords, ExportOrderRequest
from api.models.organization import UserRole, Company, Department, Role
from api.models.phone_number import MainPhoneNumber, Provider, Legal, PhoneNumberClient, PhoneNumberStatus, \
    PhoneNumberMonthlyFee, PhoneNumber, PhoneNumberActivity, PhoneNumberLockHistory, PhoneNumberTechnicalActivity
from api.models.product import Product
from api.models.package import Package
from api.models.param import Param
from api.serializers.phone_number_serializer import CreatePhoneNumberRequestSerializer, \
    CreatePhoneNumberMonthlyFeeRequestSerializer, CheckPhoneNumberRequestSerializer
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (ProductNotFound, ProductDuplicated, MainPhoneNumberDuplicated,
                                     MainPhoneNumberNotFound, ProviderNotFound, ProviderDuplicated, LegalNotFound,
                                     LegalDuplicated, PhoneNumberClientNotFound, PhoneNumberClientDuplicated,
                                     PhoneNumberStatusNotFound, PhoneNumberStatusDuplicated,
                                     PhoneNumberMonthlyFeeNotFound, PhoneNumberMonthlyFeeDuplicated,
                                     PhoneNumberNotFound, PhoneNumberDuplicated, ImportRecordNotFound,
                                     InvalidInpputDate, InvalidPhoneNumberStatus, )
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError, transaction
from groups_manager.models import Group, GroupType, Member
import api.services.validate_error_code as vec
import re
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from crm.settings import TIME_ZONE, MEDIA_ROOT


def is_locked_phone_number(history):
    if history is None:
        return False

    if history.unlock_lock_date is not None:
        return False

    return True


def update_lock_count(phone_number):
    lock_histories = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, phone_number=phone_number)
    phone_number.lock_count = lock_histories.count()
    phone_number.viettel_lock_count = lock_histories.filter(viettel_lock_date__isnull=False).count()
    phone_number.mobifone_lock_count = lock_histories.filter(mobifone_lock_date__isnull=False).count()
    phone_number.vinaphone_lock_count = lock_histories.filter(vinaphone_lock_date__isnull=False).count()
    phone_number.other_lock_count = lock_histories.filter(other_lock_date__isnull=False).count()

    phone_number.lock_history_id = lock_histories.order_by('-id').first().id if phone_number.lock_count else 0
    phone_number.viettel_lock_history_id = lock_histories.filter(viettel_lock_date__isnull=False).order_by(
        '-id').first().id if phone_number.viettel_lock_count else 0
    phone_number.mobifone_lock_history_id = lock_histories.filter(mobifone_lock_date__isnull=False).order_by(
        '-id').first().id if phone_number.mobifone_lock_count else 0
    phone_number.vinaphone_lock_history_id = lock_histories.filter(vinaphone_lock_date__isnull=False).order_by(
        '-id').first().id if phone_number.vinaphone_lock_count else 0
    phone_number.other_lock_history_id = lock_histories.filter(other_lock_date__isnull=False).order_by(
        '-id').first().id if phone_number.other_lock_count else 0


def update_lock_information(phone_number, viettel_lock_date, mobifone_lock_date, vinaphone_lock_date, other_lock_date):
    lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                         id=phone_number.viettel_lock_history_id).first()

    if viettel_lock_date:
        if is_locked_phone_number(lock_history):
            lock_history.viettel_lock_date = viettel_lock_date
            lock_history.save()
        else:
            PhoneNumberLockHistory.objects.create(company=phone_number.company,
                                                  phone_number=phone_number,
                                                  checking_lock_date=datetime.today(),
                                                  confirm_lock_date=datetime.today(),
                                                  viettel_lock_date=viettel_lock_date,
                                                  mobifone_lock_date=None,
                                                  vinaphone_lock_date=None,
                                                  other_lock_date=None)

    lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                         id=phone_number.mobifone_lock_history_id).first()
    if mobifone_lock_date:
        if is_locked_phone_number(lock_history):
            lock_history.mobifone_lock_date = mobifone_lock_date
            lock_history.save()
        else:
            PhoneNumberLockHistory.objects.create(company=phone_number.company,
                                                  phone_number=phone_number,
                                                  checking_lock_date=datetime.today(),
                                                  confirm_lock_date=datetime.today(),
                                                  viettel_lock_date=None,
                                                  mobifone_lock_date=mobifone_lock_date,
                                                  vinaphone_lock_date=None,
                                                  other_lock_date=None)

    lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                         id=phone_number.vinaphone_lock_history_id).first()

    if vinaphone_lock_date:
        if is_locked_phone_number(lock_history):
            lock_history.vinaphone_lock_date = vinaphone_lock_date
            lock_history.save()
        else:
            PhoneNumberLockHistory.objects.create(company=phone_number.company,
                                                  phone_number=phone_number,
                                                  checking_lock_date=datetime.today(),
                                                  confirm_lock_date=datetime.today(),
                                                  viettel_lock_date=None,
                                                  mobifone_lock_date=None,
                                                  vinaphone_lock_date=vinaphone_lock_date,
                                                  other_lock_date=None)

    lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                         id=phone_number.other_lock_history_id).first()

    if other_lock_date:
        if is_locked_phone_number(lock_history):
            lock_history.other_lock_date = other_lock_date
            lock_history.save()
        else:
            PhoneNumberLockHistory.objects.create(company=phone_number.company,
                                                  phone_number=phone_number,
                                                  checking_lock_date=datetime.today(),
                                                  confirm_lock_date=datetime.today(),
                                                  viettel_lock_date=None,
                                                  mobifone_lock_date=None,
                                                  vinaphone_lock_date=None,
                                                  other_lock_date=other_lock_date)

    update_lock_count(phone_number)


def update_unlock_information(phone_number, viettel_unlock_date, mobifone_unlock_date, vinaphone_unlock_date,
                              other_unlock_date):
    if viettel_unlock_date:
        lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                             id=phone_number.viettel_lock_history_id)
        if lock_history:
            lock = lock_history.first()
            lock.unlock_lock_date = viettel_unlock_date
            lock.save()

    if mobifone_unlock_date:
        lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                             id=phone_number.mobifone_lock_history_id)
        if lock_history:
            lock = lock_history.first()
            lock.unlock_lock_date = mobifone_unlock_date
            lock.save()

    if vinaphone_unlock_date:
        lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                             id=phone_number.vinaphone_lock_history_id)
        if lock_history:
            lock = lock_history.first()
            lock.unlock_lock_date = vinaphone_unlock_date
            lock.save()

    if other_unlock_date:
        lock_history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                             id=phone_number.other_lock_history_id)
        if lock_history:
            lock = lock_history.first()
            lock.unlock_lock_date = other_unlock_date
            lock.save()


def calculate_lock_information(phone_number, params):
    viettel_lock_date = params.get('viettel_lock_date', None)
    mobifone_lock_date = params.get('mobifone_lock_date', None)
    vinaphone_lock_date = params.get('vinaphone_lock_date', None)
    other_lock_date = params.get('other_lock_date', None)
    viettel_unlock_date = params.get('viettel_unlock_date', None)
    mobifone_unlock_date = params.get('mobifone_unlock_date', None)
    vinaphone_unlock_date = params.get('vinaphone_unlock_date', None)
    other_unlock_date = params.get('other_unlock_date', None)
    if viettel_lock_date or mobifone_lock_date or vinaphone_lock_date or other_lock_date:
        update_lock_information(phone_number, viettel_lock_date, mobifone_lock_date, vinaphone_lock_date,
                                other_lock_date)

    if viettel_unlock_date or mobifone_unlock_date or vinaphone_unlock_date or other_unlock_date:
        update_unlock_information(phone_number, viettel_unlock_date, mobifone_unlock_date, vinaphone_unlock_date,
                                  other_unlock_date)


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
            client_use_date = kwargs.get('client_use_date', None)
            if client_use_date is not None:
                kwargs['active_date'] = client_use_date

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

            trigger_update_phone_number_queue = False
            if kwargs.get('main_phone_number_id'):
                phone_number.main_phone_number_id = kwargs['main_phone_number_id']

            if kwargs.get('provider_id'):
                phone_number.provider_id = kwargs['provider_id']

            if kwargs.get('legal_id'):
                phone_number.legal_id = kwargs['legal_id']

            if kwargs.get('phone_number_client_id', 0) != 0:
                phone_number.phone_number_client_id = kwargs['phone_number_client_id']

            if kwargs.get('client_use_date', '') != '':
                if not phone_number.active_date:
                    phone_number.active_date = kwargs['client_use_date']
                phone_number.client_use_date = kwargs['client_use_date']

            if kwargs.get('provider_cancel_date', '') != '':
                phone_number.provider_cancel_date = kwargs['provider_cancel_date']

            if kwargs.get('phone_number_status_id'):
                old_status_id = phone_number.phone_number_status_id
                new_status_id = kwargs['phone_number_status_id']
                phone_number.phone_number_status_id = kwargs['phone_number_status_id']
                checking_status = PhoneNumberStatus.objects.get(name__iexact='Đang nghi ngờ',
                                                                company_id=phone_number.company_id,
                                                                deleted_at__isnull=True)
                add_new_status = PhoneNumberStatus.objects.get(name__iexact='Số mới nhập',
                                                               company_id=phone_number.company_id,
                                                               deleted_at__isnull=True)
                cancel_status = PhoneNumberStatus.objects.get(name__iexact='Đã hủy',
                                                              company_id=phone_number.company_id,
                                                              deleted_at__isnull=True)
                retest_status = PhoneNumberStatus.objects.get(name__iexact='Test sau mở',
                                                              company_id=phone_number.company_id,
                                                              deleted_at__isnull=True)
                trigger_status_list = [checking_status.id, add_new_status.id, retest_status.id]
                if old_status_id == new_status_id and old_status_id == checking_status.id:
                    trigger_update_phone_number_queue = True
                else:
                    if old_status_id in trigger_status_list:
                        phone_number.pic = request.user

                        if old_status_id in trigger_status_list or new_status_id in trigger_status_list:
                            trigger_update_phone_number_queue = True
                    else:
                        trigger_update_phone_number_queue = True
                if new_status_id == cancel_status.id:
                    phone_number.cancel_date = datetime.today()

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

            if kwargs.get('viettel_using_status', None) != phone_number.viettel_using_status:
                if kwargs.get('viettel_using_status', None) == 'USING' and not request.user.is_superuser:
                    phone_number.pic = request.user
                phone_number.viettel_using_status = kwargs['viettel_using_status']

            if kwargs.get('mobifone_using_status', None) != phone_number.mobifone_using_status:
                if kwargs.get('mobifone_using_status', None) == 'USING' and not request.user.is_superuser:
                    phone_number.pic = request.user
                phone_number.mobifone_using_status = kwargs['mobifone_using_status']

            if kwargs.get('vinaphone_using_status', None) != phone_number.vinaphone_using_status:
                if kwargs.get('vinaphone_using_status', None) == 'USING' and not request.user.is_superuser:
                    phone_number.pic = request.user
                phone_number.vinaphone_using_status = kwargs['vinaphone_using_status']

            if kwargs.get('other_using_status', None) != phone_number.other_using_status:
                if kwargs.get('other_using_status', None) == 'USING' and not request.user.is_superuser:
                    phone_number.pic = request.user
                phone_number.other_using_status = kwargs['other_using_status']

            if kwargs.get('viettel_unlocking_status', None) and kwargs.get('viettel_unlocking_status',
                                                                           None) != phone_number.viettel_unlocking_status:
                phone_number.viettel_unlocking_status = kwargs['viettel_unlocking_status']
                if phone_number.viettel_unlocking_status == 'SENT_PROVIDER':
                    lock = PhoneNumberLockHistory.objects.filter(pk=phone_number.viettel_lock_history_id).first()
                    if lock:
                        lock.send_provider_date = datetime.today()
                        lock.save()

            if kwargs.get('mobifone_unlocking_status', None) and kwargs.get('mobifone_unlocking_status',
                                                                            None) != phone_number.mobifone_unlocking_status:
                phone_number.mobifone_unlocking_status = kwargs['mobifone_unlocking_status']
                if phone_number.mobifone_unlocking_status == 'SENT_PROVIDER':
                    lock = PhoneNumberLockHistory.objects.filter(pk=phone_number.mobifone_lock_history_id).first()
                    if lock:
                        lock.send_provider_date = datetime.today()
                        lock.save()

            if kwargs.get('vinaphone_unlocking_status', None) and kwargs.get('vinaphone_unlocking_status',
                                                                             None) != phone_number.vinaphone_unlocking_status:
                phone_number.vinaphone_unlocking_status = kwargs['vinaphone_unlocking_status']
                if phone_number.vinaphone_unlocking_status == 'SENT_PROVIDER':
                    lock = PhoneNumberLockHistory.objects.filter(pk=phone_number.vinaphone_lock_history_id).first()
                    if lock:
                        lock.send_provider_date = datetime.today()
                        lock.save()

            if kwargs.get('other_unlocking_status', None) and kwargs.get('other_unlocking_status',
                                                                         None) != phone_number.other_unlocking_status:
                phone_number.other_unlocking_status = kwargs['other_unlocking_status']
                if phone_number.other_unlocking_status == 'SENT_PROVIDER':
                    lock = PhoneNumberLockHistory.objects.filter(pk=phone_number.other_lock_history_id).first()
                    if lock:
                        lock.send_provider_date = datetime.today()
                        lock.save()

            if kwargs.get('note', None) is not None:
                phone_number.note = kwargs['note']

            if phone_number.has_changed:
                PhoneNumberActivity.objects.create(phone_number=phone_number, company=phone_number.company,
                                                   user_id=request.user.id, diff=phone_number.diff)

            calculate_lock_information(phone_number, kwargs)

            phone_number.save()

            if trigger_update_phone_number_queue:
                self.trigger_update_phone_number_queue()

            return phone_number
        except PhoneNumber.DoesNotExist:
            raise PhoneNumberNotFound()

    def trigger_update_phone_number_queue(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'crm',
            {
                'type': 'trigger_update_phone_number_queue',
                'message': ''
            }
        )


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

        if 'client_use_date_from' in params and 'client_use_date_to' in params and params['client_use_date_from'] and \
                params['client_use_date_to']:
            query_set = query_set.filter(client_use_date__gte=params['client_use_date_from'],
                                         client_use_date__lte=params['client_use_date_to'])

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
                   'phone_number_client_list', 'phone_number_status_id_list', 'phone_number_avg_age',
                   'pics', 'lock_count_type', 'viettel_using_status', 'mobifone_using_status', 'vinaphone_using_status',
                   'other_using_status', 'sale_pics']
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'pics' and value is not None and value:
                if None in value:
                    query_set = query_set.filter(Q(pic__isnull=True) | Q(pic__in=value))
                else:
                    query_set = query_set.filter(pic__in=value)

            if key == 'sale_pics' and value is not None and value:
                phone_numeber_clients = PhoneNumberClient.objects.filter(deleted_at__isnull=True)
                if None in value:
                    phone_numeber_clients = phone_numeber_clients.filter(Q(pic__isnull=True) | Q(pic__in=value))

                    query_set = query_set.filter(Q(phone_number_client_id__isnull=True) | Q(
                        phone_number_client_id__in=phone_numeber_clients.values_list('id', flat=True)))
                else:
                    phone_numeber_clients = phone_numeber_clients.filter(pic__in=value)
                    query_set = query_set.filter(
                        phone_number_client_id__in=phone_numeber_clients.values_list('id', flat=True))

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

            if key == 'lock_count_type' and value:
                lock_count = params.get('lock_count', None)
                if lock_count is not None:
                    if PHONE_NUMBER_PROVIDER.VIETTEL in value:
                        if lock_count <= 5:
                            query_set = query_set.filter(
                                viettel_lock_count=lock_count,
                            )
                        else:
                            query_set = query_set.filter(
                                viettel_lock_count__gt=5,
                            )
                    if PHONE_NUMBER_PROVIDER.MOBI in value:
                        if lock_count <= 5:
                            query_set = query_set.filter(
                                mobifone_lock_count=lock_count,
                            )
                        else:
                            query_set = query_set.filter(
                                mobifone_lock_count__gt=5,
                            )
                    if PHONE_NUMBER_PROVIDER.VINA in value:
                        if lock_count <= 5:
                            query_set = query_set.filter(
                                vinaphone_lock_count=lock_count,
                            )
                        else:
                            query_set = query_set.filter(
                                vinaphone_lock_count__gt=5,
                            )
                    if PHONE_NUMBER_PROVIDER.OTHER in value:
                        if lock_count <= 5:
                            query_set = query_set.filter(
                                other_lock_count=lock_count,
                            )
                        else:
                            query_set = query_set.filter(
                                other_lock_count__gt=5,
                            )

            if key == 'viettel_using_status' and value:
                query_set = query_set.filter(viettel_using_status=value)

            if key == 'mobifone_using_status' and value:
                query_set = query_set.filter(mobifone_using_status=value)

            if key == 'vinaphone_using_status' and value:
                query_set = query_set.filter(vinaphone_using_status=value)

            if key == 'other_using_status' and value:
                query_set = query_set.filter(other_using_status=value)

        order_by = kwargs.get('order_by', None)
        if order_by:
            return query_set.order_by(order_by)

        return query_set.order_by('-id')


class FilterPhoneNumberTechnicalActivityService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumberTechnicalActivity.objects.filter(company_id=user_roles.first().company_id,
                                                                deleted_at__isnull=True)

        params = dict(kwargs.get('filter', []))

        if 'created_at_from' in params and 'created_at_to' in params and params['created_at_from'] and params[
            'created_at_to']:
            query_set = query_set.filter(created_at__gte=params['created_at_from'],
                                         created_at__lte=params['created_at_to'])

        filters = ['user_id_list', 'phone_number']
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'phone_number':
                query_set = query_set.filter(
                    phone_number__phone_number__icontains=value
                )

            if key == 'user_id_list' and value is not None and value:
                query_set = query_set.filter(main_phone_number_id__in=value)

        order_by = kwargs.get('order_by', None)
        if order_by:
            return query_set.order_by(order_by)

        return query_set.order_by('-id')


class RevertPhoneNumberTechnicalActivityService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        activity = PhoneNumberTechnicalActivity.objects.get(company_id=user_roles.first().company_id, pk=kwargs['id'],
                                                            deleted_at__isnull=True)

        phone_number = PhoneNumber.objects.get(pk=activity.phone_number.id)
        phone_number.viettel_using_status = activity.old_viettel_using_status
        phone_number.mobifone_using_status = activity.old_mobifone_using_status
        phone_number.vinaphone_using_status = activity.old_vinaphone_using_status
        phone_number.other_using_status = activity.old_other_using_status
        phone_number.viettel_unlocking_status = activity.old_viettel_unlocking_status
        phone_number.mobifone_unlocking_status = activity.old_mobifone_unlocking_status
        phone_number.vinaphone_unlocking_status = activity.old_vinaphone_unlocking_status
        phone_number.other_unlocking_status = activity.old_other_unlocking_status
        phone_number.phone_number_status_id = activity.old_phone_number_status_id

        old_status = PhoneNumberStatus.objects.filter(deleted_at__isnull=True,
                                                      id=activity.old_phone_number_status_id).first()
        if activity.phone_number_status.name == 'Đang bị khoá' and old_status and old_status.name == 'Đang nghi ngờ':
            if activity.viettel_lock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.viettel_lock_history_id).first()
                if lock:
                    lock.deleted_at = datetime.now(timezone(TIME_ZONE))
                    lock.save()
            if activity.mobifone_lock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.mobifone_lock_history_id).first()
                if lock:
                    lock.deleted_at = datetime.now(timezone(TIME_ZONE))
                    lock.save()
            if activity.vinaphone_lock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.vinaphone_lock_history_id).first()
                if lock:
                    lock.deleted_at = datetime.now(timezone(TIME_ZONE))
                    lock.save()
            if activity.other_lock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.other_lock_history_id).first()
                if lock:
                    lock.deleted_at = datetime.now(timezone(TIME_ZONE))
                    lock.save()

        if activity.phone_number_status.name == 'Số đã mở':
            if activity.viettel_unlock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.viettel_lock_history_id).first()
                if lock:
                    lock.unlock_lock_date = None
                    lock.save()
            if activity.mobifone_unlock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.mobifone_lock_history_id).first()
                if lock:
                    lock.unlock_lock_date = None
                    lock.save()
            if activity.vinaphone_unlock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.vinaphone_lock_history_id).first()
                if lock:
                    lock.unlock_lock_date = None
                    lock.save()
            if activity.other_unlock_date:
                lock = PhoneNumberLockHistory.objects.filter(id=phone_number.other_lock_history_id).first()
                if lock:
                    lock.unlock_lock_date = None
                    lock.save()

        update_lock_count(phone_number)
        phone_number.save()
        self.trigger_update_phone_number_queue()
        return phone_number

    def trigger_update_phone_number_queue(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'crm',
            {
                'type': 'trigger_update_phone_number_queue',
                'message': ''
            }
        )


class BulkUpdateStatusService(UpdatePhoneNumberService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        service = FilterPhoneNumberService()
        phone_numbers = service.serve(request, cookies, *args, **kwargs)
        status = kwargs.get('status', None)
        if status is None:
            return
        if phone_numbers.first() is None:
            return phone_numbers

        trigger_update_phone_number_queue = False
        checking_status = PhoneNumberStatus.objects.get(name__iexact='Đang nghi ngờ',
                                                        company_id=phone_numbers.first().company_id,
                                                        deleted_at__isnull=True)
        add_new_status = PhoneNumberStatus.objects.get(name__iexact='Số mới nhập',
                                                       company_id=phone_numbers.first().company_id,
                                                       deleted_at__isnull=True)
        cancel_status = PhoneNumberStatus.objects.get(name__iexact='Đã hủy',
                                                      company_id=phone_numbers.first().company_id,
                                                      deleted_at__isnull=True)
        retest_status = PhoneNumberStatus.objects.get(name__iexact='Test sau mở',
                                                      company_id=phone_numbers.first().company_id,
                                                      deleted_at__isnull=True)
        provider_cancel_status = PhoneNumberStatus.objects.get(name__iexact='Đã gửi nhà cung cấp hủy',
                                                      company_id=phone_numbers.first().company_id,
                                                      deleted_at__isnull=True)
        trigger_status_list = [checking_status.id, add_new_status.id, retest_status.id]

        for phone_number in phone_numbers:
            old_status_id = phone_number.phone_number_status_id
            new_status_id = status
            if old_status_id == new_status_id and old_status_id == checking_status.id:
                trigger_update_phone_number_queue = True
            else:
                if old_status_id in trigger_status_list:
                    phone_number.pic = request.user

                    if old_status_id in trigger_status_list or new_status_id in trigger_status_list:
                        trigger_update_phone_number_queue = True
                else:
                    trigger_update_phone_number_queue = True
            if new_status_id == cancel_status.id:
                phone_number.cancel_date = datetime.today()
            if new_status_id == provider_cancel_status.id:
                phone_number.provider_cancel_date = datetime.today()

            phone_number.phone_number_status_id = status
            phone_number.updated_at = datetime.now()
            if phone_number.has_changed:
                PhoneNumberActivity.objects.create(phone_number=phone_number, company=phone_number.company,
                                                   user_id=request.user.id, diff=phone_number.diff)
            phone_number.save()
        if trigger_update_phone_number_queue:
            self.trigger_update_phone_number_queue()
        return phone_numbers


class ImportStatusService(BaseService):
    def serve(self, status, phone_number, company_id, request):
        phone_number_obj = PhoneNumber.objects.get(phone_number__iexact=phone_number, company_id=company_id)
        if phone_number_obj:
            phone_number_obj.phone_number_status_id = status
            phone_number_obj.updated_at = datetime.now()
            if phone_number_obj.has_changed:
                PhoneNumberActivity.objects.create(phone_number=phone_number_obj, company=phone_number_obj.company,
                                                   user_id=request.user.id, diff=phone_number_obj.diff)
            phone_number_obj.save()


class ImportFeeService(BaseService):
    def serve(self, data_record, company_id, request):
        phone_number_obj = PhoneNumber.objects.get(phone_number__iexact=data_record['phone_number'],
                                                   company_id=company_id)
        if phone_number_obj:
            phone_number_obj.init_fee = data_record['init_fee']
            phone_number_obj.open_fee = data_record['open_fee']
            phone_number_obj.other_fee = data_record['other_fee']
            phone_number_obj.operate_fee = data_record['operate_fee']
            phone_number_obj.init_payment_date = data_record['init_payment_date']
            phone_number_obj.operate_payment_date = data_record['operate_payment_date']
            phone_number_obj.open_payment_date = data_record['open_payment_date']
            phone_number_obj.other_payment_date = data_record['other_payment_date']
            phone_number_obj.updated_at = datetime.now()
            if phone_number_obj.has_changed:
                PhoneNumberActivity.objects.create(phone_number=phone_number_obj, company=phone_number_obj.company,
                                                   user_id=request.user.id, diff=phone_number_obj.diff)
            phone_number_obj.save()


class GetStatisticPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        service = FilterPhoneNumberService()
        phone_numbers = service.serve(request, cookies, *args, **kwargs)

        res = {
            'age_avg': 0,
            'total_init_fee': 0,
            'total_operate_fee': 0,
            'total_open_fee': 0,
            'total_other_fee': 0,
            'technical_staff': []
        }

        technical_staff_statistic = {}

        departments = Department.objects.filter(deleted_at__isnull=True, company=user_roles.first().company,
                                                department_name='Phòng Kỹ Thuật');
        if departments:
            roles = Role.objects.filter(deleted_at__isnull=True, company=user_roles.first().company,
                                        department=departments.first())
            user_roles = UserRole.objects.filter(deleted_at__isnull=True, company=user_roles.first().company,
                                                 role_id__in=roles.values_list('id', flat=True))
            for user_role in user_roles:
                technical_staff_statistic[user_role.user.username] = 0

        for phone_number in phone_numbers:
            if phone_number.pic and phone_number.pic.username in technical_staff_statistic:
                technical_staff_statistic[phone_number.pic.username] += 1
            res['total_init_fee'] += phone_number.init_fee
            res['total_operate_fee'] += phone_number.operate_fee
            res['total_open_fee'] += phone_number.operate_fee
            res['total_other_fee'] += phone_number.other_fee
            res['age_avg'] += self.calculate_age(phone_number)

        if res['age_avg']:
            res['age_avg'] = res['age_avg'] / len(phone_numbers)
        for key, value in technical_staff_statistic.items():
            res['technical_staff'].append({
                'user': key,
                'count': value
            })

        return res

    def calculate_age(self, phone_number):
        if not phone_number.active_date:
            return 0

        last_date = phone_number.cancel_date if phone_number.cancel_date else datetime.today().date()
        return (last_date - phone_number.active_date).days + 1


class UpdateListPhoneNumberStatusService(UpdatePhoneNumberService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            with transaction.atomic():
                id_list = kwargs.get('phone_number_id_list')

                phone_numbers = PhoneNumber.objects.filter(deleted_at__isnull=True, id__in=id_list)
                trigger_update_phone_number_queue = False
                checking_status = PhoneNumberStatus.objects.get(name__iexact='Đang nghi ngờ',
                                                                company_id=phone_numbers.first().company_id,
                                                                deleted_at__isnull=True)
                add_new_status = PhoneNumberStatus.objects.get(name__iexact='Số mới nhập',
                                                               company_id=phone_numbers.first().company_id,
                                                               deleted_at__isnull=True)
                cancel_status = PhoneNumberStatus.objects.get(name__iexact='Đã hủy',
                                                              company_id=phone_numbers.first().company_id,
                                                              deleted_at__isnull=True)
                retest_status = PhoneNumberStatus.objects.get(name__iexact='Test sau mở',
                                                              company_id=phone_numbers.first().company_id,
                                                              deleted_at__isnull=True)
                provider_cancel_status = PhoneNumberStatus.objects.get(name__iexact='Đã gửi nhà cung cấp hủy',
                                                              company_id=phone_numbers.first().company_id,
                                                              deleted_at__isnull=True)
                trigger_status_list = [checking_status.id, add_new_status.id, retest_status.id]

                for phone_number in phone_numbers:
                    old_status_id = phone_number.phone_number_status_id
                    new_status_id = kwargs.get('phone_number_status_id')
                    if old_status_id == new_status_id and old_status_id == checking_status.id:
                        trigger_update_phone_number_queue = True
                    else:
                        if old_status_id in trigger_status_list:
                            phone_number.pic = request.user

                            if old_status_id in trigger_status_list or new_status_id in trigger_status_list:
                                trigger_update_phone_number_queue = True
                        else:
                            trigger_update_phone_number_queue = True
                    if new_status_id == cancel_status.id:
                        phone_number.cancel_date = datetime.today()
                    if new_status_id == provider_cancel_status.id:
                        phone_number.provider_cancel_date = datetime.today()

                    phone_number.phone_number_status_id = new_status_id
                    phone_number.updated_at = datetime.now()
                    if phone_number.has_changed:
                        PhoneNumberActivity.objects.create(phone_number=phone_number, company=phone_number.company,
                                                           user_id=request.user.id, diff=phone_number.diff)
                    phone_number.save()

            if trigger_update_phone_number_queue:
                self.trigger_update_phone_number_queue()

        except PhoneNumber.DoesNotExist:
            raise PhoneNumberNotFound()


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


class FilterPhoneNumberLockHistoryService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = PhoneNumberLockHistory.objects.filter(company_id=user_roles.first().company_id,
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


class PushToQueueService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        request_phone_number = request.GET.get('phone_number')
        company_name = request.GET.get('company')
        number_in_distributor = request.GET.get('number_in_distributor')
        number_left = request.GET.get('number_left')
        distributor_name = request.GET.get('distributor_name')
        lock_telco = request.GET.get('lock_telco')
        proxy = request.GET.get('proxy')
        company = Company.objects.filter(name__iexact=company_name, deleted_at__isnull=True).first()
        if not company:
            return

        phone_number = PhoneNumber.objects.filter(phone_number__iexact=request_phone_number, company_id=company.id,
                                                  deleted_at__isnull=True).first()
        if not phone_number:
            main_phone_number = MainPhoneNumber.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                                               deleted_at__isnull=True).first()
            provider = Provider.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                               deleted_at__isnull=True).first()
            legal = Legal.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                         deleted_at__isnull=True).first()
            phone_number_client = PhoneNumberClient.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                                                   deleted_at__isnull=True).first()
            phone_number_status = PhoneNumberStatus.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                                                   deleted_at__isnull=True).first()

            if not main_phone_number or not provider or not legal or not phone_number_client or not phone_number_status:
                return

            phone_number = PhoneNumber.objects.create(company=company,
                                                      phone_number=request_phone_number,
                                                      main_phone_number=main_phone_number,
                                                      provider=provider,
                                                      legal=legal,
                                                      phone_number_client=phone_number_client,
                                                      phone_number_status=phone_number_status,
                                                      pickup_date=datetime.now(),
                                                      brand='',
                                                      lock_provider='{"Viettel": false, "Mobifone": false, "Vinaphone": false, "Other": false}',
                                                      lock_count=0,
                                                      phone_number_avg_age=0,
                                                      cancel_date=None,
                                                      init_payment_date=None,
                                                      open_payment_date=None,
                                                      operate_payment_date=None,
                                                      other_payment_date=None,
                                                      number_in_distributor=number_in_distributor,
                                                      number_left=number_left,
                                                      distributor_name=distributor_name,
                                                      lock_telco=lock_telco,
                                                      proxy=proxy)
        else:
            phone_number.number_in_distributor = number_in_distributor
            phone_number.number_left = number_left
            phone_number.distributor_name = distributor_name
            phone_number.lock_telco = lock_telco
            phone_number.proxy = proxy

        phone_number.set_lock_provider(lock_telco)
        phone_number.save()
        phone_number_status = PhoneNumberStatus.objects.filter(name__iexact='Đang nghi ngờ', company_id=company.id,
                                                               deleted_at__isnull=True).first()
        if not phone_number_status:
            return
        phone_number.phone_number_status = phone_number_status
        service = UpdatePhoneNumberService()
        User = get_user_model()
        root_user = User.objects.get(username__iexact='root')
        request.user.is_superuser = True
        request.user.id = root_user.id

        service.serve(request, cookies, *args, **vars(phone_number))


class UsePhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        request_phone_number = request.GET.get('phone_number')
        company_name = request.GET.get('company')
        telco = request.GET.get('telco')
        company = Company.objects.filter(name__iexact=company_name, deleted_at__isnull=True).first()
        if not company:
            return

        phone_number = PhoneNumber.objects.filter(phone_number__iexact=request_phone_number, company_id=company.id,
                                                  deleted_at__isnull=True).first()
        if phone_number:
            if telco == 'Viettel':
                phone_number.viettel_using_status = 'USING'
            if telco == 'Mobifone':
                phone_number.mobifone_using_status = 'USING'
            if telco == 'Vinaphone':
                phone_number.vinaphone_using_status = 'USING'
            if telco == 'Other':
                phone_number.other_using_status = 'USING'

            service = UpdatePhoneNumberService()
            User = get_user_model()
            root_user = User.objects.get(username__iexact='root')
            request.user.is_superuser = True
            request.user.id = root_user.id

            service.serve(request, cookies, *args, **vars(phone_number))
        else:
            raise PhoneNumberNotFound()


class ImportPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        type = kwargs['type']
        kwargs.pop('type')
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
                error_codes = []
                if type == IMPORT_TYPE.IMPORT_NEW:
                    data_record = self.rowParser(row)
                    error_codes = self.validate_data(data_record, kwargs['company_id'])
                if type == IMPORT_TYPE.IMPORT_STATUS:
                    data_record = self.row_parser_import_status(row)
                    error_codes = self.validate_data_import_status(data_record, kwargs['company_id'])
                if type == IMPORT_TYPE.IMPORT_FEE:
                    data_record = self.row_parser_import_fee(row)
                    error_codes = self.validate_data_import_fee(data_record, kwargs['company_id'])
                if type == IMPORT_TYPE.IMPORT_STATUS_FOR_TECH:
                    data_record = self.row_parser_import_status_for_tech(row)
                    error_codes = self.validate_data_import_status_for_tech(data_record, kwargs['company_id'])
                if type == IMPORT_TYPE.IMPORT_LOCK_INFO:
                    data_record = self.row_paser_import_lock_info(row)
                    error_codes = self.validate_data_import_lock_info(data_record, kwargs['company_id'])

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
            'brand': str(rows[6].value).strip(),
            'lock_provider': '',
            'phone_number_status': str(rows[7].value).strip(),
            'pickup_date': str(rows[8].value).strip(),
            'cancel_date': str(rows[9].value).strip(),
            'init_fee': str(rows[10].value).strip(),
            'operate_fee': str(rows[11].value).strip(),
            'open_fee': str(rows[12].value).strip() if str(rows[12].value).strip() else 0,
            'other_fee': str(rows[13].value).strip() if str(rows[13].value).strip() else 0,
            'init_payment_date': str(rows[14].value).strip(),
            'open_payment_date': str(rows[15].value).strip(),
            'operate_payment_date': str(rows[16].value).strip(),
            'other_payment_date': str(rows[17].value).strip(),
            'note': str(rows[18].value).strip(),
            'client_use_date': str(rows[19].value).strip(),
        }

    def row_parser_import_status(self, rows):
        return {
            'id': '' if str(rows[0].value).strip() == '' else str(int(rows[0].value)),
            'phone_number': str(rows[1].value).strip(),
            'phone_number_status': str(rows[2].value).strip(),
            'phone_number_client': str(rows[3].value).strip(),
            'open_provider': str(rows[4].value).strip()
        }

    def row_parser_import_status_for_tech(self, rows):
        return {
            'id': '' if str(rows[0].value).strip() == '' else str(int(rows[0].value)),
            'phone_number': str(rows[1].value).strip(),
            'phone_number_status': str(rows[2].value).strip(),
            'viettel_lock_date': str(rows[3].value).strip(),
            'mobifone_lock_date': str(rows[4].value).strip(),
            'vinaphone_lock_date': str(rows[5].value).strip(),
            'other_lock_date': str(rows[6].value).strip(),
            'viettel_unlock_date': str(rows[7].value).strip(),
            'mobifone_unlock_date': str(rows[8].value).strip(),
            'vinaphone_unlock_date': str(rows[9].value).strip(),
            'other_unlock_date': str(rows[10].value).strip(),
        }

    def row_paser_import_lock_info(self, rows):
        return {
            'id': '' if str(rows[0].value).strip() == '' else str(int(rows[0].value)),
            'phone_number': str(rows[1].value).strip(),
            'using_providers': str(rows[2].value).strip(),
            'lock_provider': str(rows[3].value).strip(),
            'lock_date': str(rows[4].value).strip(),
            'open_provider': str(rows[5].value).strip(),
            'open_date': str(rows[6].value).strip(),
            'lock_status': str(rows[7].value).strip(),
            'send_provider_date': str(rows[8].value).strip(),
            'cancel_date': str(rows[9].value).strip(),
        }
    def row_parser_import_fee(self, rows):
        return {
            'id': '' if str(rows[0].value).strip() == '' else str(int(rows[0].value)),
            'phone_number': str(rows[1].value).strip(),
            'payment_date': str(rows[2].value).strip(),
            'on_net_fee': str(rows[3].value).strip(),
            'off_net_fee': str(rows[4].value).strip(),
            'billing_month': str(rows[5].value).strip() + '-01'
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

    def validate_data_import_fee(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_phone_format(data))
        error_codes.extend(self.validate_not_existed_phone(data, company_id))
        error_codes.extend(self.validate_monthly_fee_date(data))
        error_codes.extend(self.validate_monthly_fee(data))
        return error_codes

    def validate_data_import_status(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_phone_format(data))
        error_codes.extend(self.validate_not_existed_phone(data, company_id))
        error_codes.extend(self.validate_phone_number_status(data, company_id))
        error_codes.extend(self.validate_phone_number_client(data, company_id))
        return error_codes

    def validate_data_import_status_for_tech(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_phone_format(data))
        error_codes.extend(self.validate_not_existed_phone(data, company_id))
        error_codes.extend(self.validate_phone_number_status(data, company_id))
        error_codes.extend(self.validate_phone_number_status_date_for_tech(data, company_id))
        return error_codes

    def validate_data_import_lock_info(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_phone_format(data))
        error_codes.extend(self.validate_not_existed_phone(data, company_id))
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
        phone = str(row['phone_number']).strip()
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
        if entity is not None:
            return [vec.PhoneNumberDuplicated.code]

        return []

    def validate_not_existed_phone(self, row, company_id):
        phone = str(row['phone_number']).strip()

        entity = PhoneNumber.objects.filter(phone_number=phone, company_id=company_id, deleted_at__isnull=True).first()
        if entity is None:
            return [vec.PhoneNumberIsNotFound.code]

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
        if phone_number_client:
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

    def validate_phone_number_status_date_for_tech(self, row, company_id):
        error_codes = []
        phone = str(row['phone_number']).strip()

        phone_number = PhoneNumber.objects.filter(phone_number=phone, company_id=company_id,
                                                  deleted_at__isnull=True).first()
        if phone_number is None:
            return [vec.PhoneNumberIsNotFound.code]

        phone_number_status = str(row['phone_number_status']).strip()
        entity = PhoneNumberStatus.objects.filter(name__iexact=phone_number_status,
                                                  company_id=company_id).first()

        if entity is None:
            return [vec.PhoneNumberStatusNotFound.code]

        if phone_number.phone_number_status.name == 'Số mới nhập':
            if entity.name != 'Số đạt' and entity.name != 'Số không đạt':
                error_codes.append(vec.MovingNewStatusWrong.code)
        elif phone_number.phone_number_status.name == 'Đang nghi ngờ':
            if entity.name != 'Đang bị khoá' and entity.name != 'Cảnh báo sai':
                error_codes.append(vec.MovingMonitoringStatusWrong.code)
        elif phone_number.phone_number_status.name == 'Test sau mở':
            if entity.name != 'Đang bị khoá' and entity.name != 'Số đã mở':
                error_codes.append(vec.MovingRetestStatusWrong.code)
        elif phone_number.phone_number_status.name == 'Chờ hủy':
            if entity.name != 'Xác nhận hủy':
                error_codes.append(vec.MovingWaitingCancelStatusWrong.code)
        elif phone_number.phone_number_status.name == 'Xác nhận không sử dụng':
            if entity.name != 'Xác nhận không sử dụng':
                error_codes.append(vec.MovingNotUseStatusWrong.code)
        else:
            error_codes.append(vec.UseWrongStatusForTech.code)

        viettel_lock_date = str(row['viettel_lock_date']).strip()
        mobifone_lock_date = str(row['mobifone_lock_date']).strip()
        vinaphone_lock_date = str(row['vinaphone_lock_date']).strip()
        other_lock_date = str(row['other_lock_date']).strip()
        viettel_unlock_date = str(row['viettel_unlock_date']).strip()
        mobifone_unlock_date = str(row['mobifone_unlock_date']).strip()
        vinaphone_unlock_date = str(row['vinaphone_unlock_date']).strip()
        other_unlock_date = str(row['other_unlock_date']).strip()

        if viettel_lock_date and not self.validate_date_format_YYYYMMDD(viettel_lock_date):
            error_codes.append(vec.ViettelLockDateWrongFormat.code)
        if mobifone_lock_date and not self.validate_date_format_YYYYMMDD(mobifone_lock_date):
            error_codes.append(vec.MobiLockDateWrongFormat.code)
        if vinaphone_lock_date and not self.validate_date_format_YYYYMMDD(vinaphone_lock_date):
            error_codes.append(vec.VinaLockDateWrongFormat.code)
        if other_lock_date and not self.validate_date_format_YYYYMMDD(other_lock_date):
            error_codes.append(vec.OtherLockDateWrongFormat.code)

        if viettel_unlock_date and not self.validate_date_format_YYYYMMDD(viettel_unlock_date):
            error_codes.append(vec.ViettelUnLockDateWrongFormat.code)
        if mobifone_unlock_date and not self.validate_date_format_YYYYMMDD(mobifone_unlock_date):
            error_codes.append(vec.MobiUnLockDateWrongFormat.code)
        if vinaphone_unlock_date and not self.validate_date_format_YYYYMMDD(vinaphone_unlock_date):
            error_codes.append(vec.VinaUnLockDateWrongFormat.code)
        if other_unlock_date and not self.validate_date_format_YYYYMMDD(other_unlock_date):
            error_codes.append(vec.OtherUnLockDateWrongFormat.code)

        return error_codes

    def validate_date_format_YYYYMMDD(self, date_text):
        try:
            if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
                raise ValueError
            return True
        except ValueError:
            return False

    def validate_monthly_fee_date(self, row):
        error_codes = []
        payment_date = str(row['payment_date']).strip()
        billing_month = str(row['billing_month']).strip()

        if not self.validate_date_format_YYYYMMDD(payment_date):
            error_codes.append(vec.PaymentDateWrongFormat.code)
        if not self.validate_date_format_YYYYMMDD(billing_month):
            error_codes.append(vec.BillingMonthWrongFormat.code)

        return error_codes

    def validate_monthly_fee(self, row):
        error_codes = []
        on_net_fee = str(row['on_net_fee']).strip()
        off_net_fee = str(row['off_net_fee']).strip()
        if on_net_fee == '':
            error_codes.append(vec.OnNetFeeIsEmpty.code)

        if not self.isNumber(on_net_fee):
            error_codes.append(vec.OnNetFeeIsNotNumeric.code)

        if float(on_net_fee) == 0:
            error_codes.append(vec.OnNetFeeIsZero.code)

        if off_net_fee == '':
            error_codes.append(vec.OffNetFeeIsEmpty.code)

        if not self.isNumber(off_net_fee):
            error_codes.append(vec.OffNetFeeIsNotNumeric.code)

        if float(off_net_fee) == 0:
            error_codes.append(vec.OffNetFeeIsZero.code)

        return error_codes

    def validate_date(self, row):
        error_codes = []
        pickup_date = str(row['pickup_date']).strip()
        init_payment_date = str(row['init_payment_date']).strip()
        operate_payment_date = str(row['operate_payment_date']).strip()

        if not self.validate_date_format_YYYYMMDD(pickup_date):
            error_codes.append(vec.PickupDateWrongFormat.code)
        if not self.validate_date_format_YYYYMMDD(init_payment_date):
            error_codes.append(vec.InitPaymentDateWrongFormat.code)
        if not self.validate_date_format_YYYYMMDD(operate_payment_date):
            error_codes.append(vec.OperatePaymentDateWrongFormat.code)

        cancel_date = str(row['cancel_date']).strip()
        if cancel_date and not self.validate_date_format_YYYYMMDD(cancel_date):
            error_codes.append(vec.CancelDateWrongFormat.code)
        open_payment_date = str(row['open_payment_date']).strip()
        if open_payment_date and self.validate_date_format_YYYYMMDD(open_payment_date) == False:
            error_codes.append(vec.OpenPaymentDateWrongFormat.code)
        other_payment_date = str(row['other_payment_date']).strip()
        if other_payment_date and self.validate_date_format_YYYYMMDD(other_payment_date) == False:
            error_codes.append(vec.OpenPaymentDateWrongFormat.code)
        client_use_date = str(row['client_use_date']).strip()
        if client_use_date and self.validate_date_format_YYYYMMDD(client_use_date) == False:
            error_codes.append(vec.ClientUseDateWrongFormat.code)

        return error_codes

    def validate_fee(self, row):
        error_codes = []
        init_fee = str(row['init_fee']).strip()
        operate_fee = str(row['operate_fee']).strip()
        if init_fee == '':
            error_codes.append(vec.InitFeeIsEmpty.code)

        if not self.isNumber(init_fee):
            error_codes.append(vec.InitFeeIsNotNumeric.code)

        if float(init_fee) == 0:
            error_codes.append(vec.InitFeeIsZero.code)

        if operate_fee == '':
            error_codes.append(vec.OperateFeeIsEmpty.code)

        if not self.isNumber(operate_fee):
            error_codes.append(vec.OperateFeeIsNotNumeric.code)

        if float(operate_fee) == 0:
            error_codes.append(vec.OperateFeeIsZero.code)

        return error_codes

    def isNumber(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False


class ConfirmImportPhoneNumberService(ImportPhoneNumberService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        try:
            type = kwargs['type']
            record = ImportOrderRecords.objects.get(
                pk=kwargs.get('id')
            )

            create_phone_number_service = CreatePhoneNumberService()
            create_fee_service = CreatePhoneNumberMonthlyFeeService()
            with record.file.open('r') as excel_file:
                workbook = xlrd.open_workbook(excel_file.path, encoding_override='utf-8')
                worksheet = workbook.sheet_by_index(0)
                num_rows = worksheet.nrows - 1
                curr_row = 0
                while curr_row < num_rows:
                    curr_row += 1
                    row = worksheet.row(curr_row)
                    if type == IMPORT_TYPE.IMPORT_NEW:
                        data_record = self.rowParser(row)
                        error_codes = self.validate_data(data_record, kwargs['company_id'])
                        if not error_codes:
                            self.import_new(args, cookies, create_phone_number_service, data_record, kwargs, request)
                    if type == IMPORT_TYPE.IMPORT_STATUS:
                        data_record = self.row_parser_import_status(row)
                        error_codes = self.validate_data_import_status(data_record, kwargs['company_id'])
                        if not error_codes:
                            self.import_status(args, cookies, data_record, kwargs, request)
                    if type == IMPORT_TYPE.IMPORT_FEE:
                        data_record = self.row_parser_import_fee(row)
                        error_codes = self.validate_data_import_fee(data_record, kwargs['company_id'])
                        if not error_codes:
                            self.import_fee(args, cookies, create_fee_service, data_record, kwargs, request)

                    if type == IMPORT_TYPE.IMPORT_STATUS_FOR_TECH:
                        data_record = self.row_parser_import_status_for_tech(row)
                        error_codes = self.validate_data_import_status_for_tech(data_record, kwargs['company_id'])
                        if not error_codes:
                            self.import_status_for_tech(args, cookies, data_record, kwargs, request)

                    if type == IMPORT_TYPE.IMPORT_LOCK_INFO:
                        data_record = self.row_paser_import_lock_info(row)
                        error_codes = self.validate_data_import_lock_info(data_record, kwargs['company_id'])
                        if not error_codes:
                            self.import_lock_info(args, cookies, data_record, kwargs, request)

        except ImportOrderRecords.DoesNotExist:
            raise ImportRecordNotFound

    def import_new(self, args, cookies, create_phone_number_service, data_record, kwargs, request):
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
            main_phone_number=main_phone_number,
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
            client_use_date=data_record['client_use_date'],
            note=data_record['note'],
            company_id=kwargs['company_id'],
            created_at=datetime.today().date())
        create_phone_number_service.serve(request, cookies, *args,
                                          **CreatePhoneNumberRequestSerializer(phone_number).data)

    def import_status(self, args, cookies, data_record, kwargs, request):
        phone_number_status = PhoneNumberStatus.objects.filter(name=data_record['phone_number_status'],
                                                               deleted_at__isnull=True,
                                                               company_id=kwargs['company_id']).first()

        phone_number_client = PhoneNumberClient.objects.filter(name=data_record['phone_number_client'],
                                                               deleted_at__isnull=True,
                                                               company_id=kwargs['company_id']).first()

        phone_number = PhoneNumber.objects.get(phone_number__iexact=data_record['phone_number'],
                                               company_id=kwargs['company_id'])
        phone_number.phone_number_status = phone_number_status
        phone_number.phone_number_client = phone_number_client
        if data_record['open_provider'].lower() == 'Viettel'.lower():
            phone_number.viettel_unlocking_status = 'OPENED'
        if data_record['open_provider'].lower() == 'Mobifone'.lower():
            phone_number.mobifone_uhlocking_status = 'OPENED'
        if data_record['open_provider'].lower() == 'Vinaphone'.lower():
            phone_number.vinaphone_uhlocking_status = 'OPENED'
        if data_record['open_provider'].lower() == 'Other'.lower():
            phone_number.other_unlocking_status = 'OPENED'

        service = UpdatePhoneNumberService()
        service.serve(request, cookies, *args, **vars(phone_number))

    def import_fee(self, args, cookies, create_montly_fee_service, data_record, kwargs, request):
        phone_number = PhoneNumber.objects.get(phone_number__iexact=data_record['phone_number'],
                                               company_id=kwargs['company_id'])
        new_fee = PhoneNumberMonthlyFee(
            company_id=kwargs['company_id'],
            phone_number=phone_number,
            on_net_fee=data_record['on_net_fee'],
            off_net_fee=data_record['off_net_fee'],
            billing_month=data_record['billing_month'],
            payment_date=data_record['payment_date'],
        )

        create_montly_fee_service.serve(request, cookies, *args,
                                        **CreatePhoneNumberMonthlyFeeRequestSerializer(new_fee).data)

    def import_status_for_tech(self, args, cookies, data_record, kwargs, request):

        phone_number = PhoneNumber.objects.get(phone_number__iexact=data_record['phone_number'],
                                               company_id=kwargs['company_id'])
        phone_number_status = PhoneNumberStatus.objects.filter(name=data_record['phone_number_status'],
                                                               deleted_at__isnull=True,
                                                               company_id=kwargs['company_id']).first()
        payload = {
            'id': phone_number.id,
            'phone_number_status_id': phone_number_status.id,
            'viettel_lock_date': None,
            'mobifone_lock_date': None,
            'vinaphone_lock_date': None,
            'other_lock_date': None,
            'viettel_unlock_date': None,
            'mobifone_unlock_date': None,
            'vinaphone_unlock_date': None,
            'other_unlock_date': None
        }

        if phone_number_status.name == 'Đang bị khoá':
            payload['viettel_lock_date'] = data_record['viettel_lock_date']
            payload['mobifone_lock_date'] = data_record['mobifone_lock_date']
            payload['vinaphone_lock_date'] = data_record['vinaphone_lock_date']
            payload['other_lock_date'] = data_record['other_lock_date']
        elif phone_number_status.name == 'Số đã mở':
            payload['viettel_unlock_date'] = data_record['viettel_unlock_date']
            payload['mobifone_unlock_date'] = data_record['mobifone_unlock_date']
            payload['vinaphone_unlock_date'] = data_record['vinaphone_unlock_date']
            payload['other_unlock_date'] = data_record['other_unlock_date']

        service = CheckPhoneNumberService()
        service.serve(request, cookies, *args, **payload)

    def get_lock_status(self, lock_status):
        if lock_status == 'Đã gửi nhà cung cấp' or lock_status == 'Đã gửi NCC':
            return 'SENT_PROVIDER'
        if lock_status == 'Đã mở':
            return 'OPENED'
        if lock_status == 'Nhà cung cấp báo sai':
            return 'WRONG_REPORT'
        return 'AVAILABLE'

    def import_lock_info(self, args, cookies, data_record, kwargs, request):
        phone_number = PhoneNumber.objects.filter(phone_number__icontains=data_record['phone_number']).first()
        VIETTEL = 'Viettel'
        MOBIFONE = 'Mobifone'
        VINAPHONE = 'Vinaphone'
        using_providers = data_record['using_providers']
        lock_provider = data_record['lock_provider']
        lock_date = data_record['lock_date']
        open_provider = data_record['open_provider']
        open_date = data_record['open_date']
        lock_status = data_record['lock_status']
        send_provider_date = data_record['send_provider_date']
        cancel_date = data_record['cancel_date']
        if phone_number:
            with transaction.atomic():
                if lock_provider:
                    lock = PhoneNumberLockHistory.objects.create(company=phone_number.company,
                                                                 phone_number=phone_number,
                                                                 checking_lock_date=datetime.today(),
                                                                 confirm_lock_date=datetime.today(),
                                                                 viettel_lock_date=None,
                                                                 mobifone_lock_date=None,
                                                                 vinaphone_lock_date=None,
                                                                 other_lock_date=None)
                    if lock_provider.strip() == VIETTEL:
                        lock.viettel_lock_date = datetime.strptime(lock_date.strip().replace(' ', ''), '%d/%m/%Y')
                        if open_date.strip():
                            lock.unlock_lock_date = datetime.strptime(open_date.strip().replace(' ', ''), '%d/%m/%Y')
                            phone_number.viettel_using_status = 'OPEN'
                        else:
                            phone_number.viettel_using_status = 'LOCK'
                            if send_provider_date.strip():
                                lock.send_provider_date = datetime.strptime(send_provider_date.strip().replace(' ', ''),
                                                                            '%d/%m/%Y')
                        if lock_status:
                            phone_number.viettel_unlocking_status = self.get_lock_status(lock_status)
                    if lock_provider.strip() == VINAPHONE:
                        lock.vinaphone_lock_date = datetime.strptime(lock_date.strip().replace(' ', ''), '%d/%m/%Y')
                        if open_date.strip():
                            lock.unlock_lock_date = datetime.strptime(open_date.strip().replace(' ', ''), '%d/%m/%Y')
                            phone_number.vinaphone_using_status = 'OPEN'
                        else:
                            phone_number.vinaphone_using_status = 'LOCK'
                            if send_provider_date.strip():
                                lock.send_provider_date = datetime.strptime(send_provider_date.strip().replace(' ', ''),
                                                                            '%d/%m/%Y')
                        if lock_status:
                            phone_number.vinaphone_unlocking_status = self.get_lock_status(lock_status)
                    if lock_provider.strip() == MOBIFONE:
                        lock.mobifone_lock_date = datetime.strptime(lock_date.strip().replace(' ', ''), '%d/%m/%Y')
                        if open_date.strip():
                            lock.unlock_lock_date = datetime.strptime(open_date.strip().replace(' ', ''), '%d/%m/%Y')
                            phone_number.mobifone_using_status = 'OPEN'
                        else:
                            phone_number.mobifone_using_status = 'LOCK'
                            if send_provider_date.strip():
                                lock.send_provider_date = datetime.strptime(send_provider_date.strip().replace(' ', ''),
                                                                            '%d/%m/%Y')
                        if lock_status:
                            phone_number.mobifone_unlocking_status = self.get_lock_status(lock_status)
                    lock.save()

                provider_list = using_providers.split(',')
                for provider in provider_list:
                    if provider.strip() == VIETTEL:
                        phone_number.viettel_using_status = 'USING'
                    if provider.strip() == VINAPHONE:
                        phone_number.vinaphone_using_status = 'USING'
                    if provider.strip() == MOBIFONE:
                        phone_number.mobifone_using_status = 'USING'

                if cancel_date:
                    status = PhoneNumberStatus.objects.filter(name__iexact='Đã hủy', company_id=17).first()
                    phone_number.provider_cancel_date = datetime.strptime(cancel_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if status:
                        phone_number.phone_number_status_id = status.id
                # if client_use_date:
                #     phone_number.client_use_date = datetime.strptime(client_use_date.strip().replace(' ', ''), '%d/%m/%Y')
                #     if not phone_number.active_date:
                #         phone_number.active_date = phone_number.client_use_date

                update_lock_count(phone_number)
                phone_number.save()


class CheckPhoneNumberService(BaseService):
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

            if kwargs.get('viettel_lock_date', None) and phone_number.pickup_date \
                    and kwargs.get('viettel_lock_date', None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('mobifone_lock_date', None) and phone_number.pickup_date and kwargs.get('mobifone_lock_date',
                                                                                                  None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('vinaphone_lock_date', None) and phone_number.pickup_date and kwargs.get(
                    'vinaphone_lock_date',
                    None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('other_lock_date', None) and phone_number.pickup_date and kwargs.get('other_lock_date',
                                                                                               None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('viettel_unlock_date', None) and phone_number.pickup_date and kwargs.get(
                    'viettel_unlock_date',
                    None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('mobifone_unlock_date', None) and phone_number.pickup_date and kwargs.get(
                    'mobifone_unlock_date',
                    None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('vinaphone_unlock_date', None) and phone_number.pickup_date and kwargs.get(
                    'vinaphone_unlock_date',
                    None) < phone_number.pickup_date:
                raise InvalidInpputDate()
            if kwargs.get('other_unlock_date', None) and phone_number.pickup_date and kwargs.get('other_unlock_date',
                                                                                                 None) < phone_number.pickup_date:
                raise InvalidInpputDate()

            trigger_update_phone_number_queue = False
            trigger_update_lock_history = False

            technical_activity = PhoneNumberTechnicalActivity()
            technical_activity.company = phone_number.company
            technical_activity.phone_number = phone_number
            technical_activity.user_id = request.user.id
            technical_activity.old_viettel_using_status = phone_number.viettel_using_status
            technical_activity.old_mobifone_using_status = phone_number.mobifone_using_status
            technical_activity.old_vinaphone_using_status = phone_number.vinaphone_using_status
            technical_activity.old_other_using_status = phone_number.other_using_status
            technical_activity.old_viettel_unlocking_status = phone_number.viettel_unlocking_status
            technical_activity.old_mobifone_unlocking_status = phone_number.mobifone_unlocking_status
            technical_activity.old_vinaphone_unlocking_status = phone_number.vinaphone_unlocking_status
            technical_activity.old_other_unlocking_status = phone_number.other_unlocking_status
            technical_activity.old_phone_number_status_id = phone_number.phone_number_status_id
            technical_activity.viettel_lock_date = kwargs.get('viettel_lock_date', None)
            technical_activity.mobifone_lock_date = kwargs.get('mobifone_lock_date', None)
            technical_activity.vinaphone_lock_date = kwargs.get('vinaphone_lock_date', None)
            technical_activity.other_lock_date = kwargs.get('other_lock_date', None)
            technical_activity.viettel_unlock_date = kwargs.get('viettel_unlock_date', None)
            technical_activity.mobifone_unlock_date = kwargs.get('mobifone_unlock_date', None)
            technical_activity.vinaphone_unlock_date = kwargs.get('vinaphone_unlock_date', None)
            technical_activity.other_unlock_date = kwargs.get('other_unlock_date', None)
            technical_activity.phone_number_status_id = kwargs.get('phone_number_status_id', None)

            if kwargs.get('phone_number_status_id'):
                old_status_id = phone_number.phone_number_status_id
                new_status_id = kwargs['phone_number_status_id']
                phone_number.phone_number_status_id = kwargs['phone_number_status_id']
                checking_status = PhoneNumberStatus.objects.get(name__iexact='Đang nghi ngờ',
                                                                company_id=phone_number.company_id,
                                                                deleted_at__isnull=True)
                add_new_status = PhoneNumberStatus.objects.get(name__iexact='Số mới nhập',
                                                               company_id=phone_number.company_id,
                                                               deleted_at__isnull=True)
                retest_status = PhoneNumberStatus.objects.get(name__iexact='Test sau mở',
                                                              company_id=phone_number.company_id,
                                                              deleted_at__isnull=True)
                false_positive = PhoneNumberStatus.objects.get(name__iexact='Cảnh báo sai',
                                                               company_id=phone_number.company_id,
                                                               deleted_at__isnull=True)
                wait_cancel = PhoneNumberStatus.objects.get(name__iexact='Chờ hủy',
                                                            company_id=phone_number.company_id,
                                                            deleted_at__isnull=True)
                not_use = PhoneNumberStatus.objects.get(name__iexact='Không được sử dụng',
                                                        company_id=phone_number.company_id,
                                                        deleted_at__isnull=True)
                lock = PhoneNumberStatus.objects.get(name__iexact='Đang bị khoá',
                                                     company_id=phone_number.company_id,
                                                     deleted_at__isnull=True)
                unlock = PhoneNumberStatus.objects.get(name__iexact='Số đã mở',
                                                       company_id=phone_number.company_id,
                                                       deleted_at__isnull=True)

                trigger_status_list = [checking_status.id, add_new_status.id, retest_status.id, wait_cancel.id,
                                       not_use.id]
                if old_status_id in trigger_status_list:
                    phone_number.pic = request.user
                    trigger_update_phone_number_queue = True

                if new_status_id == lock.id:
                    phone_number.phone_number_status_id = self.get_new_status_after_lock(phone_number)
                    if old_status_id != retest_status.id:
                        trigger_update_lock_history = True
                        if phone_number.viettel_using_status == 'LOCK' and kwargs.get('viettel_lock_date',
                                                                                      None) is None:
                            phone_number.viettel_using_status = 'OPEN'
                        if phone_number.mobifone_using_status == 'LOCK' and kwargs.get('mobifone_lock_date',
                                                                                       None) is None:
                            phone_number.mobifone_using_status = 'OPEN'
                        if phone_number.vinaphone_using_status == 'LOCK' and kwargs.get('vinaphone_lock_date',
                                                                                        None) is None:
                            phone_number.vinaphone_using_status = 'OPEN'
                        if phone_number.other_using_status == 'LOCK' and kwargs.get('other_lock_date', None) is None:
                            phone_number.other_using_status = 'OPEN'

                        if kwargs.get('viettel_lock_date', None):
                            phone_number.viettel_using_status = 'LOCK'
                        if kwargs.get('mobifone_lock_date', None):
                            phone_number.mobifone_using_status = 'LOCK'
                        if kwargs.get('vinaphone_lock_date', None):
                            phone_number.vinaphone_using_status = 'LOCK'
                        if kwargs.get('other_lock_date', None):
                            phone_number.other_using_status = 'LOCK'

                if old_status_id == retest_status.id and new_status_id == lock.id:
                    if phone_number.viettel_unlocking_status == 'OPENED':
                        phone_number.viettel_unlocking_status = 'WRONG_REPORT'
                    if phone_number.mobifone_unlocking_status == 'OPENED':
                        phone_number.mobifone_unlocking_status = 'WRONG_REPORT'
                    if phone_number.vinaphone_unlocking_status == 'OPENED':
                        phone_number.vinaphone_unlocking_status = 'WRONG_REPORT'
                    if phone_number.other_unlocking_status == 'OPENED':
                        phone_number.other_unlocking_status = 'WRONG_REPORT'
                    phone_number.phone_number_status_id = self.get_new_status_after_lock(phone_number)

                if old_status_id == retest_status.id and new_status_id == unlock.id:
                    if phone_number.viettel_unlocking_status == 'OPENED':
                        if kwargs.get('viettel_unlock_date', None):
                            phone_number.viettel_unlocking_status = 'AVAILABLE'
                        else:
                            phone_number.viettel_unlocking_status = 'WRONG_REPORT'
                    if phone_number.mobifone_unlocking_status == 'OPENED':
                        if kwargs.get('mobifone_unlock_date', None):
                            phone_number.mobifone_unlocking_status = 'AVAILABLE'
                        else:
                            phone_number.mobifone_unlocking_status = 'WRONG_REPORT'
                    if phone_number.vinaphone_unlocking_status == 'OPENED':
                        if kwargs.get('vinaphone_unlock_date', None):
                            phone_number.vinaphone_unlocking_status = 'AVAILABLE'
                        else:
                            phone_number.vinaphone_unlocking_status = 'WRONG_REPORT'
                    if phone_number.other_unlocking_status == 'OPENED':
                        if kwargs.get('other_unlock_date', None):
                            phone_number.other_unlocking_status = 'AVAILABLE'
                        else:
                            phone_number.other_unlocking_status = 'WRONG_REPORT'

                    if phone_number.viettel_using_status == 'LOCK' and kwargs.get('viettel_unlock_date', None):
                        phone_number.viettel_using_status = 'OPEN'
                    if phone_number.mobifone_using_status == 'LOCK' and kwargs.get('mobifone_unlock_date', None):
                        phone_number.mobifone_using_status = 'OPEN'
                    if phone_number.vinaphone_using_status == 'LOCK' and kwargs.get('vinaphone_unlock_date', None):
                        phone_number.vinaphone_using_status = 'OPEN'
                    if phone_number.other_using_status == 'LOCK' and kwargs.get('other_unlock_date', None):
                        phone_number.other_using_status = 'OPEN'

                    trigger_update_lock_history = True
                    phone_number.phone_number_status_id = self.get_new_status_after_lock(phone_number)

                if new_status_id == false_positive.id:
                    if phone_number.viettel_using_status == 'LOCK':
                        phone_number.viettel_using_status = 'OPEN'
                    if phone_number.mobifone_using_status == 'LOCK':
                        phone_number.mobifone_using_status = 'OPEN'
                    if phone_number.vinaphone_using_status == 'LOCK':
                        phone_number.vinaphone_using_status = 'OPEN'
                    if phone_number.other_using_status == 'LOCK':
                        phone_number.other_using_status = 'OPEN'
                    phone_number.phone_number_status_id = self.get_new_status_after_lock(phone_number)

                technical_activity.viettel_using_status = phone_number.viettel_using_status
                technical_activity.mobifone_using_status = phone_number.mobifone_using_status
                technical_activity.vinaphone_using_status = phone_number.vinaphone_using_status
                technical_activity.other_using_status = phone_number.other_using_status
                technical_activity.viettel_unlocking_status = phone_number.viettel_unlocking_status
                technical_activity.mobifone_unlocking_status = phone_number.mobifone_unlocking_status
                technical_activity.vinaphone_unlocking_status = phone_number.vinaphone_unlocking_status
                technical_activity.other_unlocking_status = phone_number.other_unlocking_status

            if phone_number.has_changed:
                PhoneNumberActivity.objects.create(phone_number=phone_number, company=phone_number.company,
                                                   user_id=request.user.id, diff=phone_number.diff)

            if trigger_update_lock_history:
                calculate_lock_information(phone_number, kwargs)

            technical_activity.save()
            phone_number.last_technical_activity_id = technical_activity.id
            phone_number.save()

            if trigger_update_phone_number_queue:
                self.trigger_update_phone_number_queue()

            return phone_number
        except PhoneNumber.DoesNotExist:
            raise PhoneNumberNotFound()

    def get_new_status_after_lock(self, phone_number):
        if phone_number.viettel_using_status == 'USING' or phone_number.mobifone_using_status == 'USING' or \
                phone_number.vinaphone_using_status == 'USING' or phone_number.other_using_status == 'USING':
            return PhoneNumberStatus.objects.get(name__iexact='Đang sử dụng',
                                                 company_id=phone_number.company_id,
                                                 deleted_at__isnull=True).id

        if phone_number.viettel_using_status == 'LOCK' and phone_number.mobifone_using_status == 'LOCK' and \
                phone_number.vinaphone_using_status == 'LOCK' and phone_number.other_using_status == 'LOCK':
            return PhoneNumberStatus.objects.get(name__iexact='Đang bị khoá',
                                                 company_id=phone_number.company_id,
                                                 deleted_at__isnull=True).id

        return PhoneNumberStatus.objects.get(name__iexact='Chưa sử dụng',
                                             company_id=phone_number.company_id,
                                             deleted_at__isnull=True).id

    def trigger_update_phone_number_queue(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'crm',
            {
                'type': 'trigger_update_phone_number_queue',
                'message': ''
            }
        )


class ExportPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        service = FilterPhoneNumberService()
        phone_numbers = service.serve(request, cookies, *args, **{'filter': kwargs, 'order_by': 'id'})
        export_request = ExportOrderRequest.objects.create()
        file_path = MEDIA_ROOT + '/' + 'export_data' + '/' + str(export_request.id) + '_' + str(
            export_request.created_at.timestamp()) + '.xls'

        export_data = []
        for phone_number in phone_numbers:
            export_data.append(self.normalize_order_row(phone_number))

        df = pd.DataFrame(export_data, columns=['ID',
                                                'Số',
                                                'Số chủ',
                                                'Nhà cung cấp',
                                                'Pháp nhân',
                                                'Số khách',
                                                'Trạng thái',
                                                'Ngày lấy',
                                                'Ngày khách lấy',
                                                'Brand',
                                                'Tuổi thọ',
                                                'Ngày hủy',
                                                'Phí khởi tạo',
                                                'Phí vận hành',
                                                'Phí mở',
                                                'Phí khác',
                                                'Ngày nhập phí tạo',
                                                'Ngày nhập phí mở',
                                                'Ngày nhập phí vận hành',
                                                'Ngày nhập phí khác',
                                                'Ghi chú',
                                                'Số lần khóa Viettel',
                                                'Số lần khóa Mobifone',
                                                'Số lần khóa Vinaphone',
                                                'Số lần khóa Ngoại mạng',
                                                'Ngày đầu khách lấy',
                                                'Ngày báo NCC hủy',
                                                'Thời gian tạo'])
        df.to_excel(file_path, index=False, header=True)
        export_request.file.name = file_path[len(MEDIA_ROOT):]
        export_request.save()

        return export_request

    def normalize_order_row(self, phone_number):
        return [
            phone_number.id,
            phone_number.phone_number,
            phone_number.main_phone_number.name if phone_number.main_phone_number is not None else '',
            phone_number.provider.name if phone_number.provider is not None else '',
            phone_number.legal.name if phone_number.legal is not None else '',
            phone_number.phone_number_client.name if phone_number.phone_number_client is not None else '',
            phone_number.phone_number_status.name if phone_number.phone_number_status is not None else '',
            phone_number.pickup_date.__str__() if phone_number.pickup_date is not None else '',
            phone_number.client_use_date.__str__() if phone_number.client_use_date is not None else '',
            phone_number.brand,
            phone_number.phone_number_avg_age.__str__(),
            phone_number.cancel_date.__str__() if phone_number.cancel_date is not None else '',
            phone_number.init_fee.__str__(),
            phone_number.operate_fee.__str__(),
            phone_number.open_fee.__str__(),
            phone_number.other_fee.__str__(),
            phone_number.init_payment_date.__str__() if phone_number.init_payment_date is not None else '',
            phone_number.open_payment_date.__str__() if phone_number.open_payment_date is not None else '',
            phone_number.operate_payment_date.__str__() if phone_number.operate_payment_date is not None else '',
            phone_number.other_payment_date.__str__() if phone_number.other_payment_date is not None else '',
            phone_number.note,
            phone_number.viettel_lock_count.__str__(),
            phone_number.mobifone_lock_count.__str__(),
            phone_number.vinaphone_lock_count.__str__(),
            phone_number.other_lock_count.__str__(),
            phone_number.active_date.__str__() if phone_number.active_date is not None else '',
            phone_number.provider_cancel_date.__str__() if phone_number.provider_cancel_date is not None else '',
            phone_number.created_at.astimezone(timezone(TIME_ZONE)).__str__()]


class CopyPhoneNumberService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter_phone_number_service = FilterPhoneNumberService()
        phone_numbers = filter_phone_number_service.serve(request, cookies, *args, **kwargs)
        number_list = list(phone_numbers.values_list('phone_number', flat=True))
        return '\r\n'.join(number_list)


class BulkUpdateStatusForTechService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        service = FilterPhoneNumberService()
        phone_numbers = service.serve(request, cookies, *args, **kwargs)
        status = kwargs.get('status', None)
        service = CheckPhoneNumberService()
        if status is None:
            return
        with transaction.atomic():
            for phone_number in phone_numbers:
                if not self.validate_status(status, phone_number):
                    raise InvalidPhoneNumberStatus()

                payload = self.create_payload(phone_number, status)
                if payload:
                    serializer = CheckPhoneNumberRequestSerializer(data=payload)
                    serializer.is_valid()
                    service.serve(request, cookies, *args, **serializer.validated_data)

        return phone_numbers

    def create_payload(self, phone_number, status_id):
        phone_number_status = PhoneNumberStatus.objects.filter(deleted_at__isnull=True, id=status_id).first()
        if not phone_number_status:
            return None

        payload = {
            'id': phone_number.id,
            'phone_number_status_id': phone_number_status.id,
            'viettel_lock_date': None,
            'mobifone_lock_date': None,
            'vinaphone_lock_date': None,
            'other_lock_date': None,
            'viettel_unlock_date': None,
            'mobifone_unlock_date': None,
            'vinaphone_unlock_date': None,
            'other_unlock_date': None
        }

        if phone_number_status.name == 'Đang bị khoá':
            payload['viettel_lock_date'] = self.get_lock_date(phone_number, PHONE_NUMBER_PROVIDER.VIETTEL)
            payload['mobifone_lock_date'] = self.get_lock_date(phone_number, PHONE_NUMBER_PROVIDER.MOBI)
            payload['vinaphone_lock_date'] = self.get_lock_date(phone_number, PHONE_NUMBER_PROVIDER.VINA)
            payload['other_lock_date'] = self.get_lock_date(phone_number, PHONE_NUMBER_PROVIDER.OTHER)
        elif phone_number_status.name == 'Số đã mở':
            payload['viettel_unlock_date'] = self.get_unlock_date(phone_number, PHONE_NUMBER_PROVIDER.VIETTEL)
            payload['mobifone_unlock_date'] = self.get_unlock_date(phone_number, PHONE_NUMBER_PROVIDER.MOBI)
            payload['vinaphone_unlock_date'] = self.get_unlock_date(phone_number, PHONE_NUMBER_PROVIDER.VINA)
            payload['other_unlock_date'] = self.get_unlock_date(phone_number, PHONE_NUMBER_PROVIDER.OTHER)

        return payload

    def get_unlock_date(self, phone_number, type):
        return datetime.today().strftime('%Y-%m-%d')

    def get_lock_date(self, phone_number, type):
        lock_provider_json = {}
        if phone_number.lock_provider:
            lock_provider_json = json.loads(phone_number.lock_provider)
        lock_date = None
        if type == PHONE_NUMBER_PROVIDER.VIETTEL:
            if phone_number.viettel_using_status != 'LOCK':
                return None

            history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                            id=phone_number.viettel_lock_history_id).first()
            if history and history.unlock_lock_date is None:
                lock_date = history.viettel_lock_date
            if lock_date is None:
                if 'Viettel' in lock_provider_json and 'viettelEnterDate' in lock_provider_json and lock_provider_json[
                    'Viettel']:
                    lock_date = lock_provider_json['viettelEnterDate']
        if type == PHONE_NUMBER_PROVIDER.VINA:
            if phone_number.vinaphone_using_status != 'LOCK':
                return None

            history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                            id=phone_number.vinaphone_lock_history_id).first()
            if history and history.unlock_lock_date is None:
                lock_date = history.vinaphone_lock_date
            if lock_date is None:
                if 'Vinaphone' in lock_provider_json and 'vinaphoneEnterDate' in lock_provider_json and \
                        lock_provider_json['Vinaphone']:
                    lock_date = lock_provider_json['vinaphoneEnterDate']
        if type == PHONE_NUMBER_PROVIDER.MOBI:
            if phone_number.mobifone_using_status != 'LOCK':
                return None

            history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                            id=phone_number.mobifone_lock_history_id).first()
            if history and history.unlock_lock_date is None:
                lock_date = history.mobifone_lock_date
            if lock_date is None:
                if 'Mobifone' in lock_provider_json and 'mobifoneEnterDate' in lock_provider_json and \
                        lock_provider_json['Mobifone']:
                    lock_date = lock_provider_json['mobifoneEnterDate']
        if type == PHONE_NUMBER_PROVIDER.OTHER:
            if phone_number.other_using_status != 'LOCK':
                return None

            history = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True,
                                                            id=phone_number.other_lock_history_id).first()
            if history and history.unlock_lock_date is None:
                lock_date = history.other_lock_date
            if lock_date is None:
                if 'Other' in lock_provider_json and 'otherEnterDate' in lock_provider_json and lock_provider_json[
                    'Other']:
                    lock_date = lock_provider_json['otherEnterDate']

        if lock_date is None:
            lock_date = datetime.now().strftime('%Y-%m-%d')

        if not isinstance(lock_date, str):
            lock_date = lock_date.strftime('%Y-%m-%d')

        return lock_date

    def validate_status(self, status_id, phone_number):
        status = PhoneNumberStatus.objects.filter(deleted_at__isnull=True, id=status_id).first()
        if status:
            if phone_number.phone_number_status.name == 'Đang nghi ngờ':
                return status.name == 'Đang bị khoá' or status.name == 'Cảnh báo sai'

            if phone_number.phone_number_status.name == 'Test sau mở':
                return status.name == 'Đang bị khoá' or status.name == 'Số đã mở'

            if phone_number.phone_number_status.name == 'Chờ hủy':
                return status.name == 'Xác nhận hủy'

            if phone_number.phone_number_status.name == 'Số mới nhập':
                return status.name == 'Số đạt' or status.name == 'Số không đạt'

            if phone_number.phone_number_status.name == 'Không được sử dụng':
                return status.name == 'Xác nhận không sử dụng'
        return True


class UpdateListPhoneNumberStatusForTechService(BulkUpdateStatusForTechService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            service = CheckPhoneNumberService()
            with transaction.atomic():
                id_list = kwargs.get('phone_number_id_list')

                for phone_number_id in id_list:
                    phone_number = PhoneNumber.objects.get(pk=phone_number_id)
                    if not self.validate_status(kwargs.get('phone_number_status_id'), phone_number):
                        raise InvalidPhoneNumberStatus()

                    payload = self.create_payload(phone_number, kwargs.get('phone_number_status_id'))
                    if payload:
                        serializer = CheckPhoneNumberRequestSerializer(data=payload)
                        serializer.is_valid()
                        service.serve(request, cookies, *args, **serializer.validated_data)

        except PhoneNumber.DoesNotExist:
            raise PhoneNumberNotFound()
