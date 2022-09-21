from datetime import datetime

import json
from dateutil.relativedelta import relativedelta

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import UserRole
from api.models.system_configuration import DataStatus, DataSubStatus
from api.services.data import FilterOrderService

from api.services.manage import FilterSaleUserService


class FilterReportService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filters = ['order', 'order_by']
        params = dict(kwargs.get('filter', []))
        orders = []
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})
                orders = orders.filter(due_date__isnull=False)

        report = dict()
        user_service = FilterSaleUserService()
        sales = user_service.serve(request, cookies, *args, **kwargs)
        self.initialize_report(sales, report)

        for order in orders:
            if order.pic and order.pic.username in report:
                report[order.pic.username] = {
                    'pic': order.pic.username,
                    'total_order': report[order.pic.username]['total_order'] + 1,
                    'total_confirmed_order': report[order.pic.username]['total_confirmed_order'] + self.confirmed_order(
                        order),
                    'conversion_rate': (report[order.pic.username]['total_confirmed_order'] + self.confirmed_order(
                        order)) / (report[order.pic.username]['total_order'] + 1),
                    'turnover': report[order.pic.username]['turnover'] + order.amount,
                    'debt': report[order.pic.username]['debt'] + order.debt,
                    'waiting_approved_debt': report[order.pic.username][
                                                 'waiting_approved_debt'] + order.waiting_approval_debt,
                    'total_confirmed_time': report[order.pic.username]['total_confirmed_time'] + self.confirmed_time(
                        order),
                    'average_confirmed_time': self.calculate_average_confirmed_time(report, order),
                    'actual_amount': report[order.pic.username]['actual_amount'] + order.amount - order.debt,
                    'top': 0
                }

        reports = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            reports.sort(key=lambda r: r['actual_amount'], reverse=True)
            for index, report in enumerate(reports):
                report['top'] = index + 1
        else:
            reports.sort(key=lambda r: r['actual_amount'], reverse=False)
            for index, report in enumerate(reports[::-1]):
                report['top'] = index + 1

        return reports

    def initialize_report(self, sales, report):
        for sale in sales:
            report[sale.username] = {
                'pic': sale.username,
                'total_order': 0,
                'total_confirmed_order': 0,
                'conversion_rate': 0,
                'turnover': 0,
                'debt': 0,
                'waiting_approved_debt': 0,
                'total_confirmed_time': 0,
                'average_confirmed_time': 0,
                'actual_amount': 0,
                'top': 0
            }

    def confirmed_order(self, order):
        if order.data_status and order.data_status.name.lower() == 'đã xác nhận':
            return 1

        return 0

    def confirmed_time(self, order):
        if self.confirmed_order(order) == 0:
            return 0

        return (order.confirmed_date - order.created_date).days

    def calculate_average_confirmed_time(self, report, order):
        if (report[order.pic.username]['total_confirmed_order'] + self.confirmed_order(order)) == 0:
            return 0

        return (report[order.pic.username]['total_confirmed_time'] + self.confirmed_time(
            order)) / (report[order.pic.username]['total_confirmed_order'] + self.confirmed_order(order))


class FilterAnnualOrderReportService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        orders = []
        filters = ['order']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})
                orders = orders.filter(annual_due_date__isnull=False)

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
            reports.sort(key=lambda r: r['paid_amount'], reverse=True)
            for index, report in enumerate(reports):
                report['top'] = index + 1
        else:
            reports.sort(key=lambda r: r['paid_amount'], reverse=False)
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


class FilterBadDebtReportService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        orders = []
        filters = ['order']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'order' and value is not None:
                order_service = FilterOrderService()
                orders = order_service.serve(request, cookies, *args, **{'filter': value})
                if params.get('months', None):
                    from_date = datetime.today() - relativedelta(months=params.get('months'))
                    orders.filter(annual_due_date__lt=from_date)

        report = dict()
        user_service = FilterSaleUserService()
        sales = user_service.serve(request, cookies, *args, **kwargs)
        self.initialize_report(sales, report)

        for order in orders:
            if order.pic and order.pic.username not in report:
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

