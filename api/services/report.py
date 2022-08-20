from datetime import datetime

from dateutil.relativedelta import relativedelta

from api.common.base_service import BaseService
from api.common.cookies import Cookies
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
                orders = order_service.serve(request, cookies, *args, **value)
                orders = orders.filter(due_date__isnull=False)

        report = dict()
        user_service = FilterSaleUserService()
        sales = user_service.serve(request, cookies, *args, **kwargs)
        self.initializer_report(sales, report)

        for order in orders:
            if order.pic:
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

        report = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            report.sort(key=lambda r: r['actual_amount'], reverse=True)
        else:
            report.sort(key=lambda r: r['actual_amount'], reverse=False)

        return report

    def initializer_report(self, sales, report):
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

        return order.confirmed_date - order.created_date

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
                orders = order_service.serve(request, cookies, *args, **value)
                orders = orders.filter(annual_due_date__isnull=False)

        report = dict()
        user_service = FilterSaleUserService()
        sales = user_service.serve(request, cookies, *args, **kwargs)
        self.initializer_report(sales, report)

        for order in orders:
            if order.pic:
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

        report = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            report.sort(key=lambda r: r['paid_amount'], reverse=True)
        else:
            report.sort(key=lambda r: r['paid_amount'], reverse=False)

        return report

    def initializer_report(self, sales, report):
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
                orders = order_service.serve(request, cookies, *args, **value)
                if params.get('months', None):
                    from_date = datetime.today() - relativedelta(months=params.get('months'))
                    orders.filter(annual_due_date__lt=from_date)

        report = dict()
        user_service = FilterSaleUserService()
        sales = user_service.serve(request, cookies, *args, **kwargs)
        self.initializer_report(sales, report)

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

        report = list(report.values())
        if params.get('order_by', None) and params.get('order_by', None) == 'desc':
            report.sort(key=lambda r: r['remaining_debt'], reverse=True)
        else:
            report.sort(key=lambda r: r['remaining_debt'], reverse=False)

        return report

    def initializer_report(self, sales, report):
        for sale in sales:
            report[sale.username] = {
                "pic": sale.username,
                "total_order": 0,
                "total_debt": 0,
                "paid_amount": 0,
                "remaining_debt": 0,
                "waiting_approved_remaining_debt": 0,
                'top': 0
            }
