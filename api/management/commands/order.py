from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from pytz import timezone

from api.const import ORDER_DETAIL_TYPE, ORDER_PAYMENT_STATUS
from api.models.data import AnnualOrder, OrderDetail, AnnualOrderHistory, OrderDetailHistory, Order, Payment, \
    OrderDetailPayment
from api.models.system_configuration import DataStatus
from api.services.data import create_order_detail_history, recalculate_order, recalculate_order_details_by_payment
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

    def reset_order_detail(self):
        order_details = OrderDetail.objects.filter(
            company_id=17,
            type=ORDER_DETAIL_TYPE.NEW_BUY,
            deleted_at__isnull=True
        )

        for order_detail in order_details:
            order_detail.remaining_payment_amount = order_detail.total_payment_amount
            order_detail.save()

        order_details = OrderDetail.objects.filter(
            company_id=17,
            type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
            deleted_at__isnull=True
        )

        for order_detail in order_details:
            order_detail.annual_remaining_payment_amount = order_detail.total_payment_amount
            order_detail.save()
    def migrate_payments(self):
        payments = Payment.objects.filter(company_id=17).exclude(
            orderdetailpayment=None,
            status__in=[ORDER_PAYMENT_STATUS.DISAPPROVED, ORDER_PAYMENT_STATUS.CANCELLED,
                        ORDER_PAYMENT_STATUS.DELETED]).order_by('id')

        data_status = DataStatus.objects.filter(company_id=17, name__iexact='Đã hủy',
                                                deleted_at__isnull=True).first()

        for payment in payments:
            if payment.order.data_status_id == data_status.id:
                continue

            with transaction.atomic():
                if payment.type == ORDER_DETAIL_TYPE.NEW_BUY:
                    order_details = OrderDetail.objects.filter(
                        order_id=payment.order_id,
                        type=ORDER_DETAIL_TYPE.NEW_BUY,
                        deleted_at__isnull=True
                    )

                    if len(order_details) == 0:
                        continue

                    print(str(payment.id) + ', ')

                    payment.order_detail_list = str([item.id for item in order_details])
                    payment.save()

                    if payment.order_detail_list:
                        payment_value = payment.value
                        for order_detail in order_details:

                            if payment_value == 0:
                                break
                            paid_amount = min(payment_value, order_detail.remaining_payment_amount)
                            OrderDetailPayment.objects.create(payment=payment, order_detail=order_detail,
                                                              value=paid_amount)
                            recalculate_order_details_by_payment(order_detail)
                            payment_value -= paid_amount
                else:
                    OrderDetailPayment.objects.create(payment=payment, order_detail=payment.order_detail,
                                                      value=payment.value)
                    recalculate_order_details_by_payment(payment.order_detail)
                recalculate_order(payment.order)

    def migrate_payment_date(self):
        order_details = OrderDetail.objects.filter(
            company_id=17,
            type=ORDER_DETAIL_TYPE.NEW_BUY,
            deleted_at__isnull=True
        )

        for order_detail in order_details:
            if order_detail.payment_date is None:
                print(str(order_detail.order_id) + ',')
                order_detail.payment_date = order_detail.created_at.date()
                order_detail.save()


    def recalculate_order_17(self):
        order_details = OrderDetail.objects.filter(company_id=17, deleted_at__isnull=True)
        for order_detail in order_details:
            recalculate_order_details_by_payment(order_detail)

        orders = Order.objects.filter(company_id=17, deleted_at__isnull=True)
        for order in orders:
            recalculate_order(order)

    def fix_annual_order_generation(self):
        order_details = OrderDetail.objects.filter(due_date__gt='2023-01-10', deleted_at__isnull=True,
                                                   type=ORDER_DETAIL_TYPE.ANNUAL_BUY)

        for order_detail in order_details:
            print('Fixing order detail id: ' + str(order_detail.id))
            ao = AnnualOrder.objects.filter(order_detail_id=order_detail.id)
            fi = ao.first()
            if fi:
                fi.order_detail_id = OrderDetail.objects.filter(order_id=order_detail.order_id,
                                                                type=ORDER_DETAIL_TYPE.ANNUAL_BUY,
                                                                id__lt=order_detail.id).order_by(
                    '-id').first().id
                fi.save()
            order_detail.deleted_at = datetime.now()
            order_detail.save()
            recalculate_order(order_detail.order)

    def handle(self, *args, **options):
        self.initializer_logger()
        processing_date = datetime.now(timezone(TIME_ZONE)).date() if options['date'] == '' else datetime.strptime(
            options['date'], '%Y%m%d').date()

        self.process_annual_buy(processing_date)
        self.calculate_debt_status_order(processing_date)

        #self.fix_annual_order_generation()
        # self.recalculate_order_17()
        # self.reset_order_detail()
        # self.migrate_payments()
        # self.migrate_payment_date()
