import json
import math
import re
from datetime import datetime
from pytz import timezone

import pandas as pd
import xlrd
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.aggregates import Sum

from api.common.base_service import BaseService
from api.common.common import Common
from api.common.cookies import Cookies
from api.const import PRODUCT_PAYMENT_METHOD, ORDER_PAYMENT_STATUS, ORDER_DETAIL_TYPE, DEBT_STATUS, PAYMENT_METHOD
from api.models.data import CrawlData, Order, Customer, OrderDetail, OrderHistory, OrderDetailHistory, AnnualOrder, \
    User, FBPage, FBUser, Payment, AnnualOrderHistory, ImportOrderRecords
from api.models.organization import UserRole
from api.models.system_configuration import DataStatus, DataSubStatus, DataChannel, DataSource
from api.serializers.data_serializer import ImportOrderDataRequestSerializer, CreateOrderRequestSerializer
from api.services import utils
from api.services.exceptions import OrderNotFound, OrderDuplicated, OrderDetailNotFound, OrderDetailDuplicated, \
    FBPageNotFound, FBUserNotExisted, PaymentNotFound, ImportRecordNotFound, PaymentForNoProductOrder
import api.services.validate_error_code as vec
import operator
import functools
import pytz

from api.utils.date import get_last_of_month
from api.utils.phone import extract_phone
from crm.settings import TIME_ZONE


def create_order_detail_history(order_detail):
    OrderDetailHistory.objects.create(company_id=order_detail.company_id, order_id=order_detail.order_id,
                                      order_detail_id=order_detail.id,
                                      type=order_detail.type, product_id=order_detail.product_id,
                                      quantity=order_detail.quantity, price=order_detail.price,
                                      annual_price=order_detail.annual_price,
                                      discount_value=order_detail.discount_value,
                                      discount_type=order_detail.discount_type,
                                      remaining_payment_amount=order_detail.remaining_payment_amount,
                                      paid_payment_amount=order_detail.paid_payment_amount,
                                      debt=order_detail.debt, due_date=order_detail.due_date,
                                      file_attach=order_detail.file_attach, invoice=order_detail.invoice,
                                      annual_paid_payment_amount=order_detail.annual_paid_payment_amount,
                                      annual_remaining_payment_amount=order_detail.annual_remaining_payment_amount,
                                      total_payment_amount=order_detail.total_payment_amount)


def create_order_history(order):
    OrderHistory.objects.create(order_id=order.id, created_date=order.created_date,
                                price=order.price, debt=order.debt, due_date=order.due_date,
                                annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                pic=order.pic, customer_id=order.customer_id, shipping_code=order.shipping_code,
                                shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                data_sub_status_id=order.data_sub_status_id, debt_status=order.debt_status,
                                data_source_id=order.data_source_id, data_channel_id=order.data_channel_id,
                                company_id=order.company_id, discount_type=order.discount_type,
                                discount_value=order.discount_value, amount=order.amount,
                                annual_amount=order.annual_amount, care_notes=order.care_notes,
                                duplicated_with=order.duplicated_with, confirmed_date=order.confirmed_date,
                                customer_name=order.customer_name, customer_address=order.customer_address,
                                customer_email=order.customer_email, created_by=order.created_by,
                                updated_by=order.updated_by)


def calculate_debt_status(order, today):
    if order.debt > 0 or order.annual_debt > 0:
        return DEBT_STATUS.UNPAID

    if order.waiting_approval_debt > 0 or order.waiting_approval_annual_debt:
        return DEBT_STATUS.UNAPPROVED

    if OrderDetail.objects.filter(order_id=order.id, due_date__lt=today,
                                  deleted_at__isnull=True):
        return DEBT_STATUS.NOTIFIED

    return DEBT_STATUS.APPROVED


