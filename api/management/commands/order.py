import json
import requests

from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, Q, F
from pytz import timezone

from api.const import ORDER_DETAIL_TYPE, ORDER_PAYMENT_STATUS, DEBT_STATUS, NOTIFICATION_TYPE
from api.models.call_center import CallLog
from api.models.data import AnnualOrder, OrderDetail, AnnualOrderHistory, OrderDetailHistory, Order, Payment, \
    OrderDetailPayment
from api.models.notification import Notification
from api.models.system_configuration import DataStatus, DataChannel
from api.services.data import create_order_detail_history, recalculate_order, recalculate_order_details_by_payment, \
    recalculate_payment_order_detail
from api.utils.date import get_last_of_month, get_first_of_month
from api.utils.order_detail import update_charge_date_order_detail
from api.utils.phone import classify_telecom_number
from crm.settings import TIME_ZONE
import logging
from logging.handlers import RotatingFileHandler

from crm.settings import LOG_ROOT, LOG_LEVEL

import api.utils.call_center as call_center_utils

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
            if date_in_month_payment == (processing_date + relativedelta(
                    days=annual_order.product.number_of_date_notify - 1)).day:
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
                                                              annual_remaining_payment_amount=annual_order.order_detail.product.period_fee * annual_order.order_detail.quantity - annual_order.order_detail.discount_value,
                                                              annual_paid_payment_amount=0,
                                                              paid_payment_amount=0,
                                                              debt=annual_order.order_detail.product.period_fee * annual_order.order_detail.quantity - annual_order.order_detail.discount_value,
                                                              due_date=(processing_date + relativedelta(
                                                                  days=annual_order.product.number_of_date_notify - 1)))
                create_order_detail_history(new_order_detail)
                recalculate_order(new_order_detail.order)

                annual_order.order_detail_id = new_order_detail.id
                annual_order.save()
                AnnualOrderHistory.objects.create(annual_order_id=annual_order.id, order_detail_id=new_order_detail.id)

                if new_order_detail.order.pic_id:
                    Notification.objects.create(company=new_order_detail.order.company,
                                                user_id=new_order_detail.order.pic_id,
                                                type=NOTIFICATION_TYPE.ANNUAL_BUY,
                                                content=json.dumps({
                                                    'phone': str(new_order_detail.order.customer.phone),
                                                    'customer_name': new_order_detail.order.customer_name
                                                }))

    def calculate_debt_status_order(self, processing_date):
        yesterday = processing_date - relativedelta(days=1)
        self.logger.info('Calculating debt status, yesterday: ' + str(yesterday))
        order_id_list = OrderDetail.objects.filter(due_date=yesterday, deleted_at__isnull=True).values_list('order_id',
                                                                                                            flat=True)
        orders = Order.objects.filter(id__in=order_id_list, deleted_at__isnull=True)
        self.logger.info('Number of orders: ' + str(len(orders)))
        for order in orders:
            old_debt_status = order.debt_status
            recalculate_order(order)
            if order.debt_status == DEBT_STATUS.UNPAID and order.debt_status != old_debt_status and order.pic_id:
                Notification.objects.create(company=order.company, user_id=order.pic_id, type=NOTIFICATION_TYPE.DEBT,
                                            content=json.dumps({
                                                'phone': str(order.customer.phone),
                                                'customer_name': order.customer_name,
                                                'debt': order.debt + order.annual_debt
                                            }))

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

    def fix_annual_order_generation(self, processing_date):
        annual_orders = AnnualOrder.objects.filter(is_active=True, deleted_at__isnull=True)
        for annual_order in annual_orders:
            date_in_month_payment = annual_order.product.date_in_month_payment
            if date_in_month_payment == (processing_date + relativedelta(
                    days=annual_order.product.number_of_date_notify - 1)).day:
                self.logger.info('Fixing AnnualOrder id: ' + str(annual_order.id))
                ao = AnnualOrderHistory.objects.filter(annual_order_id=annual_order.id).order_by('-id')
                fi = ao.first()
                if fi:
                    annual_order.order_detail_id = fi.order_detail_id
                    annual_order.save()
                    recalculate_order(annual_order.order_detail.order)

    def notify_renew_date(self, processing_date):
        month_end = get_last_of_month(processing_date)
        self.logger.info('Notify renew date, month_end: ' + str(month_end))

        order_details = OrderDetail.objects.filter(deleted_at__isnull=True, renew_date=processing_date)

        for order_detail in order_details:
            if order_detail.order.pic_id:
                Notification.objects.create(company=order_detail.order.company,
                                            user_id=order_detail.order.pic_id,
                                            type=NOTIFICATION_TYPE.RENEW,
                                            content=json.dumps({
                                                'phone': str(order_detail.order.customer.phone),
                                                'customer_name': order_detail.order.customer_name
                                            }))

    def migrate_order_detail_payment(self):
        with transaction.atomic():
            payments = Payment.objects.filter(deleted_at__isnull=True)
            for payment in payments:
                print('Update payment id: ', payment.id)
                details = OrderDetailPayment.objects.filter(deleted_at__isnull=True, payment=payment).order_by('id')
                payment.auto_picked_order_details = json.dumps([x.order_detail_id for x in details])
                payment.save()

    def fix_order_detail_list_in_payment(self):
        with transaction.atomic():
            payments = Payment.objects.filter(deleted_at__isnull=True, order_detail_list='')
            for payment in payments:
                print('Update payment id: ', payment.id)
                if payment.order_detail_id:
                    payment.order_detail_list = json.dumps([payment.order_detail_id])
                else:
                    payment.order_detail_list = json.dumps([0])
                payment.save()

    def initialize_charge_date(self):
        order_details = OrderDetail.objects.filter(deleted_at__isnull=True, charge_to_date__isnull=True)
        for order_detail in order_details:
            print("Processing: ", order_detail.id)
            order_detail.charge_from_date = datetime(year=2023, month=8, day=1)
            order_detail.charge_to_date = datetime(year=2023, month=8, day=31)
            order_detail.save()
            update_charge_date_order_detail(order_detail)
            recalculate_order_details_by_payment(order_detail)

    def fix_data_channels(self):
        orders = Order.objects.filter(deleted_at__isnull=True, company_id=26)
        for order in orders:
            if order.data_channel and order.data_source and order.data_channel.data_source.id != order.data_source_id:
                print('Found: ', order.id)
                new_data_channel = DataChannel.objects.filter(data_source_id=order.data_source_id, name=order.data_channel.name).first()
                if new_data_channel:
                    order.data_channel_id = new_data_channel.id
                    print('New channel id: ', new_data_channel.id)
                    order.save()

    def migrate_call_log(self):
        last_month = get_first_of_month(datetime.now() - relativedelta(month=1))
        call_logs = CallLog.objects.filter(calldate__gte=last_month)
        for call_log in call_logs:
            call_log.provider = classify_telecom_number(call_log.dstchannel)

        batch_size = 1000
        for i in range(0, len(call_logs), batch_size):
            print('Processing from {} to {}'.format(i, i + batch_size))
            batch = call_logs[i:i + batch_size]
            CallLog.objects.bulk_update(batch, fields=['provider'])

    def fix_call_log_missing(self):
        url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid=1709258120.35581337&fromdate=2024-02-01 00:00:00'
        call_logs = CallLog.objects.filter(status__isnull=True, created_at__gte='2024-02-01')
        session = requests.Session()
        session.auth = ('ITY', 'Crm1ty@1305Fri')
        for call_log in call_logs:
            url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid={}&fromdate=2024-02-01 00:00:00'.format(call_log.callid)
            response = session.get(url)

            # Print the response
            response_json = response.json()
            if len(response_json['cdr']) == 1:
                data = response_json['cdr'][0]
                call_log.calldate = datetime.strptime(data['calldate'], '%Y-%m-%d %H:%M:%S')
                call_log.duration = int(data['duration'])
                call_log.billsec = int(data['billsec'])
                call_log.status = data['status']
                call_log.recording = data['recordingfile']
                call_log.accountcode = data['accountcode']
                call_log.ip = data['ip']
                call_log.dstchannel = data['dstchannel']
                call_log.userfield = data['userfield']
                call_log.provider = classify_telecom_number(call_log.dstchannel)
                call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
                call_log.save()
            else:
                print('Cannot get data for callid: ' + call_log.callid)

    def fix_dstchannel(self):
        import pandas as pd

        records = pd.read_csv('/home/khanhnt/crm/202402.csv', header=None).to_numpy()
        dst_dict = dict()
        for record in records:
            dst_dict[str(record[0])] = record[1]
            # if 'VTL' not in record[1] and 'VMS' not in record[1] and 'VNP' not in record[1] and 'OTHER' not in record[1]\
            #         and 'Other' not in record[1]:
            #     print(record[1])

        print(len(dst_dict))
        call_logs = CallLog.objects.filter(deleted_at__isnull=True, created_at__gte='2024-02-01')
        for call_log in call_logs:
            call_id = call_log.callid
            call_id = call_id.split('.')[0]
            #print('checking ' + call_id)
            if call_id in dst_dict:
                if call_log.dstchannel != dst_dict[call_id]:
                    call_log.dstchannel = dst_dict[call_id]
                    call_log.provider = classify_telecom_number(call_log.dstchannel)
                    call_log.save()
                # else:
                #     print(call_log.callid)

            else:
                print('Missing: ' + str(call_id))

    def recalculate_provider(self):
        call_logs = CallLog.objects.filter(deleted_at__isnull=True, created_at__gte='2024-02-01', created_at__lte='2024-03-14')
        for call_log in call_logs:
            old_provider = call_log.provider
            call_log.provider = classify_telecom_number(call_log.phone)
            call_log.save()
            if call_log.provider != old_provider:
                print("Changed " + str(call_log.id))

    def handle(self, *args, **options):
        self.initializer_logger()
        processing_date = datetime.now(timezone(TIME_ZONE)).date() if options['date'] == '' else datetime.strptime(
            options['date'], '%Y%m%d').date()

        self.process_annual_buy(processing_date)
        self.calculate_debt_status_order(processing_date)
        self.notify_renew_date(processing_date)

        # self.recalculate_provider()
        # self.fix_dstchannel()
        # self.fix_call_log_missing()
        # self.migrate_call_log()
        # self.initialize_charge_date()
        # self.fix_annual_order_generation()
        # self.recalculate_order_17()
        # self.reset_order_detail()
        # self.migrate_payments()
        # self.migrate_payment_date()
        # self.migrate_order_detail_payment()
        #s elf.fix_order_detail_list_in_payment()
