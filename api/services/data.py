import json
import math
from datetime import datetime

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import PRODUCT_PAYMENT_METHOD
from api.models.data import CrawlData, Order, Customer, OrderDetail, OrderHistory, OrderDetailHistory, AnnualOrder
from api.models.organization import UserRole
from api.services import utils
from api.services.exceptions import OrderNotFound, OrderDuplicated, OrderDetailNotFound, OrderDetailDuplicated
import operator
import functools
import pytz

from api.utils.date import get_last_of_month
from crm.settings import TIME_ZONE


def create_annual_order(order):
    if order.product is not None and order.product.payment_method == PRODUCT_PAYMENT_METHOD.CREDIT:
        AnnualOrder.objects.create(order_id=order.id)


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

            OrderHistory.objects.create(order_id=order.id, created_date=order.created_date, product_id=order.product_id,
                                        price=order.price, debt=order.debt, due_date=order.due_date,
                                        annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                        pic=order.pic, customer_id=order.customer_id, shipping_code=order.shipping_code,
                                        shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                        data_sub_status_id=order.data_sub_status_id, debt_status=order.debt_status,
                                        data_source_id=order.data_source_id, data_channel_id=order.data_channel_id)

            if order.product is not None and order.product.payment_method == PRODUCT_PAYMENT_METHOD.CREDIT:
                create_annual_order(order)

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

            if kwargs.get('product_id'):
                order.product_id = kwargs['product_id']
                self.change_product(order)

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

            order.save()

            OrderHistory.objects.create(order_id=order.id, created_date=order.created_date, product_id=order.product_id,
                                        price=order.price, debt=order.debt, due_date=order.due_date,
                                        annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                        pic=order.pic, customer_id=order.customer_id, shipping_code=order.shipping_code,
                                        shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                        data_sub_status_id=order.data_sub_status_id, debt_status=order.debt_status,
                                        data_source_id=order.data_source_id, data_channel_id=order.data_channel_id)

            return order
        except Order.DoesNotExist:
            raise OrderNotFound()

    def change_product(self, order):
        AnnualOrder.objects.filter(order_id=order.id, deleted_at__isnull=True, is_active=True).update(
            deleted_at=timezone.now())

        create_annual_order(order)


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

            query_set = Order.objects.get(
                company_id=user_roles.first().company_id,
                deleted_at__isnull=True
            )

        filters = ['from_date', 'to_date', 'pics', 'data_status' 'debt_status', 'data_source', 'phone', 'customer_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'from_date' and value is not None:
                query_set = query_set.filter(
                    created_date__gte=value,
                )

            if key == 'to_date' and value is not None:
                query_set = query_set.filter(
                    created_date__lte=value,
                )

            if key == 'pics' and value is not None:
                query_set = query_set.filter(
                    pic__in=value,
                )

            if key == 'data_status' and value is not None:
                query = functools.reduce(
                    operator.or_,
                    (Q(data_status_id=ds, data_sub_status_id=dss) for ds, dss in value)
                )
                query_set = query_set.filter(query)

            if key == 'data_source' and value is not None:
                query = functools.reduce(
                    operator.or_,
                    (Q(data_source_id=ds, data_channel_id=dc) for ds, dc in value)
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

        return query_set


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

            order_detail = self.update_order(request, cookies, *args, order_detail)

            OrderDetailHistory.objects.create(order_id=order_detail.order_id, order_detail_id=order_detail.id,
                                              type=order_detail.type, product_id=order_detail.product_id,
                                              quantity=order_detail.quantity, price=order_detail.price,
                                              discount=order_detail.discount,
                                              remaining_payment_amount=order_detail.remaining_payment_amount,
                                              paid_payment_amount=order_detail.paid_payment_amount,
                                              debt=order_detail.debt, due_date=order_detail.due_date,
                                              file_attach=order_detail.file_attach, invoice=order_detail.invoice)

            return order_detail
        except IntegrityError as e:
            raise OrderDetailDuplicated()

    def update_order(self, request, cookies: Cookies, *args, order_detail):
        order = Order.objects.get(pk=order_detail.order_id)

        if order_detail.product is not None and order_detail.product.payment_method == PRODUCT_PAYMENT_METHOD.CREDIT:
            order_detail = self.create_annual_buy(order_detail)

            order.annual_debt += order_detail.debt
            order.annual_due_date = order_detail.due_date
        else:
            order.debt += order_detail.debt
            order.due_date = order_detail.due_date

        order_service = UpdateOrderService()
        order_service.serve(request, cookies, *args, **order)

        return order_detail

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

        return query_set


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
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )


            if kwargs.get('product_id'):
                order_detail.order_id = kwargs['product_id']

            if kwargs.get('quantity'):
                order_detail.order_id = kwargs['quantity']

            if kwargs.get('price'):
                order_detail.order_id = kwargs['price']

            if kwargs.get('discount'):
                order_detail.order_id = kwargs['discount']

            if kwargs.get('remaining_payment_amount'):
                order_detail.order_id = kwargs['remaining_payment_amount']

            if kwargs.get('paid_payment_amount'):
                order_detail.order_id = kwargs['paid_payment_amount']

            if kwargs.get('debt'):
                order_detail.order_id = kwargs['debt']

            if kwargs.get('due_date'):
                order_detail.order_id = kwargs['due_date']

            if kwargs.get('file_attach'):
                order_detail.order_id = kwargs['file_attach']

            if kwargs.get('invoice'):
                order_detail.order_id = kwargs['invoice']


            order_detail.save()
            OrderDetailHistory.objects.create(order_id=order_detail.order_id, order_detail_id=order_detail.id,
                                              type=order_detail.type, product_id=order_detail.product_id,
                                              quantity=order_detail.quantity, price=order_detail.price,
                                              discount=order_detail.discount,
                                              remaining_payment_amount=order_detail.remaining_payment_amount,
                                              paid_payment_amount=order_detail.paid_payment_amount,
                                              debt=order_detail.debt, due_date=order_detail.due_date,
                                              file_attach=order_detail.file_attach, invoice=order_detail.invoice)

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

            return OrderDetail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
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
                                                product_id=order.product_id,
                                                price=order.price, debt=order.debt, due_date=order.due_date,
                                                annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                                pic=order.pic, customer_id=order.customer_id,
                                                shipping_code=order.shipping_code,
                                                shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                                data_sub_status_id=order.data_sub_status_id,
                                                debt_status=order.debt_status,
                                                data_source_id=order.data_source_id,
                                                data_channel_id=order.data_channel_id)

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
                                                product_id=order.product_id,
                                                price=order.price, debt=order.debt, due_date=order.due_date,
                                                annual_debt=order.annual_debt, annual_due_date=order.annual_due_date,
                                                pic=order.pic, customer_id=order.customer_id,
                                                shipping_code=order.shipping_code,
                                                shipping_fee=order.shipping_fee, data_status_id=order.data_status_id,
                                                data_sub_status_id=order.data_sub_status_id,
                                                debt_status=order.debt_status,
                                                data_source_id=order.data_source_id,
                                                data_channel_id=order.data_channel_id)

                    order.pic = pic_list[pic_index]
                    order.save()

        except Order.DoesNotExist:
            raise OrderNotFound()