def recalculate_order(order):
    annual_order_details = OrderDetail.objects.filter(order_id=order.id, type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
                                                      deleted_at__isnull=True).order_by('-id')
    order_details = OrderDetail.objects.filter(order_id=order.id, type=ORDER_DETAIL_TYPE.NEW_BUY,
                                               deleted_at__isnull=True).order_by('-id')

    order.annual_amount = 0
    order.annual_debt = 0
    order.amount = 0
    order.debt = 0
    today = datetime.now(timezone(TIME_ZONE)).date()
    for order_detail in annual_order_details:
        order.annual_amount += order_detail.total_payment_amount
        order.annual_debt += order_detail.debt

    for order_detail in order_details:
        order.amount += order_detail.total_payment_amount
        order.debt += order_detail.debt

    if annual_order_details:
        order.annual_due_date = annual_order_details.first().due_date

    if order_details:
        order.due_date = order_details.first().due_date

    waiting_approval_debt = Payment.objects.filter(order_id=order.id,
                                                   status=ORDER_PAYMENT_STATUS.WAITING_APPROVAL,
                                                   type=ORDER_DETAIL_TYPE.NEW_BUY,
                                                   deleted_at__isnull=True).aggregate(Sum('value'))['value__sum']
    order.waiting_approval_debt = 0 if waiting_approval_debt is None else waiting_approval_debt
    waiting_approval_annual_debt = Payment.objects.filter(order_id=order.id,
                                                          status=ORDER_PAYMENT_STATUS.WAITING_APPROVAL,
                                                          type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
                                                          deleted_at__isnull=True).aggregate(Sum('value'))['value__sum']
    order.waiting_approval_annual_debt = 0 if waiting_approval_annual_debt is None else waiting_approval_annual_debt

    order.debt_status = calculate_debt_status(order, today)
    order.save()


def recalculate_order_details_by_payment(order_detail):
    if order_detail.type == ORDER_DETAIL_TYPE.ANNUAL_BUY:
        payment_amount = Payment.objects.filter(order_detail_id=order_detail.id,
                                                type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
                                                deleted_at__isnull=True).exclude(
            status=ORDER_PAYMENT_STATUS.DISAPPROVED).aggregate(Sum('value'))['value__sum']
        payment_amount = 0 if payment_amount is None else payment_amount
        order_detail.debt = order_detail.total_payment_amount - payment_amount

        annual_order_history = AnnualOrderHistory.objects.filter(order_detail_id=order_detail.id).first()
        if annual_order_history:
            annual_order_history_query = AnnualOrderHistory.objects.filter(
                annual_order_id=annual_order_history.annual_order_id, deleted_at__isnull=True,
                id__lte=annual_order_history.id)

            paid_amount = Payment.objects.filter(
                order_detail_id__in=annual_order_history_query.values_list('order_detail_id', flat=True),
                type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
                deleted_at__isnull=True).exclude(
                status=ORDER_PAYMENT_STATUS.DISAPPROVED).aggregate(Sum('value'))['value__sum']
            paid_amount = 0 if paid_amount is None else paid_amount
            order_detail.annual_paid_payment_amount = paid_amount
            order_detail.annual_remaining_payment_amount = order_detail.price * order_detail.quantity - \
                                                           order_detail.discount_value - paid_amount
        order_detail.save()

    if order_detail.type == ORDER_DETAIL_TYPE.NEW_BUY:
        order_details = OrderDetail.objects.filter(
            order_id=order_detail.order_id,
            type=ORDER_DETAIL_TYPE.NEW_BUY,
            deleted_at__isnull=True
        )
        payment_value = Payment.objects.filter(order_id=order_detail.order_id, type=ORDER_DETAIL_TYPE.NEW_BUY,
                                               deleted_at__isnull=True).exclude(
            status=ORDER_PAYMENT_STATUS.DISAPPROVED).aggregate(Sum('value'))['value__sum']

        payment_value = 0 if payment_value is None else payment_value
        for order_detail in order_details:
            if payment_value == 0:
                break
            paid_amount = min(payment_value, order_detail.total_payment_amount)
            payment_value -= paid_amount
            order_detail.paid_payment_amount = paid_amount
            order_detail.remaining_payment_amount = order_detail.total_payment_amount - paid_amount
            order_detail.debt = order_detail.remaining_payment_amount
            order_detail.save()


class FilterCrawlDataService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = CrawlData.objects.all()

        filters = ['source', 'phone', 'status', ]
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if value is None:
                continue
            if key not in filters:
                continue

            if key == 'source':
                query_set = query_set.filter(
                    source=value,
                )
            if key == 'status':
                query_set = query_set.filter(
                    status=value,
                )
            if key == 'phone':
                query_set = query_set.filter(
                    phone__icontains=value,
                )

        return query_set


class GetCrawlDataService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)
            if 'order_id' in kwargs and kwargs['order_id'] is not None:
                order = Order.objects.get(pk=kwargs.get('order_id'))
                if order.crawl_data_id is not None:
                    return order.crawl_data
            return CrawlData.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except CrawlData.DoesNotExist as e:
            raise OrderNotFound()


class CreateOrderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            kwargs['created_by'] = request.user.username
            kwargs['updated_by'] = request.user.username

            order = Order.objects.create(
                **kwargs
            )
            if kwargs.get('data_status_id', None):
                if order.data_status.name.lower() == 'đã xác nhận':
                    order.confirmed_date = datetime.now(TIME_ZONE).date()
            if order.customer:
                duplicated = Order.objects.filter(deleted_at__isnull=True, customer_id=order.customer_id,
                                                  company_id=order.company_id).exclude(pk=order.id).order_by('-id')
                if duplicated.first():
                    order.duplicated_with = duplicated.first().id
            order.save()

            create_order_history(order)

            return order
        except IntegrityError as e:
            raise OrderDuplicated()


class GetOrderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return Order.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except Order.DoesNotExist as e:
            raise OrderNotFound()


class UpdateOrderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                order = Order.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                order = Order.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('created_date'):
                order.created_date = kwargs['created_date']

            if kwargs.get('price'):
                order.price = kwargs['price']

            if kwargs.get('debt'):
                order.debt = kwargs['debt']

            if kwargs.get('due_date'):
                order.due_date = kwargs['due_date']

            if kwargs.get('annual_debt'):
                order.annual_debt = kwargs['annual_debt']

            if kwargs.get('annual_due_date'):
                order.annual_due_date = kwargs['annual_due_date']

            if kwargs.get('pic_id'):
                order.pic_id = kwargs['pic_id']

            if kwargs.get('customer_id'):
                order.customer_id = kwargs['customer_id']

            if kwargs.get('shipping_code'):
                order.shipping_code = kwargs['shipping_code']

            if kwargs.get('shipping_fee'):
                order.shipping_fee = kwargs['shipping_fee']

            if kwargs.get('discount_value'):
                order.discount_value = kwargs['discount_value']

            if kwargs.get('discount_type'):
                order.discount_type = kwargs['discount_type']

            if kwargs.get('amount'):
                order.amount = kwargs['amount']

            if kwargs.get('annual_amount'):
                order.annual_amount = kwargs['annual_amount']

            if kwargs.get('data_status_id') and kwargs.get('data_status_id') != order.data_status_id:
                order.data_status_id = kwargs['data_status_id']
                if order.data_status.name.lower() == 'đã xác nhận':
                    order.confirmed_date = datetime.now(TIME_ZONE).date()

            if kwargs.get('data_sub_status_id'):
                order.data_sub_status_id = kwargs['data_sub_status_id']

            if kwargs.get('data_source_id'):
                order.data_source_id = kwargs['data_source_id']

            if kwargs.get('data_channel_id'):
                order.data_channel_id = kwargs['data_channel_id']

            if kwargs.get('care_notes'):
                order.care_notes = kwargs['care_notes']

            if kwargs.get('customer_name'):
                order.customer_name = kwargs['customer_name']

            if kwargs.get('customer_address'):
                order.customer_address = kwargs['customer_address']

            if kwargs.get('customer_email'):
                order.customer_email = kwargs['customer_email']

            order.updated_by = request.user.username
            order.save()

            create_order_history(order)

            return order
        except Order.DoesNotExist:
            raise OrderNotFound()


class FilterOrderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if request.user.is_superuser:
            query_set = Order.objects.filter(
                deleted_at__isnull=True
            )
        else:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            query_set = Order.objects.filter(
                company_id=user_roles.first().company_id,
                deleted_at__isnull=True
            )

        filters = ['id', 'from_date', 'to_date', 'pics', 'data_status', 'debt_status', 'data_source', 'phone',
                   'customer_name']
        params = dict(kwargs.get('filter', []))
        items = params.items()
        for key, value in items:
            if key not in filters:
                continue

            if key == 'id' and value is not None:
                query_set = query_set.filter(
                    id=value,
                )

            if key == 'from_date' and value is not None:
                query_set = query_set.filter(
                    created_date__gte=value.strftime('%Y-%m-%d'),
                )

            if key == 'to_date' and value is not None:
                query_set = query_set.filter(
                    created_date__lte=value.strftime('%Y-%m-%d'),
                )

            if key == 'confirmed_from_date' and value is not None:
                query_set = query_set.filter(
                    confirmed_date__gte=value.strftime('%Y-%m-%d'),
                )

            if key == 'confirmed_to_date' and value is not None:
                query_set = query_set.filter(
                    created_date__lte=value.strftime('%Y-%m-%d'),
                )

            if key == 'annual_due_date_from_date' and value is not None:
                query_set = query_set.filter(
                    annual_due_date__gte=value.strftime('%Y-%m-%d'),
                )

            if key == 'annual_due_date_to_date' and value is not None:
                query_set = query_set.filter(
                    annual_due_date__lte=value.strftime('%Y-%m-%d'),
                )

            if key == 'pics' and value is not None:
                if len(value) == 0:
                    query_set = query_set.filter(pic__isnull=True)
                else:
                    query_set = query_set.filter(
                        pic__in=value,
                    )

            if key == 'data_status' and value is not None and value:
                query = functools.reduce(
                    operator.or_,
                    (Q(data_status_id=data_status['data_status_id'],
                       data_sub_status_id=data_status['data_sub_status_id']) if 'data_sub_status_id' in data_status and
                                                                                data_status[
                                                                                    'data_sub_status_id'] is not None else Q(
                        data_status_id=data_status['data_status_id']) for data_status in value)
                )
                query_set = query_set.filter(query)

            if key == 'data_source' and value is not None and value:
                query = functools.reduce(
                    operator.or_,
                    (Q(data_source_id=data_source['data_source_id'],
                       data_channel_id=data_source['data_channel_id']) if 'data_channel_id' in data_source and
                                                                          data_source[
                                                                              'data_channel_id'] is not None else Q(
                        data_source_id=data_source['data_source_id']) for data_source in value)
                )
                query_set = query_set.filter(query)

            if key == 'phone' and value is not None:
                customers = Customer.objects.filter(phone__icontains=value)
                query_set = query_set.filter(customer_id__in=customers.values_list('id', flat=True))

            if key == 'customer_name' and value is not None:
                customers = Customer.objects.filter(name__icontains=value)
                query_set = query_set.filter(customer_id__in=customers.values_list('id', flat=True))

            if key == 'debt_status' and value is not None:
                query_set = query_set.filter(debt_status=value)

        return query_set.order_by('-created_at')


class DeleteOrderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return Order.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except Order.DoesNotExist as e:
            raise OrderNotFound()


class CreateOrderDetailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            order_detail = OrderDetail.objects.create(
                **kwargs
            )

            recalculate_order(order_detail.order)
            if order_detail.product.payment_method == PRODUCT_PAYMENT_METHOD.CREDIT:
                self.create_annual_buy(order_detail)

            create_order_detail_history(order_detail)

            return order_detail
        except IntegrityError as e:
            raise OrderDetailDuplicated()

    def create_annual_buy(self, order_detail):
        annual_order = AnnualOrder.objects.create(company_id=order_detail.company_id, order_detail_id=order_detail.id,
                                                  product_id=order_detail.product_id)

        AnnualOrderHistory.objects.create(annual_order_id=annual_order.id, order_detail_id=order_detail.id)


class GetOrderDetailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return OrderDetail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except OrderDetail.DoesNotExist as e:
            raise OrderDetailNotFound()


class FilterOrderDetailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = OrderDetail.objects.filter(company_id=user_roles.first().company_id)

        filters = ['order_id', 'type']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order_id' and value is not None:
                query_set = query_set.filter(
                    order_id=value,
                )

            if key == 'type' and value is not None:
                query_set = query_set.filter(
                    type=value,
                )

        return query_set.order_by('-id')


class UpdateOrderDetailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                order_detail = OrderDetail.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                order_detail = OrderDetail.objects.get(
                    pk=kwargs.get('order_detail_id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('product_id'):
                order_detail.product_id = kwargs['product_id']

            if kwargs.get('quantity'):
                order_detail.quantity = kwargs['quantity']

            if kwargs.get('price'):
                order_detail.price = kwargs['price']

            if kwargs.get('annual_price'):
                order_detail.annual_price = kwargs['annual_price']

            if kwargs.get('discount_value'):
                order_detail.discount_value = kwargs['discount_value']

            if kwargs.get('discount_type'):
                order_detail.discount_type = kwargs['discount_type']

            if kwargs.get('remaining_payment_amount'):
                order_detail.remaining_payment_amount = kwargs['remaining_payment_amount']

            if kwargs.get('paid_payment_amount'):
                order_detail.paid_payment_amount = kwargs['paid_payment_amount']

            if kwargs.get('debt'):
                order_detail.debt = kwargs['debt']

            if kwargs.get('due_date'):
                order_detail.due_date = kwargs['due_date']

            if kwargs.get('file_attach'):
                order_detail.file_attach = kwargs['file_attach']

            if kwargs.get('invoice'):
                order_detail.invoice = kwargs['invoice']

            if kwargs.get('annual_paid_payment_amount'):
                order_detail.annual_paid_payment_amount = kwargs['annual_paid_payment_amount']

            if kwargs.get('annual_remaining_payment_amount'):
                order_detail.annual_remaining_payment_amount = kwargs['annual_remaining_payment_amount']

            if kwargs.get('total_payment_amount'):
                order_detail.total_payment_amount = kwargs['total_payment_amount']

            order_detail.save()

            create_order_detail_history(order_detail)
            recalculate_order_details_by_payment(order_detail)
            recalculate_order(order_detail.order)

            return order_detail
        except OrderDetail.DoesNotExist:
            raise OrderDetailNotFound()


class DeleteOrderDetailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            order_detail = OrderDetail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            order_detail.delete()

            recalculate_order(order_detail.order)

            return order_detail
        except OrderDetail.DoesNotExist as e:
            raise OrderDetailNotFound()


class FilterOrderHistoryService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = OrderHistory.objects.filter(company_id=user_roles.first().company_id)

        filters = ['order_id']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order_id' and value is not None:
                query_set = query_set.filter(
                    order_id=value,
                )

        return query_set.order_by('-id')


class FilterOrderDetailHistoryService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = OrderDetailHistory.objects.filter(company_id=user_roles.first().company_id)

        filters = ['order_detail_id', 'order_id', 'type']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order_detail_id' and value is not None:
                query_set = query_set.filter(
                    order_detail_id=value,
                )

            if key == 'order_id' and value is not None:
                query_set = query_set.filter(
                    order_id=value,
                )

            if key == 'type' and value is not None:
                query_set = query_set.filter(
                    type=value,
                )

        return query_set.order_by('order_detail_id', '-created_at')


class BulkUpdateOrderStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            with transaction.atomic():
                order_id_list = kwargs.get('order_id_list')

                for order_id in order_id_list:
                    order = Order.objects.get(pk=order_id)
                    OrderHistory.objects.create(order_id=order.id, created_date=order.created_date,
                                                price=order.price, debt=order.debt, due_date=order.due_date,
                                                annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                                pic=order.pic, customer_id=order.customer_id,
                                                shipping_code=order.shipping_code,
                                                shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                                data_sub_status_id=order.data_sub_status_id,
                                                debt_status=order.debt_status,
                                                data_source_id=order.data_source_id,
                                                data_channel_id=order.data_channel_id,
                                                company_id=order.company_id)

                    order.data_status_id = kwargs.get('data_status_id')
                    order.data_sub_status_id = kwargs.get('data_sub_status_id')
                    order.save()

        except Order.DoesNotExist:
            raise OrderNotFound()


class BulkUpdateOrderPicService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            with transaction.atomic():
                order_id_list = kwargs.get('order_id_list')
                pic_list = kwargs.get('pic_list')
                number_order_per_pic = len(pic_list)

                for index, order_id in enumerate(order_id_list):
                    pic_index = index % number_order_per_pic
                    order = Order.objects.get(pk=order_id)
                    OrderHistory.objects.create(order_id=order.id, created_date=order.created_date,
                                                price=order.price, debt=order.debt, due_date=order.due_date,
                                                annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                                pic=order.pic, customer_id=order.customer_id,
                                                shipping_code=order.shipping_code,
                                                shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                                data_sub_status_id=order.data_sub_status_id,
                                                debt_status=order.debt_status,
                                                data_source_id=order.data_source_id,
                                                data_channel_id=order.data_channel_id,
                                                company_id=order.company_id)

                    order.pic = User.objects.get(pk=pic_list[pic_index])
                    order.save()

        except Order.DoesNotExist:
            raise OrderNotFound()


class FilterFBPageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if request.user.is_superuser:
            query_set = FBPage.objects.filter(
                deleted_at__isnull=True
            )
        else:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            query_set = FBPage.objects.filter(
                company_id=user_roles.first().company_id,
                deleted_at__isnull=True
            )

        filters = ['page_id_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'page_id_name' and value is not None:
                query_set = query_set.filter(
                    Q(page_id__icontains=value) | Q(page_name__icontains=value)
                )

        return query_set


class UpdateFBPageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            fb_page = FBPage.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id,
                deleted_at__isnull=True
            )

            if kwargs.get('is_subscribed', None) is not None:
                fb_page.is_subscribed = kwargs['is_subscribed']

            fb_page.save()

            return fb_page
        except FBPage.DoesNotExist as e:
            raise FBPageNotFound()


class DeleteFBPageService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return FBPage.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id,
                deleted_at__isnull=True
            ).update(deleted_at=datetime.now())

        except FBPage.DoesNotExist as e:
            raise FBPageNotFound()


class GetSynchronizedFBAccountService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            fb_user = FBUser.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True).order_by(
                '-id').first()

            if fb_user is None:
                raise FBUserNotExisted()
            return fb_user

        except FBUser.DoesNotExist as e:
            raise FBUserNotExisted()


