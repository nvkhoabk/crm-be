from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from pytz import timezone

from api.const import ORDER_DETAIL_TYPE
from api.models.data import AnnualOrder, OrderDetail, AnnualOrderHistory, OrderDetailHistory, Order
from api.services.data import create_order_detail_history, recalculate_order
from api.utils.date import get_last_of_month
from crm.settings import TIME_ZONE


class Command(BaseCommand):
    help = 'Runs a job'

    def process_annual_buy(self):
        month_end = get_last_of_month(datetime.now(timezone(TIME_ZONE)))
        annual_orders = AnnualOrder.objects.filter(is_active=True, deleted_at__isnull=True)
        for annual_order in annual_orders:
            date_in_month_payment = min(annual_order.product.date_in_month_payment, month_end.day)
            if date_in_month_payment + 1 - annual_order.product.number_of_date_notify == datetime.now(
                    timezone(TIME_ZONE)).day:
                new_order_detail = OrderDetail.objects.create(order_id=annual_order.order_detail.order_id,
                                                              company_id=annual_order.order_detail.company_id,
                                                              product_id=annual_order.order_detail.product_id,
                                                              type=annual_order.order_detail.type,
                                                              quantity=annual_order.order_detail.quantity,
                                                              price=annual_order.order_detail.price,
                                                              annual_price=annual_order.order_detail.annual_price,
                                                              total_payment_amount=annual_order.order_detail.total_payment_amount,
                                                              remaining_payment_amount=annual_order.order_detail.remaining_payment_amount,
                                                              paid_payment_amount=0,
                                                              debt=annual_order.product.period_fee,
                                                              due_date=annual_order.order_detail.due_date + relativedelta(
                                                                  months=1))
                create_order_detail_history(new_order_detail)
                recalculate_order(new_order_detail.order)

                annual_order.order_detail_id = new_order_detail.id
                annual_order.save()
                AnnualOrderHistory.objects.create(annual_order_id=annual_order.id, order_detail_id=new_order_detail.id)

    def calculate_debt_status_order(self):
        yesterday = datetime.now(timezone(TIME_ZONE)) - relativedelta(days=1)
        order_id_list = OrderDetail.objects.filter(due_date=yesterday, deleted_at__isnull=True).values_list('order_id',
                                                                                                            flat=True)
        orders = Order.objects.filter(id__in=order_id_list, deleted_at__isnull=True)
        for order in orders:
            recalculate_order(order)

    def recalculate_order_17(self):
        orders = Order.objects.filter(company_id=17)
        for order in orders:
            recalculate_order(order)

    def handle(self, *args, **options):
        self.process_annual_buy()
        self.calculate_debt_status_order()
        #self.recalculate_order_17()
