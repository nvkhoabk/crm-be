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
from api.services.data import FilterOrderService
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



        filters = ['order', 'order_by']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **kwargs['order'])

            if key == 'order_by' and value is not None:
                query_set = query_set.order_by()

        return [
            {'pic': 'Nhân viên A',
             'total_order': 1000,
             'total_confirmed_order': 800,
             'conversion_rate': 80,
             'turnover': 20000000,
             'debt': 0,
             'waiting_approved_debt': 10000000,
             'average_confirmed_time': 100000,
             'top': 1
             },
            {
                'pic': 'Nhân viên B',
                'total_order': 1000,
                'total_confirmed_order': 800,
                'conversion_rate': 80,
                'turnover': 20000000,
                'debt': 0,
                'waiting_approved_debt': 10000000,
                'average_confirmed_time': 100000,
                'top': 2
            }
        ]


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



        filters = ['order', 'order_by']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **kwargs['order'])

            if key == 'order_by' and value is not None:
                query_set = query_set.order_by()

        return [
            {"pic": "Nhân viên A",
             "total_order": 100,
             "total_debt": 10000000,
             "paid_amount": 500000,
             "remaining_debt": 10000000 - 500000,
             "waiting_approved_remaining_debt": 10000000,
             'top': 1
             },
            {
                "pic": "Nhân viên B",
                "total_order": 200,
                "total_debt": 20000000,
                "paid_amount": 1000000,
                "remaining_debt": 20000000 - 1000000,
                "waiting_approved_remaining_debt": 20000000,
                'top': 2
            }
        ]


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



        filters = ['order', 'order_by']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **kwargs['order'])

            if key == 'order_by' and value is not None:
                query_set = query_set.order_by()

        return [{"pic": "Nhân viên A",
                 "total_order": 100,
                 "total_debt": 10000000,
                 "paid_amount": 500000,
                 "remaining_debt": 10000000 - 500000,
                 "waiting_approved_remaining_debt": 10000000,
                 'top': 1
                 },
                {
                    "pic": "Nhân viên B",
                    "total_order": 200,
                    "total_debt": 20000000,
                    "paid_amount": 1000000,
                    "remaining_debt": 20000000 - 1000000,
                    "waiting_approved_remaining_debt": 20000000,
                    'top': 1
                }]