class DeleteSynchronizedFBAccountService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }

        user_roles = UserRole.objects.filter(**filter)

        FBPage.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True).update(
            deleted_at=datetime.now())
        FBUser.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True).update(
            deleted_at=datetime.now())


class CreatePaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        with transaction.atomic():
            payment = Payment(
                **kwargs
            )

            payment.status = ORDER_PAYMENT_STATUS.WAITING_APPROVAL
            payment = Payment.objects.create(company_id=payment.company_id, order_id=payment.order_id, type=payment.type,
                                          value=payment.value, status=payment.status, sale_note=payment.sale_note,
                                          invoice_no=payment.invoice_no, order_detail=payment.order_detail,
                                          payment_method=payment.payment_method)

            if payment.type == ORDER_DETAIL_TYPE.NEW_BUY:
                order_details = OrderDetail.objects.filter(
                    order_id=payment.order.id,
                    type=ORDER_DETAIL_TYPE.NEW_BUY,
                    deleted_at__isnull=True
                )
                if order_details.first() is None:
                    raise PaymentForNoProductOrder()
                recalculate_order_details_by_payment(order_details.first())
            else:
                recalculate_order_details_by_payment(payment.order_detail)
            recalculate_order(payment.order)

            return payment


class GetPaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return Payment.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except Payment.DoesNotExist as e:
            raise PaymentNotFound()


class UpdatePaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                payment = Payment.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                payment = Payment.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('value'):
                payment.value = kwargs['value']

            if kwargs.get('invoice_no'):
                payment.invoice_no = kwargs['invoice_no']

            if kwargs.get('payment_method'):
                payment.payment_method = kwargs['payment_method']

            if kwargs.get('sale_note'):
                payment.sale_note = kwargs['sale_note']

            payment.save()
            if 'value' in kwargs:
                recalculate_order_details_by_payment(payment)
                recalculate_order(payment.order)

            return payment
        except Payment.DoesNotExist:
            raise PaymentNotFound()


class ApprovePaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                payment = Payment.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                payment = Payment.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            recalculate_order(payment.order)

            payment.status = ORDER_PAYMENT_STATUS.APPROVED
            payment.accountant_note = kwargs.get('accountant_note')
            payment.save()

            recalculate_order(Order.objects.get(pk=payment.order_id))

            return payment
        except Payment.DoesNotExist:
            raise PaymentNotFound()


class DisapprovePaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                payment = Payment.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                payment = Payment.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            recalculate_order_details_by_payment(payment)
            recalculate_order(payment.order)

            payment.status = ORDER_PAYMENT_STATUS.DISAPPROVED
            payment.accountant_note = kwargs.get('accountant_note')
            payment.save()

            return payment
        except Payment.DoesNotExist:
            raise PaymentNotFound()


class FilterPaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = Payment.objects.filter(company_id=user_roles.first().company_id)

        filters = ['order_id', 'type', 'status', 'order']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})
                query_set = query_set.filter(
                    order_id__in=orders.values_list('id', flat=True),
                )

            if key == 'order_id' and value is not None:
                query_set = query_set.filter(
                    order_id=value,
                )

            if key == 'type' and value is not None:
                query_set = query_set.filter(type=value)

            if key == 'status' and value is not None:
                query_set = query_set.filter(status=value)

        return query_set.order_by('-id')


class DeletePaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            payment = Payment.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
            payment.delete()
            recalculate_order_details_by_payment(payment)
            recalculate_order(payment.order)

            return payment

        except Payment.DoesNotExist as e:
            raise PaymentNotFound()


