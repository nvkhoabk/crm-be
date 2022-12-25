from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from pytz import timezone

from api.const import ORDER_DETAIL_TYPE
from api.models.data import AnnualOrder, OrderDetail, AnnualOrderHistory, OrderDetailHistory, Order
from api.services.data import create_order_detail_history, recalculate_order
from api.utils.date import get_last_of_month
from crm.settings import TIME_ZONE
import logging
from logging.handlers import RotatingFileHandler

from crm.settings import LOG_ROOT, LOG_LEVEL


class Command(BaseCommand):
    help = 'Job generate annual buy and recalculate debt status'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument('--date', help='Processing date', default='')

    def initializer_logger(self):
        logging.basicConfig(handlers=[RotatingFileHandler(filename=LOG_ROOT + 'crm.order.log',
                                                          maxBytes=512000, backupCount=4)], level=LOG_LEVEL,
                            format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        self.logger = logging.getLogger(__name__)

    def process_annual_buy(self, processing_date):
        month_end = get_last_of_month(processing_date)
        self.logger.info('Processing annual buy, month_end: ' + str(month_end))
        annual_orders = AnnualOrder.objects.filter(is_active=True, deleted_at__isnull=True)
        for annual_order in annual_orders:
            date_in_month_payment = min(annual_order.product.date_in_month_payment, month_end.day)
            if date_in_month_payment + 1 - annual_order.product.number_of_date_notify == processing_date.day \
                    and annual_order.order_detail.due_date == processing_date + relativedelta(
                days=annual_order.product.number_of_date_notify - 1):
                self.logger.info('Creating new order detail for annual_order_id: ' + str(annual_order.id))

                new_order_detail = OrderDetail.objects.create(order_id=annual_order.order_detail.order_id,
                                                              company_id=annual_order.order_detail.company_id,
                                                              product_id=annual_order.order_detail.product_id,
                                                              type=annual_order.order_detail.type,
                                                              quantity=annual_order.order_detail.quantity,
                                                              price=annual_order.order_detail.price,
                                                              annual_price=annual_order.order_detail.annual_price,
                                                              total_payment_amount=annual_order.order_detail.total_payment_amount,
                                                              remaining_payment_amount=annual_order.order_detail.remaining_payment_amount,
                                                              annual_remaining_payment_amount=annual_order.order_detail.price * annual_order.order_detail.quantity - annual_order.order_detail.discount_value,
                                                              annual_paid_payment_amount=0,
                                                              paid_payment_amount=0,
                                                              debt=annual_order.product.period_fee,
                                                              due_date=annual_order.order_detail.due_date + relativedelta(
                                                                  months=1))
                create_order_detail_history(new_order_detail)
                recalculate_order(new_order_detail.order)

                annual_order.order_detail_id = new_order_detail.id
                annual_order.save()
                AnnualOrderHistory.objects.create(annual_order_id=annual_order.id, order_detail_id=new_order_detail.id)

    def calculate_debt_status_order(self, processing_date):
        yesterday = processing_date - relativedelta(days=1)
        self.logger.info('Calculating debt status, yesterday: ' + str(yesterday))
        order_id_list = OrderDetail.objects.filter(due_date=yesterday, deleted_at__isnull=True).values_list('order_id',
                                                                                                            flat=True)
        orders = Order.objects.filter(id__in=order_id_list, deleted_at__isnull=True)
        self.logger.info('Number of orders: ' + str(len(orders)))
        for order in orders:
            recalculate_order(order)

    def recalculate_order_17(self):
        orders = Order.objects.filter(company_id=17)
        for order in orders:
            recalculate_order(order)

    def handle(self, *args, **options):
        self.initializer_logger()
        processing_date = datetime.now(timezone(TIME_ZONE)).date() if options['date'] == '' else datetime.strptime(
            options['date'], '%Y%m%d').date()

        self.process_annual_buy(processing_date)
        self.calculate_debt_status_order(processing_date)
        self.recalculate_order_17()
