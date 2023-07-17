import logging
from datetime import datetime, timedelta

import json
from logging.handlers import RotatingFileHandler

from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, ExpressionWrapper, F, fields

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import ORDER_PAYMENT_STATUS, ORDER_DETAIL_TYPE
from api.models.data import OrderDetail, Payment, Order
from api.models.organization import UserRole
from api.models.system_configuration import DataStatus, DataSubStatus
from api.services.data import FilterOrderService

from api.services.manage import FilterSaleUserService
from crm.settings import LOG_ROOT, LOG_LEVEL


class FilterReportService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        filters = ['order', 'order_by']
        params = dict(kwargs.get('filter', []))
        orders = []
        sales = []
        need_report_null_pic = False
        order_details = []

        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})
                data_status = DataStatus.objects.filter(company_id=user_roles.first().company_id, name__iexact='Đã hủy',
                                                        deleted_at__isnull=True).first()
                if value.get('pics', None) is not None:
                    user_service = FilterSaleUserService()
                    sales = user_service.serve(request, cookies, *args, **kwargs)
                    sales = sales.filter(id__in=value.get('pics'))
                    if None in value.get('pics'):
                        need_report_null_pic = True

                if data_status:
                    orders = orders.exclude(data_status_id=data_status.id)

                order_details = self.collect_order_details(orders, value['payment_from_date'],
                                                           value['payment_to_date'])

        report = dict()

        order_total_map = self.get_order_total_map(orders)
        orders = orders.filter(due_date__isnull=False)
        amount_map = self.get_amount_map(order_details, orders)
        confirmed_order_map = self.get_confirmed_order_map(orders)
        report_null_pic = self.calculate_report(sales, report, order_total_map, amount_map, confirmed_order_map, need_report_null_pic)

        reports = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            reports.sort(key=lambda r: r['actual_amount'], reverse=True)
            for index, report in enumerate(reports):
                report['top'] = index + 1
        else:
            reports.sort(key=lambda r: r['actual_amount'], reverse=False)
            for index, report in enumerate(reports[::-1]):
                report['top'] = index + 1

        if need_report_null_pic:
            reports.append(report_null_pic)

        return reports

    def collect_order_details(self, orders, payment_from_date, payment_to_date):
        order_details = OrderDetail.objects.filter(order__in=orders, deleted_at__isnull=True,
                                                   type=ORDER_DETAIL_TYPE.NEW_BUY)

        if payment_from_date and payment_to_date:
            order_details = order_details.filter(payment_date__gte=payment_from_date,
                                                 payment_date__lte=payment_to_date)
        return order_details

    def get_order_total_map(self, orders):
        order_total_map = orders.values('pic__username').order_by('pic_id').annotate(
                total=Count('*'))
        order_total_map = {order_total['pic__username']: order_total['total'] for order_total in order_total_map}
        return order_total_map

    def get_amount_map(self, order_details, orders):
        if len(order_details) == 0:
            return dict()

        order_details = order_details.filter(order__in=orders)
        amount_map = order_details.values('order__pic__username').order_by(
            'order__pic__username').annotate(total_debt=Sum('debt'), total_amount=Sum('total_payment_amount'),
                                             total_waiting_approval_debt=Sum('waiting_approval_debt'),
                                             total_price=Sum('price'))

        return {amount['order__pic__username']: amount for amount in amount_map}

    def get_confirmed_order_map(self, orders):
        orders = orders.filter(data_status__isnull=False).filter(data_status__name__iexact='đã xác nhận')
        confirmed_date = ExpressionWrapper(F('confirmed_date') + timedelta(days=1) - F('created_date'),
                                           output_field=fields.DurationField())

        orders = orders.values('pic__username').order_by(
            'pic__username')

        confirmed_order_map = orders.annotate(total_confirmed=Count('*'), total_confirmed_time=Sum(confirmed_date))
        return {order['pic__username']: order for order in confirmed_order_map}

    def get_report_total_order(self, sale_name, order_total_map):
        if sale_name not in order_total_map:
            return 0
        return order_total_map[sale_name]

    def get_report_total_confirmed_order(self, sale_name, confirmed_order_map):
        if sale_name not in confirmed_order_map:
            return 0
        return confirmed_order_map[sale_name]['total_confirmed']

    def get_report_conversion_rate(self, sale_name, order_total_map, confirmed_order_map):
        if sale_name not in order_total_map or order_total_map[sale_name] == 0 or sale_name not in confirmed_order_map:
            return 0

        return confirmed_order_map[sale_name]['total_confirmed'] / order_total_map[sale_name]

    def get_report_turnover(self, sale_name, amount_map):
        if sale_name not in amount_map:
            return 0

        return amount_map[sale_name]['total_amount']

    def get_report_debt(self, sale_name, amount_map):
        if sale_name not in amount_map:
            return 0

        return amount_map[sale_name]['total_debt']

    def get_report_waiting_approved_debt(self, sale_name, amount_map):
        if sale_name not in amount_map:
            return 0

        return amount_map[sale_name]['total_waiting_approval_debt']

    def get_report_total_confirmed_time(self, sale_name, confirmed_order_map):
        if sale_name not in confirmed_order_map:
            return 0

        return confirmed_order_map[sale_name]['total_confirmed_time'].days

    def get_report_average_confirmed_time(self, sale_name, confirmed_order_map):
        if sale_name not in confirmed_order_map or confirmed_order_map[sale_name]['total_confirmed'] == 0:
            return 0

        return confirmed_order_map[sale_name]['total_confirmed_time'].days / confirmed_order_map[sale_name][
            'total_confirmed']

    def get_report_actual_amount(self, sale_name, amount_map):
        if sale_name not in amount_map:
            return 0

        return amount_map[sale_name]['total_amount'] - amount_map[sale_name]['total_debt']

    def get_report_total_price(self, sale_name, amount_map):
        if sale_name not in amount_map:
            return 0

        return amount_map[sale_name]['total_price']

    def calculate_report(self, sales, report, order_total_map, amount_map, confirmed_order_map, need_report_null_pic):
        for sale in sales:
            if sale.username in report:
                continue
            report[sale.username] = {
                'pic': sale.username,
                'total_order': self.get_report_total_order(sale.username, order_total_map),
                'total_confirmed_order': self.get_report_total_confirmed_order(sale.username, confirmed_order_map),
                'conversion_rate': self.get_report_conversion_rate(sale.username, order_total_map, confirmed_order_map),
                'turnover': self.get_report_turnover(sale.username, amount_map),
                'debt': self.get_report_debt(sale.username, amount_map),
                'waiting_approved_debt': self.get_report_waiting_approved_debt(sale.username, amount_map),
                'total_confirmed_time': self.get_report_total_confirmed_time(sale.username, confirmed_order_map),
                'average_confirmed_time': self.get_report_average_confirmed_time(sale.username, confirmed_order_map),
                'actual_amount': self.get_report_actual_amount(sale.username, amount_map),
                'total_price': self.get_report_total_price(sale.username, amount_map),
                'top': 0
            }

        if need_report_null_pic:
            return {
                'pic': 'Chưa chia data',
                'total_order': self.get_report_total_order(None, order_total_map),
                'total_confirmed_order': self.get_report_total_confirmed_order(None, confirmed_order_map),
                'conversion_rate': self.get_report_conversion_rate(None, order_total_map, confirmed_order_map),
                'turnover': self.get_report_turnover(None, amount_map),
                'debt': self.get_report_debt(None, amount_map),
                'waiting_approved_debt': self.get_report_waiting_approved_debt(None, amount_map),
                'total_confirmed_time': self.get_report_total_confirmed_time(None, confirmed_order_map),
                'average_confirmed_time': self.get_report_average_confirmed_time(None, confirmed_order_map),
                'actual_amount': self.get_report_actual_amount(None, amount_map),
                'total_price': self.get_report_total_price(None, amount_map),
                'top': 0
            }

        return None