class ImportOrderDataService(BaseService):
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
            'order_id': '' if str(rows[1].value).strip() == '' else str(int(rows[1].value)).strip(),
            'phone': str(rows[2].value).strip(),
            'shipping_code': str(rows[3].value).strip(),
            'shipping_fee': '' if str(rows[4].value).strip() == '' else str(int(rows[4].value)),
            'amount': '' if str(rows[5].value).strip() == '' else str(int(rows[5].value)),
            'sale_note': str(rows[6].value).strip(),
        }

    def validate_data(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_id(data))
        error_codes.extend(self.validate_phone(data))
        error_codes.extend(self.validate_order_id(data, company_id))
        error_codes.extend(self.validate_payment_amount(data, company_id))
        return error_codes

    def validate_id(self, row):
        error_codes = []
        id_str = str(row['id']).strip()
        if id_str == '':
            error_codes.append(vec.IdIsEmpty.code)

        if not id_str.isnumeric():
            error_codes.append(vec.IdIsNotNumeric.code)

        return error_codes

    def validate_order_id(self, row, company_id):
        error_codes = []
        order_id = str(row['order_id']).strip()

        if order_id == '':
            error_codes.append(vec.OrderIdEmpty.code)
        else:
            if not order_id.isnumeric():
                error_codes.append(vec.OrderIdIsNotNumeric.code)
            else:
                if Order.objects.filter(pk=int(order_id), company_id=company_id).first() is None:
                    error_codes.append(vec.OrderNotFound.code)

        return error_codes

    def validate_phone(self, row):
        phone = str(row['phone']).strip()
        if phone == '':
            return []

        phone.replace(' ', '')
        phone.replace('.', '')
        phone.replace('+', '')
        path = r'([\+84|84|0]+(3|5|7|8|9|1[2|6|8|9]))+([0-9]{8})\b'

        if re.match(path, phone):
            return []

        return [vec.InvalidPhoneFormat.code]

    def validate_payment_amount(self, row, company_id):
        amount = str(row['amount']).strip()
        error_codes = []

        if amount == '':
            return []

        if not amount.isnumeric():
            error_codes.append(vec.AmountIsNotNumeric.code)

        if row['order_id'] != '' and int(amount) > 0:
            order = Order.objects.filter(pk=int(row['order_id']), company_id=company_id).first()
            if order is not None:
                order_details = OrderDetail.objects.filter(
                    order_id=order.id,
                    type=ORDER_DETAIL_TYPE.NEW_BUY,
                    deleted_at__isnull=True
                )
                if order_details.first() is None:
                    error_codes.append(vec.PaymentForNoProductOrder.code)
        return error_codes


class ImportOrderService(BaseService):
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
            'phone': str(rows[1].value).strip(),
            'name': str(rows[2].value).strip(),
            'data_source': str(rows[3].value).strip(),
            'data_channel': str(rows[4].value).strip(),
            'care_note': str(rows[5].value).strip(),
            'data_status': str(rows[6].value).strip(),
            'data_sub_status': str(rows[7].value).strip(),
            'email': str(rows[8].value).strip()
        }

    def validate_data(self, data, company_id):
        error_codes = []
        error_codes.extend(self.validate_id(data))
        error_codes.extend(self.validate_phone(data))
        error_codes.extend(self.validate_data_status(data, company_id))
        error_codes.extend(self.validate_data_source(data, company_id))
        error_codes.extend(self.validate_email(data))
        return error_codes

    def validate_id(self, row):
        error_codes = []
        id_str = str(row['id']).strip()
        if id_str == '':
            error_codes.append(vec.IdIsEmpty.code)

        if not id_str.isnumeric():
            error_codes.append(vec.IdIsNotNumeric.code)

        return error_codes

    def validate_phone(self, row):
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

    def validate_data_status(self, row, company_id):
        error_codes = []
        data_status = str(row['data_status']).strip()
        data_sub_status = str(row['data_sub_status']).strip()
        if data_status == '':
            if data_sub_status != '':
                error_codes.append(vec.DataStatusEmptyDataSubStatusNotEmpty.code)
        else:
            data_status = DataStatus.objects.filter(name__iexact=data_status).first()
            if data_status is None:
                error_codes.append(vec.DataStatusNotFound.code)

        if data_sub_status != '':
            data_sub_status = DataSubStatus.objects.filter(data_status_id=data_status.id, company_id=company_id,
                                                           name__iexact=data_sub_status)
            if data_sub_status is None:
                error_codes.append(vec.DataStatusNotFound.code)

        return error_codes

    def validate_data_source(self, row, company_id):
        error_codes = []
        data_source = str(row['data_source']).strip()
        data_channel = str(row['data_channel']).strip()
        if data_source == '':
            if data_channel != '':
                error_codes.append(vec.DataSourceEmptyDataChannelNotEmpty.code)

        else:
            data_source = DataSource.objects.filter(name__iexact=data_source).first()
            if data_source is None:
                error_codes.append(vec.DataSourceNotFound.code)

        if data_channel != '':
            data_channel = DataChannel.objects.filter(data_status_id=data_source.id, company_id=company_id,
                                                      name__iexact=data_channel)
            if data_channel is None:
                error_codes.append(vec.DataChannelNotFound.code)

        return error_codes

    def validate_email(self, row):
        error_codes = []
        email = str(row['email']).strip()
        if email == '':
            return error_codes

        pat = r'^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$'
        if re.match(pat, email):
            return error_codes
        return [vec.InvalidEmailFormat.code]


