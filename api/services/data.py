import json
import math
from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.utils import timezone

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import PRODUCT_PAYMENT_METHOD, ORDER_PAYMENT_STATUS, ORDER_DETAIL_TYPE, DEBT_STATUS
from api.models.data import CrawlData, Order, Customer, OrderDetail, OrderHistory, OrderDetailHistory, AnnualOrder, \
    User, FBPage, FBUser, Payment
from api.models.organization import UserRole
from api.services import utils
from api.services.exceptions import OrderNotFound, OrderDuplicated, OrderDetailNotFound, OrderDetailDuplicated, \
    FBPageNotFound, FBUserNotExisted, PaymentNotFound
import operator
import functools
import pytz

from api.utils.date import get_last_of_month
from crm.settings import TIME_ZONE


def create_annual_order(order_detail):
    AnnualOrder.objects.create(company_id=order.company_id, order_id=order.id)


def recalculate_order(order):
    annual_order_details = OrderDetail.objects.filter(order_id=order.id, type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
                                                      deleted_at__isnull=True).order_by('-id')
    order_details = OrderDetail.objects.filter(order_id=order.id, type=ORDER_DETAIL_TYPE.NEW_BUY,
                                               deleted_at__isnull=True).order_by('-id')

    order.annual_amount = 0
    order.annual_debt = 0
    order.amount = 0
    order.debt = 0
    for order_detail in annual_order_details:
        order.annual_amount += order_detail.remaining_payment_amount
        order.annual_debt += order_detail.debt

    for order_detail in order_details:
        order.amount += order_detail.remaining_payment_amount
        order.debt += order_detail.debt

    if annual_order_details:
        order.annual_due_date = annual_order_details.first().due_date

    if order_details:
        order.due_date = order_details[0].due_date

    if order.debt > 0 or order.annual_debt > 0:
        waiting_approval_payment_value = Payment.objects.filter(order_id=order.id,
                                                                status=ORDER_PAYMENT_STATUS.WAITING_APPROVAL,
                                                                deleted_at__isnull=True).aggregate(Sum('value'))
        if waiting_approval_payment_value == (order.debt + order.annual_debt):
            order.debt_status = DEBT_STATUS.UNAPPROVED
        else:
            order.debt_status = DEBT_STATUS.UNPAID
    else:
        order.debt_status = DEBT_STATUS.APPROVED

    order.save()


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
            order = Order.objects.create(
                **kwargs
            )

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
                                        duplicated_with=order.duplicated_with, confirmed_date=order.confirmed_date)

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

            if kwargs.get('pic'):
                order.pic = kwargs['pic']

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

            if kwargs.get('data_status_id'):
                order.data_status_id = kwargs['data_status_id']

            if kwargs.get('data_sub_status_id'):
                order.data_sub_status_id = kwargs['data_sub_status_id']

            if kwargs.get('data_source_id'):
                order.data_source_id = kwargs['data_source_id']

            if kwargs.get('data_channel_id'):
                order.data_channel_id = kwargs['data_channel_id']

            if kwargs.get('care_notes'):
                order.care_notes = kwargs['care_notes']

            order.save()

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
                                        duplicated_with=order.duplicated_with, confirmed_date=order.confirmed_date)

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

        filters = ['id', 'from_date', 'to_date', 'pics', 'data_status' 'debt_status', 'data_source', 'phone',
                   'customer_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
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

            if key == 'pics' and value is not None and value:
                query_set = query_set.filter(
                    pic__in=value,
                )

            if key == 'data_status' and value is not None and value:
                query = functools.reduce(
                    operator.or_,
                    (Q(data_status_id=ds, data_sub_status_id=dss) if dss is not None else Q(data_status_id=ds) for
                     ds, dss in value)
                )
                query_set = query_set.filter(query)

            if key == 'data_source' and value is not None and value:
                query = functools.reduce(
                    operator.or_,
                    (Q(data_source_id=ds, data_channel_id=dc) if dc is not None else Q(data_source_id=ds) for ds, dc in
                     value)
                )
                query_set = query_set.filter(query)

            if key == 'phone' and value is not None:
                customers = Customer.objects.filter(phone__icontains=value)
                query_set = query_set.filter(customer_id__in=customers.values_list('id', flat=True))

            if key == 'customer_name' and value is not None:
                customers = Customer.objects.filter(name__icontains=value)
                query_set = query_set.filter(customer_id__in=customers.values_list('id', flat=True))

            if key == 'debt_status' and value is not None:
                query_set = query_set.query.filter(debt_status=value)

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

            OrderDetailHistory.objects.create(order_id=order_detail.order_id, order_detail_id=order_detail.id,
                                              type=order_detail.type, product_id=order_detail.product_id,
                                              quantity=order_detail.quantity, price=order_detail.price,
                                              annual_price=order_detail.annual_price,
                                              discount_type=order_detail.discount_type,
                                              discount_value=order_detail.discount_value,
                                              remaining_payment_amount=order_detail.remaining_payment_amount,
                                              total_payment_amount=order_detail.total_payment_amount,
                                              paid_payment_amount=order_detail.paid_payment_amount,
                                              debt=order_detail.debt, due_date=order_detail.due_date,
                                              file_attach=order_detail.file_attach, invoice=order_detail.invoice,
                                              company_id=order_detail.company_id)

            return order_detail
        except IntegrityError as e:
            raise OrderDetailDuplicated()

    def create_annual_buy(self, order_detail):
        current_date = datetime.now(pytz.timezone(TIME_ZONE)).date()
        if get_last_of_month(current_date).day < order_detail.product.date_in_month_payment:
            current_date = get_last_of_month(current_date)
        else:
            current_date.replace(day=order_detail.product.date_in_month_payment)

        order_detail.due_date = current_date

        return order_detail


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
                order_detail.price = kwargs['annual_price']

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

            order_detail.save()
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
                                              file_attach=order_detail.file_attach, invoice=order_detail.invoice)

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
                number_order_per_pic = math.floor(len(order_id_list) / len(pic_list)) + 1

                for index, order_id in enumerate(order_id_list):
                    pic_index = math.floor(index / number_order_per_pic)
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
            ).update(deleted_at=timezone.now())

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
            deleted_at=timezone.now())
        FBUser.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True).update(
            deleted_at=timezone.now())


class CreatePaymentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            user_roles = UserRole.objects.filter(user_id=request.user)

            if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                raise PermissionDenied()

        payment = Payment(
            **kwargs
        )

        payment.status = ORDER_PAYMENT_STATUS.WAITING_APPROVAL
        return Payment.objects.create(company_id=payment.company_id, order_id=payment.order_id, type=payment.type,
                                      value=payment.value, status=payment.status, sale_note=payment.sale_note,
                                      invoice_no=payment.invoice_no, order_detail=payment.order_detail,
                                      payment_method=payment.payment_method)


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

            if payment.type == ORDER_DETAIL_TYPE.ANNUAL_BUY:
                order_detail = OrderDetail.objects.get(
                    pk=payment.order_detail.id,
                )
                order_detail.paid_payment_amount = order_detail.paid_payment_amount + payment.value
                order_detail.remaining_payment_amount = order_detail.remaining_payment_amount - payment.value
                order_detail.debt = order_detail.annual_price - \
                                    order_detail.discount_value - order_detail.paid_payment_amount
                order_detail.save()

            if payment.type == ORDER_DETAIL_TYPE.NEW_BUY:
                order_details = OrderDetail.objects.filter(
                    order_id=payment.order_id,
                    type=ORDER_DETAIL_TYPE.NEW_BUY,
                    deleted_at__isnull=True
                )
                payment_value = payment.value
                for order_detail in order_details:
                    if payment_value == 0:
                        break
                    paid_amount = min(payment_value, order_detail.remaining_payment_amount)
                    payment_value -= paid_amount
                    order_detail.paid_payment_amount = order_detail.paid_payment_amount + paid_amount
                    order_detail.remaining_payment_amount = order_detail.remaining_payment_amount - paid_amount
                    order_detail.debt = order_detail.total_payment_amount - \
                                        order_detail.discount_value - order_detail.paid_payment_amount
                    order_detail.save()

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
            if payment.status == ORDER_PAYMENT_STATUS.APPROVED and payment.type == ORDER_DETAIL_TYPE.ANNUAL_BUY:
                order_detail = OrderDetail.objects.get(
                    pk=payment.order_detail.id,
                )
                order_detail.paid_payment_amount = order_detail.paid_payment_amount - payment.value
                order_detail.remaining_payment_amount = order_detail.remaining_payment_amount - payment.value
                order_detail.debt = order_detail.annual_price - \
                                    order_detail.discount_value - order_detail.paid_payment_amount
                order_detail.save()

            if payment.status == ORDER_PAYMENT_STATUS.APPROVED and payment.type == ORDER_DETAIL_TYPE.NEW_BUY:
                order_detail = OrderDetail.objects.get(
                    pk=payment.order_detail.id,
                )
                order_detail.paid_payment_amount = order_detail.paid_payment_amount - payment.value
                order_detail.remaining_payment_amount = order_detail.remaining_payment_amount - payment.value
                order_detail.debt = order_detail.remaining_payment_amount - \
                                    order_detail.discount_value - order_detail.paid_payment_amount
                order_detail.save()

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
                orders = order_service.serve(request, cookies, *args, **value)
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

            return Payment.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except Payment.DoesNotExist as e:
            raise PaymentNotFound()