class FilterAnnualOrderReportService(BaseService):
    def __init__(self):
        self.logger = None

    def initializer_logger(self):
        logging.basicConfig(handlers=[RotatingFileHandler(filename=LOG_ROOT + 'crm.report.log',
                                                          maxBytes=512000, backupCount=4)], level=LOG_LEVEL,
                            format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        self.logger = logging.getLogger(__name__)

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        self.initializer_logger()

        user_roles = UserRole.objects.filter(**filter)
        orders = []
        sales = []
        filters = ['order']
        params = dict(kwargs.get('filter', []))
        order_detail_map = dict()
        need_report_null_pic = False
        report_null_pic = {
            'pic': 'Chưa chia data',
            'total_order': 0,
            'total_debt': 0,
            'paid_amount': 0,
            'remaining_debt': 0,
            'waiting_approved_remaining_debt': 0,
            'total_price': 0,
            'top': 0
        }

        self.logger.info('Start process annual report')
        self.logger.info('Start collect orders')
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})
                orders = orders.filter(annual_due_date__isnull=False, data_status__isnull=False,
                                       data_status__name__iexact='đã xác nhận')

                if value.get('pics', None) is not None:
                    user_service = FilterSaleUserService()
                    sales = user_service.serve(request, cookies, *args, **kwargs)
                    sales = sales.filter(id__in=value.get('pics'))
                    if None in value.get('pics'):
                        need_report_null_pic = True

                order_detail_map = self.get_order_detail_map(orders, value['payment_from_date'], value['payment_to_date'])

        report = dict()
        self.initialize_report(sales, report)

        self.logger.info('Complete collect orders')
        self.logger.info('Start calculate report')
        self.logger.info('Total orders: ' + str(len(orders)))

        for order in orders:
            if order.pic and order.pic.username in report and order.annual_due_date:
                report[order.pic.username]['total_order'] += 1
                if order.annual_due_date:
                    report[order.pic.username] = self.calculate_report_record(report, order, order_detail_map)
            if order.pic is None and need_report_null_pic and order.id in order_detail_map:
                annual_amount = order_detail_map[order.id]['total_amount']
                annual_debt = order_detail_map[order.id]['total_debt']
                waiting_approval_annual_debt = order_detail_map[order.id]['total_waiting_approval_debt']
                total_price = order_detail_map[order.id]['total_price']

                report_null_pic = {
                    'pic': report_null_pic['pic'],
                    'total_order': report_null_pic['total_order'] + 1,
                    'total_debt': report_null_pic['total_debt'] + annual_amount,
                    'paid_amount': report_null_pic['paid_amount'] + annual_amount - annual_debt,
                    'remaining_debt': report_null_pic['remaining_debt'] + annual_debt,
                    'waiting_approved_remaining_debt': report_null_pic[
                                                           'waiting_approved_remaining_debt'] + waiting_approval_annual_debt,
                    'total_price': total_price,
                    'top': 0
                }

        self.logger.info('Complete calculate report')

        reports = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            reports.sort(key=lambda r: r['paid_amount'], reverse=True)
            for index, report in enumerate(reports):
                report['top'] = index + 1
        else:
            reports.sort(key=lambda r: r['paid_amount'], reverse=False)
            for index, report in enumerate(reports.reverse()):
                report['top'] = index + 1

        if need_report_null_pic:
            reports.append(report_null_pic)

        return reports

    def initialize_report(self, sales, report):
        for sale in sales:
            if sale.username in report:
                continue
            report[sale.username] = {
                'pic': sale.username,
                'total_order': 0,
                'total_debt': 0,
                'paid_amount': 0,
                'remaining_debt': 0,
                'waiting_approved_remaining_debt': 0,
                'total_price': 0,
                'top': 0
            }

    def calculate_report_record(self, report, order, order_detail_map):
        if order.id not in order_detail_map:
            return report[order.pic.username]

        annual_amount = order_detail_map[order.id]['total_amount']
        annual_debt = order_detail_map[order.id]['total_debt']
        waiting_approval_annual_debt = order_detail_map[order.id]['total_waiting_approval_debt']
        total_price = order_detail_map[order.id]['total_price']

        return {
            'pic': order.pic.username,
            'total_order': report[order.pic.username]['total_order'],
            'total_debt': report[order.pic.username]['total_debt'] + annual_amount,
            'paid_amount': report[order.pic.username]['paid_amount'] + annual_amount - annual_debt,
            'remaining_debt': report[order.pic.username]['remaining_debt'] + annual_debt,
            'waiting_approved_remaining_debt': report[order.pic.username][
                                                   'waiting_approved_remaining_debt'] + waiting_approval_annual_debt,
            'total_price': total_price,
            'top': 0
        }

    def get_order_detail_map(self, orders, payment_from_date, payment_to_date):
        order_details = OrderDetail.objects.filter(order__in=orders, deleted_at__isnull=True,
                                                   type=ORDER_DETAIL_TYPE.ANNUAL_BUY)

        if payment_from_date and payment_to_date:
            order_details = order_details.filter(payment_date__gte=payment_from_date,
                                                 payment_date__lte=payment_to_date)

        order_details = order_details.values('order').order_by(
            'order').annotate(total_debt=Sum('debt'), total_amount=Sum('total_payment_amount'),
                              total_waiting_approval_debt=Sum('waiting_approval_debt'), total_price=Sum('price'))
        order_detail_map = dict()
        for order_detail in order_details:
            if order_detail['order'] in order_detail_map:
                order_detail_map[order_detail['order']].append(order_detail)
            else:
                order_detail_map[order_detail['order']] = order_detail

        return order_detail_map