class ConfirmImportOrderService(ImportOrderService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        try:
            record = ImportOrderRecords.objects.get(
                pk=kwargs.get('id')
            )

            create_order_service = CreateOrderService()

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
                        customer = None
                        if data_record['phone'] != '':
                            customer = Customer.objects.filter(
                                phone=data_record['phone'], company_id=kwargs['company_id']).first()
                            if customer is None:
                                customer = Customer.objects.create(
                                    phone=data_record['phone'], company_id=kwargs['company_id'],
                                    name=data_record['name'], email=data_record['email'])
                            else:
                                if data_record['name'] != '' or data_record['email'] != '':
                                    customer.name = data_record['name'] if data_record['name'] != '' else customer.name
                                    customer.email = data_record['email'] if data_record[
                                                                                 'email'] != '' else customer.email
                                    customer.save()

                        data_source = DataSource.objects.filter(name=data_record['data_source']).first()
                        data_channel = DataChannel.objects.filter(name=data_record['data_channel']).first()
                        data_status = DataStatus.objects.filter(name=data_record['data_status']).first()
                        data_sub_status = DataSubStatus.objects.filter(name=data_record['data_sub_status']).first()
                        order = Order(customer_name=data_record['name'], data_source=data_source,
                                      data_channel=data_channel, data_status=data_status,
                                      data_sub_status=data_sub_status, care_notes=data_record['care_note'],
                                      customer_email=data_record['email'], customer=customer,
                                      company_id=kwargs['company_id'])
                        order.created_date = datetime.today().date()
                        create_order_service.serve(request, cookies, *args, **CreateOrderRequestSerializer(order).data)

        except ImportOrderRecords.DoesNotExist:
            raise ImportRecordNotFound


class ConfirmImportOrderDataService(ImportOrderDataService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        try:
            record = ImportOrderRecords.objects.get(
                pk=kwargs.get('id')
            )

            update_order_service = UpdateOrderService()

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
                        order_data = {'id': int(data_record['order_id'])}
                        order = Order.objects.filter(pk=int(data_record['order_id']),
                                                     company_id=kwargs['company_id']).first()

                        if data_record['phone'] != '':
                            order = Order.objects.filter(pk=int(data_record['order_id']),
                                                         company_id=kwargs['company_id']).first()
                            normalized_phone = data_record['phone']
                            if order.customer and order.customer.phone != normalized_phone:
                                customer = Customer.objects.create(phone=normalized_phone,
                                                                   company_id=kwargs['company_id'])
                                order_data['customer_id'] = customer.id

                        if data_record['shipping_code'] != '':
                            order_data['shipping_code'] = data_record['shipping_code']

                        if data_record['shipping_fee'] != '':
                            order_data['shipping_fee'] = int(data_record['shipping_fee'])

                        update_order_service.serve(request, cookies, *args, **order_data)

                        if data_record['amount'] != '' and int(data_record['amount']) > 0:
                            payment_service = CreatePaymentService()
                            payment = payment_service.serve(request, cookies, *args, **{
                                'company_id': kwargs['company_id'],
                                'order_id': order.id,
                                'type': ORDER_DETAIL_TYPE.NEW_BUY,
                                'value': int(data_record['amount']), 'sale_note': data_record['sale_note'],
                                'payment_method': PAYMENT_METHOD.TRANSFER
                            })
                            payment_service = ApprovePaymentService()
                            payment_service.serve(request, cookies, *args, **{
                                'id': payment.id,
                                'accountant_note': 'Import từ excel'
                            })

        except ImportOrderRecords.DoesNotExist:
            raise ImportRecordNotFound

