import json
import requests
import xlrd

from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum, Q, F
from pytz import timezone

from api.const import ORDER_DETAIL_TYPE, ORDER_PAYMENT_STATUS, DEBT_STATUS, NOTIFICATION_TYPE, PHONE_NUMBER_PROVIDER, \
    CALL_DIRECTION
from api.models.call_center import CallLog
from api.models.data import AnnualOrder, OrderDetail, AnnualOrderHistory, OrderDetailHistory, Order, Payment, \
    OrderDetailPayment
from api.models.notification import Notification
from api.models.phone_number import PhoneNumber, PhoneNumberLockHistory, PhoneNumberClient, PhoneNumberStatus
from api.models.system_configuration import DataStatus, DataChannel
from api.services.data import create_order_detail_history, recalculate_order, recalculate_order_details_by_payment, \
    recalculate_payment_order_detail
from api.services.phone_number import calculate_lock_information, update_lock_count
from api.utils.date import get_last_of_month, get_first_of_month
from api.utils.order_detail import update_charge_date_order_detail, recalcuate_monthly_order_detail_by_payment
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

    def fix_montly_order_detail(self):
        order_details = OrderDetail.objects.filter(deleted_at__isnull=True, charge_to_date__isnull=False,
                                                   company_id=17).exclude(charge_from_date='2023-08-01')
        for order_detail in order_details:
            print("Processing: ", order_detail.id)
            update_charge_date_order_detail(order_detail)
            recalcuate_monthly_order_detail_by_payment(order_detail)

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
        call_logs = CallLog.objects.filter(status__isnull=True, created_at__gte='2024-05-01')
        session = requests.Session()
        session.auth = ('ITY', 'Crm1ty@1305Fri')
        for call_log in call_logs:
            url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid={}&fromdate=2024-02-05 00:00:00'.format(call_log.callid)
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

    def fix_call_log_wrong(self):
        crm = open('crm.csv', 'r')
        crm_lines = crm.readlines()
        cdr = open('cdr.csv', 'r')
        cdr_lines = cdr.readlines()
        url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid=1709258120.35581337&fromdate=2024-02-01 00:00:00'
        session = requests.Session()
        session.auth = ('ITY', 'Crm1ty@1305Fri')

        print('Processing crm')
        for line in crm_lines:
            try:
                callid = line.split(',')[2]
                url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid={}&fromdate=2024-02-01 00:00:00'.format(
                    callid)
                response = session.get(url)
                call_log = CallLog.objects.get(callid=callid, deleted_at__isnull=True)
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
                    call_log.extension = data['extension']
                    call_log.phone = data['phone']
                    call_log.provider = classify_telecom_number(call_log.dstchannel)
                    call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
                    call_log.save()
                else:
                    print('Cannot get data for callid: ' + call_log.callid)
            except Exception as e:
                print('Exception: ' + str(e))

        print('Processing cdr')
        for line in cdr_lines:
            try:
                callid = line.split(',')[2]
                url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid={}&fromdate=2024-02-01 00:00:00'.format(
                    callid)
                response = session.get(url)
                call_logs = CallLog.objects.filter(callid=callid, deleted_at__isnull=True)
                if call_logs:
                    call_log = call_logs.first()
                else:
                    call_log = CallLog.objects.create(callid=callid, extension="")

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
                    call_log.extension = data['extension']
                    call_log.phone = data['phone']
                    call_log.provider = classify_telecom_number(call_log.dstchannel)
                    call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
                    call_log.save()
                else:
                    print('Cannot get data for callid: ' + call_log.callid)
            except Exception as e:
                print('Exception: ' + str(e))


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

    def fix_lock_date_phone_number(self):
        phone_numbers = PhoneNumber.objects.filter(deleted_at__isnull=True, lock_history_id__gt=0)
        for pn in phone_numbers:
            print('Processing ' + pn.phone_number + ' with provider: ' + pn.lock_provider)
            lock = PhoneNumberLockHistory.objects.get(pk=pn.lock_history_id)
            current_lock = json.loads(pn.lock_provider)
            if current_lock[PHONE_NUMBER_PROVIDER.VIETTEL]:
                lock.viettel_lock_date = lock.created_at.date()
            if current_lock[PHONE_NUMBER_PROVIDER.MOBI]:
                lock.mobifone_lock_date = lock.created_at.date()
            if current_lock[PHONE_NUMBER_PROVIDER.VINA]:
                lock.vinaphone_lock_date = lock.created_at.date()
            if current_lock[PHONE_NUMBER_PROVIDER.OTHER]:
                lock.other_lock_date = lock.created_at.date()
            lock.save()
            calculate_lock_information(pn, {})
            pn.save()

    def init_phone_number_client(self):
        clients = PhoneNumberClient.objects.filter()
        for client in clients:
            order = Order.objects.filter(company_id=17, deleted_at__isnull=True, pic__isnull=False,
                                         customer_name__icontains=client.name).order_by('-id').first()
            print('Checking ' + client.name)
            if order:
                print(order.pic_id)
                print(order.pic.username)
                # client.pic_id = order.pic_id
                # client.save()

    def get_lock_status(self, lock_status):
        if lock_status == 'Đã gửi nhà cung cấp' or lock_status == 'Đã gửi NCC':
            return 'SENT_PROVIDER'
        if lock_status == 'Đã mở':
            return 'OPENED'
        if lock_status == 'Nhà cung cấp báo sai':
            return 'WRONG_REPORT'
        return 'AVAILABLE'
    def update_phone_number_info(self, phone, using_providers, lock_provider, lock_date,
                                                      open_provider, open_date, lock_status, send_provider_date,
                                                      cancel_date, client_use_date):
        phone_number = PhoneNumber.objects.filter(phone_number__icontains=phone).first()
        VIETTEL = 'Viettel'
        MOBIFONE = 'Mobifone'
        VINAPHONE = 'Vinaphone'
        if phone_number:
            if lock_provider:
                lock = PhoneNumberLockHistory.objects.create(company=phone_number.company,
                                                             phone_number=phone_number,
                                                             checking_lock_date=datetime.today(),
                                                             confirm_lock_date=datetime.today(),
                                                             viettel_lock_date=None,
                                                             mobifone_lock_date=None,
                                                             vinaphone_lock_date=None,
                                                             other_lock_date=None)
                if lock_provider.strip() == VIETTEL:
                    lock.viettel_lock_date = datetime.strptime(lock_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if open_date.strip():
                        lock.unlock_lock_date = datetime.strptime(open_date.strip().replace(' ', ''), '%d/%m/%Y')
                        phone_number.viettel_using_status = 'OPEN'
                    else:
                        phone_number.viettel_using_status = 'LOCK'
                        if send_provider_date.strip():
                            lock.send_provider_date = datetime.strptime(send_provider_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if lock_status:
                        phone_number.viettel_unlocking_status = self.get_lock_status(lock_status)
                if lock_provider.strip() == VINAPHONE:
                    lock.vinaphone_lock_date = datetime.strptime(lock_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if open_date.strip():
                        lock.unlock_lock_date = datetime.strptime(open_date.strip().replace(' ', ''), '%d/%m/%Y')
                        phone_number.vinaphone_using_status = 'OPEN'
                    else:
                        phone_number.vinaphone_using_status = 'LOCK'
                        if send_provider_date.strip():
                            lock.send_provider_date = datetime.strptime(send_provider_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if lock_status:
                        phone_number.vinaphone_unlocking_status = self.get_lock_status(lock_status)
                if lock_provider.strip() == MOBIFONE:
                    lock.mobifone_lock_date = datetime.strptime(lock_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if open_date.strip():
                        lock.unlock_lock_date = datetime.strptime(open_date.strip().replace(' ', ''), '%d/%m/%Y')
                        phone_number.mobifone_using_status = 'OPEN'
                    else:
                        phone_number.mobifone_using_status = 'LOCK'
                        if send_provider_date.strip():
                            lock.send_provider_date = datetime.strptime(send_provider_date.strip().replace(' ', ''), '%d/%m/%Y')
                    if lock_status:
                        phone_number.mobifone_unlocking_status = self.get_lock_status(lock_status)
                lock.save()

            provider_list = using_providers.split(',')
            for provider in provider_list:
                if provider.strip() == VIETTEL:
                    phone_number.viettel_using_status = 'USING'
                if provider.strip() == VINAPHONE:
                    phone_number.vinaphone_using_status = 'USING'
                if provider.strip() == MOBIFONE:
                    phone_number.mobifone_using_status = 'USING'

            if cancel_date:
                status = PhoneNumberStatus.objects.filter(name__iexact='Đã hủy').first()
                phone_number.provider_cancel_date = datetime.strptime(cancel_date.strip().replace(' ', ''), '%d/%m/%Y')
                if status:
                    phone_number.phone_number_status_id = status.id
            if client_use_date:
                phone_number.client_use_date = datetime.strptime(client_use_date.strip().replace(' ', ''), '%d/%m/%Y')
                if not phone_number.active_date:
                    phone_number.active_date = phone_number.client_use_date

            update_lock_count(phone_number)
            phone_number.save()
        else:
            print('Khong tim thay: {}'.format(phone))

    def fix_pickup_date(self, phone, pickup_date):
        phone_number = PhoneNumber.objects.filter(phone_number__icontains=phone).first()
        VIETTEL = 'Viettel'
        MOBIFONE = 'Mobifone'
        VINAPHONE = 'Vinaphone'
        if phone_number:
            print(pickup_date)
            if pickup_date:
                phone_number.pickup_date = datetime.strptime(pickup_date.strip().replace(' ', ''), '%Y-%m-%d')
            phone_number.save()
        else:
            print('Khong tim thay: {}'.format(phone))
    def migrate_phone_number(self):
        workbook = xlrd.open_workbook('input.xlsx', encoding_override='utf-8')
        worksheet = workbook.sheet_by_index(0)
        num_rows = worksheet.nrows - 1
        curr_row = 0
        rows = []
        while curr_row < num_rows:
            curr_row += 1
            rows = worksheet.row(curr_row)
            print(len(rows))
            phone_number = str(rows[1].value).strip()
            using_providers = str(rows[2].value).strip()
            lock_provider = str(rows[3].value).strip()
            lock_date = str(rows[4].value).strip()
            open_provider = str(rows[5].value).strip()
            open_date = str(rows[6].value).strip()
            lock_status = str(rows[7].value).strip()
            send_provider_date = str(rows[8].value).strip()
            cancel_date = str(rows[9].value).strip()
            client_use_date = str(rows[10].value).strip()
            print('{}*{}'.format(phone_number, using_providers))
            # self.fix_pickup_date(phone_number, send_provider_date)
            self.update_phone_number_info(phone_number, using_providers, lock_provider, lock_date,
                                                      open_provider, open_date, lock_status, send_provider_date,
                                                      cancel_date, client_use_date)

    def fix_call_log_wrong1(self):
        from django.utils.timezone import make_aware
        input = ['1716277957.5810315',
                 '1716277954.5810301',
                 '1716277944.5810222',
                 '1716277941.5810194',
                 '1716170284.5528155',
                 '1716169273.5523514',
                 '1714812173.3583208',
                 '1714812171.3583200',
                 '1714725831.3408343',
                 '1714725830.3408330']
        session = requests.Session()
        session.auth = ('ITY', 'Crm1ty@1305Fri')

        print('Processing crm')
        for line in input:
            try:
                callid = line
                url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid={}&fromdate=2024-04-31 00:00:00'.format(
                    callid)
                response = session.get(url)
                # Print the response
                response_json = response.json()
                if len(response_json['cdr']) == 1:
                    data = response_json['cdr'][0]
                    call_log = CallLog.objects.filter(callid=callid, deleted_at__isnull=True).first()
                    if call_log is None:
                        call_log = CallLog(callid=data['callid'], phone=data['phone'],
                                           extension=data['extension'])
                        call_log.direction = CALL_DIRECTION.OUTGOING

                    call_log.calldate = make_aware(datetime.strptime(data['calldate'], '%Y-%m-%d %H:%M:%S'))
                    call_log.duration = int(data['duration'])
                    call_log.billsec = int(data['billsec'])
                    call_log.status = data['status']
                    call_log.recording = data['recordingfile']
                    call_log.accountcode = data['accountcode']
                    call_log.ip = data['ip']
                    call_log.dstchannel = data['dstchannel']
                    call_log.userfield = data['userfield']
                    call_log.extension = data['extension']
                    call_log.phone = data['phone']
                    call_log.provider = classify_telecom_number(call_log.dstchannel)
                    call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
                    call_log.save()
            except Exception as e:
                print('Exception: ' + str(e))




    def handle(self, *args, **options):
        # self.initializer_logger()
        # processing_date = datetime.now(timezone(TIME_ZONE)).date() if options['date'] == '' else datetime.strptime(
        #     options['date'], '%Y%m%d').date()
        #
        # self.process_annual_buy(processing_date)
        # self.calculate_debt_status_order(processing_date)
        # self.notify_renew_date(processing_date)

        self.migrate_phone_number()
        # self.fix_montly_order_detail()
        # self.fix_call_log_wrong()
        # self.init_phone_number_client()
        # self.fix_call_log_missing()
        # self.fix_lock_date_phone_number()
        # self.recalculate_provider()
        # self.fix_dstchannel()
        # self.fix_call_log_wrong()
        # self.migrate_call_log()
        # self.initialize_charge_date()
        # self.fix_annual_order_generation()
        # self.recalculate_order_17()
        # self.reset_order_detail()
        # self.migrate_payments()
        # self.migrate_payment_date()
        # self.migrate_order_detail_payment()
        # self.fix_order_detail_list_in_payment()