class FilterBadDebtReportService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)
        orders = []
        filters = ['months']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'months' and value is not None:
                orders = Order.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True,
                                              annual_due_date__isnull=False, annual_debt__gt=0)
                data_status = DataStatus.objects.filter(company_id=user_roles.first().company_id, name__iexact='Đã hủy',
                                                        deleted_at__isnull=True).first()
                if data_status:
                    orders = orders.exclude(data_status_id=data_status.id)
                if params.get('months', None):
                    from_date = datetime.today() - relativedelta(months=params.get('months'))
                    orders = orders.filter(annual_due_date__lt=from_date)

        report = dict()

        user_service = FilterSaleUserService()
        sales = user_service.serve(request, cookies, *args, **kwargs)
        self.initialize_report(sales, report)

        for order in orders:
            if order.pic and order.pic.username in report:
                report[order.pic.username] = {
                    'pic': order.pic.username,
                    'total_order': report[order.pic.username]['total_order'] + 1,
                    'total_debt': report[order.pic.username]['total_debt'] + order.annual_amount,
                    'paid_amount': report[order.pic.username]['paid_amount'] + order.annual_amount - order.annual_debt,
                    'remaining_debt': report[order.pic.username]['remaining_debt'] + order.annual_debt,
                    'waiting_approved_remaining_debt': report[order.pic.username][
                                                           'waiting_approved_remaining_debt'] + order.waiting_approval_annual_debt,
                    'top': 0
                }

        reports = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            reports.sort(key=lambda r: r['remaining_debt'], reverse=True)
            for index, report in enumerate(reports):
                report['top'] = index + 1
        else:
            reports.sort(key=lambda r: r['remaining_debt'], reverse=False)
            for index, report in enumerate(reports.reverse()):
                report['top'] = index + 1

        return reports

    def initialize_report(self, sales, report):
        for sale in sales:
            report[sale.username] = {
                'pic': sale.username,
                'total_order': 0,
                'total_debt': 0,
                'paid_amount': 0,
                'remaining_debt': 0,
                'waiting_approved_remaining_debt': 0,
                'top': 0
            }


