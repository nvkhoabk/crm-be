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


class FilterReportService(BaseService):
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

        filters = ['from_date', 'to_date', 'pics', 'data_status' 'debt_status', 'data_source', 'phone', 'customer_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'from_date' and value is not None:
                query_set = query_set.filter(
                    created_date__gte=value.strftime('%Y-%m-%d'),
                )

            if key == 'to_date' and value is not None:
                query_set = query_set.filter(
                    created_date__lte=value.strftime('%Y-%m-%d'),
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


class FilterAnnualOrderReportService(BaseService):
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

        filters = ['from_date', 'to_date', 'pics', 'data_status' 'debt_status', 'data_source', 'phone', 'customer_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'from_date' and value is not None:
                query_set = query_set.filter(
                    created_date__gte=value.strftime('%Y-%m-%d'),
                )

            if key == 'to_date' and value is not None:
                query_set = query_set.filter(
                    created_date__lte=value.strftime('%Y-%m-%d'),
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


class FilterBadDebtReportService(BaseService):
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

        filters = ['from_date', 'to_date', 'pics', 'data_status' 'debt_status', 'data_source', 'phone', 'customer_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'from_date' and value is not None:
                query_set = query_set.filter(
                    created_date__gte=value.strftime('%Y-%m-%d'),
                )

            if key == 'to_date' and value is not None:
                query_set = query_set.filter(
                    created_date__lte=value.strftime('%Y-%m-%d'),
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