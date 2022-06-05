import json

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.data import CrawlData, Order, Customer, OrderDetail, OrderHistory, OrderDetailHistory
from api.models.organization import UserRole
from api.services import utils
from api.services.exceptions import OrderNotFound, OrderDuplicated, OrderDetailNotFound, OrderDetailDuplicated
import operator
import functools


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

            return Order.objects.create(
                **kwargs
            )
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
                order.email = kwargs['created_date']

            if kwargs.get('product_id'):
                order.email = kwargs['product_id']

            if kwargs.get('price'):
                order.email = kwargs['price']

            if kwargs.get('debt'):
                order.email = kwargs['debt']

            if kwargs.get('due_date'):
                order.email = kwargs['due_date']

            if kwargs.get('annual_debt'):
                order.email = kwargs['annual_debt']

            if kwargs.get('annual_due_date'):
                order.email = kwargs['annual_due_date']

            if kwargs.get('pic'):
                order.email = kwargs['pic']

            if kwargs.get('customer_id'):
                order.email = kwargs['customer_id']

            if kwargs.get('shipping_code'):
                order.email = kwargs['shipping_code']

            if kwargs.get('shipping_fee'):
                order.email = kwargs['shipping_fee']

            order.save()

            return order
        except Order.DoesNotExist:
            raise OrderNotFound()


class FilterOrderService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = Order.objects.filter(company_id=user_roles.first().company_id)

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

            return OrderDetail.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise OrderDetailDuplicated()


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


            OrderDetail.save()

            return OrderDetail
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

        return query_set


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

        return query_set