class FilterOrderStatusReportService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)
        filters = ['order', 'order_by']
        params = dict(kwargs.get('filter', []))
        orders = []
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})

        reports = dict()
        report_by_date = dict()
        self.initialize_report(request.user, reports)

        for order in orders:
            if order.created_date is None:
                continue

            created_date_str = order.created_date.strftime('%d/%m/%Y')
            if order.data_status and order.data_status.name in reports:
                reports[order.data_status.name]['total'] += 1
                if order.created_date:
                    if created_date_str not in reports[order.data_status.name]['records']:
                        reports[order.data_status.name]['records'][created_date_str] = 1
                    else:
                        reports[order.data_status.name]['records'][created_date_str] += 1

                if order.data_sub_status:
                    if order.data_sub_status.name in reports[order.data_status.name]['data_sub_status']:
                        reports[order.data_status.name]['data_sub_status'][order.data_sub_status.name]['total'] += 1
                    else:
                        reports[order.data_status.name]['data_sub_status'][order.data_sub_status.name] = {
                            'total': 1,
                            'title': order.data_sub_status.name,
                            'records': dict()
                        }
                    if created_date_str not in reports[order.data_status.name]['data_sub_status'][
                        order.data_sub_status.name]['records']:
                        reports[order.data_status.name]['data_sub_status'][order.data_sub_status.name]['records'][
                            created_date_str] = 1
                    else:
                        reports[order.data_status.name]['data_sub_status'][order.data_sub_status.name]['records'][
                            created_date_str] += 1

            if created_date_str in report_by_date:
                report_by_date[created_date_str] += 1
            else:
                report_by_date[created_date_str] = 1


        final_report = {
            'report_by_status': [],
            'report_by_date': []
        }
        for report in list(reports.values()):
            report['level'] = 1
            data_sub_status = report['data_sub_status']
            records = report['records']
            report['records'] = []
            for key, value in records.items():
                report['records'].append({
                    'key': key,
                    'value': value
                })
            final_report['report_by_status'].append({
                'level': report['level'],
                'title': report['title'],
                'total': report['total'],
                'records': report['records']
            })
            for data_ss in list(data_sub_status.values()):
                data_ss['level'] = 2
                records = data_ss['records']
                data_ss['records'] = []
                for key, value in records.items():
                    data_ss['records'].append({
                        'key': key,
                        'value': value
                    })

                final_report['report_by_status'].append({
                    'level': data_ss['level'],
                    'title': data_ss['title'],
                    'total': data_ss['total'],
                    'records': data_ss['records']
                })

        for key, value in report_by_date.items():
            final_report['report_by_date'].append({
                'key': key,
                'value': value
            })

        return final_report

    def initialize_report(self, user, report):
        filter = {
            'user': user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)
        data_status = DataStatus.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

        for ds in data_status:
            data_sub_status = DataSubStatus.objects.filter(company_id=user_roles.first().company_id,
                                                           deleted_at__isnull=True, data_status=ds)
            report[ds.name] = {
                'title': ds.name,
                'total': 0,
                'records': dict(),
                'data_sub_status': dict(),
            }
            for dss in data_sub_status:
                report[ds.name]['data_sub_status'][dss.name] = {
                    'total': 0,
                    'title': dss.name,
                    'records': dict()
                }

