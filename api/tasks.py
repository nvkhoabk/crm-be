"""
Celery tasks
"""
import json
import time
from datetime import datetime

import requests
from celery import shared_task
from celery.result import AsyncResult
from celery.signals import worker_ready
from django.contrib.auth import get_user_model

import api.utils.cache as cache
from api.common.cookies import Cookies

from api.const import CALL_DIRECTION
from api.models.call_center import CallLog, CallCenter, CallAgent
from api.models.organization import Company
import api.utils.call_center as call_center_utils
from api.models.phone_number import PhoneNumberStatus, PhoneNumber, PhoneNumberClient, Legal, Provider, MainPhoneNumber
import api.services.phone_number as update_phone_number
from api.utils.phone import classify_telecom_number
from crm import settings
import redis
from crm.celery import app
from django.utils.timezone import make_aware

# connect to our Redis instance
# redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
#                                    port=settings.REDIS_PORT, db=0)

INTERVAL_WRITE_DATA_KEY = 'interval_write_call_log'
WRITE_DATA_INTERVAL = 100
CALL_LOG_CACHE_NAME = 'call_log_cache'


class FakeRequest:
    user = None

    class FakeUser:
        def __int__(self):
            self.is_superuser = True

    def __int__(self):
        print('Calling user')
        self.user = FakeRequest.FakeUser()


# def bulk_insert_call_logs():
#     call_logs = redis_instance.lrange(CALL_LOG_CACHE_NAME, 0, -1)
#     if call_logs:
#         return
#
#     crm_call_log_list = []
#     for call_log in call_logs:
#         crm_call_log_list.append(CallLog(call_log))
#
#     CallLog.objects.bulk_create(crm_call_log_list)


# @worker_ready.connect
# def start_periodic_task(sender, **kwargs):
#     # Start the periodic task when Celery worker starts
#     print("This task start at init")
#     task_id = interval_write_call_log.apply_async(countdown=WRITE_DATA_INTERVAL)


@shared_task
def interval_write_call_log():
    # bulk_insert_call_logs()
    interval_write_call_log.apply_async(countdown=WRITE_DATA_INTERVAL)


@shared_task
def insert_new_call_log(call_log_str):
    call_log = CallLog(json.load(call_log_str))
    company_id = call_log.status


@shared_task
def get_company_information(id):
    company = Company.objects.get(pk=id)
    print(company.name)


@shared_task
def insert_start_call(type, callid, phone, extension):
    if type == CALL_DIRECTION.INCOMING:
        CallLog.objects.create(callid=callid, phone=phone,
                               extension=extension, direction=CALL_DIRECTION.INCOMING)
    else:
        CallLog.objects.create(callid=callid, phone=phone,
                               extension=extension, direction=CALL_DIRECTION.OUTGOING)


@shared_task
def insert_call_answered(phone, extension, calldate, duration, status, recording, billsec, accountcode, ip, dstchannel,
                         userfield, callid, direction):
    print('Running: {}-{}-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(phone, extension, calldate, duration, status, recording,
                                                             billsec, accountcode, ip, dstchannel, direction))

    call_log = CallLog.objects.filter(callid=callid, phone=phone,
                                      deleted_at__isnull=True).order_by('-created_at')
    if not call_log:
        call_log = CallLog()
    else:
        call_log = call_log.first()

    if direction == CALL_DIRECTION.OUTGOING:
        call_log.direction = CALL_DIRECTION.OUTGOING
    else:
        call_log.direction = CALL_DIRECTION.INCOMING

    call_log.callid = callid
    call_log.calldate = make_aware(datetime.strptime(calldate, '%Y-%m-%d %H:%M:%S'))
    call_log.duration = int(duration)
    call_log.status = status
    call_log.recording = recording
    call_log.billsec = int(billsec)
    call_log.accountcode = accountcode
    call_log.ip = ip
    call_log.dstchannel = dstchannel
    call_log.userfield = userfield
    call_log.provider = classify_telecom_number(call_log.dstchannel)
    call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
    call_log.save()

    if cache.get_ext_company(call_log.extension) == 0:
        request = FakeRequest()
        cookies = Cookies()
        call_center_utils.handle_new_extension(call_log.extension, call_log.accountcode, request, cookies)

        # recalculate chargeable_time because company is not existed in previous time
        call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
        call_log.save()

    if call_log.direction == CALL_DIRECTION.OUTGOING and call_log.chargeable_time > 0:
        cache.update_call_center_month_minute(call_log)


@shared_task
def insert_to_queue_phone_number(request_phone_number, company_name, number_in_distributor, number_left,
                                 distributor_name, lock_telco, proxy):
    company = Company.objects.filter(name__iexact=company_name, deleted_at__isnull=True).first()
    if not company:
        return

    phone_number = PhoneNumber.objects.filter(phone_number__iexact=request_phone_number, company_id=company.id,
                                              deleted_at__isnull=True).first()
    if not phone_number:
        main_phone_number = MainPhoneNumber.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                                           deleted_at__isnull=True).first()
        provider = Provider.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                           deleted_at__isnull=True).first()
        legal = Legal.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                     deleted_at__isnull=True).first()
        phone_number_client = PhoneNumberClient.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                                               deleted_at__isnull=True).first()
        phone_number_status = PhoneNumberStatus.objects.filter(name__iexact='Không xác định', company_id=company.id,
                                                               deleted_at__isnull=True).first()

        if not main_phone_number or not provider or not legal or not phone_number_client or not phone_number_status:
            return

        phone_number = PhoneNumber.objects.create(company=company,
                                                  phone_number=request_phone_number,
                                                  main_phone_number=main_phone_number,
                                                  provider=provider,
                                                  legal=legal,
                                                  phone_number_client=phone_number_client,
                                                  phone_number_status=phone_number_status,
                                                  pickup_date=datetime.now(),
                                                  brand='',
                                                  lock_provider='{"Viettel": false, "Mobifone": false, "Vinaphone": false, "Other": false}',
                                                  lock_count=0,
                                                  phone_number_avg_age=0,
                                                  cancel_date=None,
                                                  init_payment_date=None,
                                                  open_payment_date=None,
                                                  operate_payment_date=None,
                                                  other_payment_date=None,
                                                  number_in_distributor=number_in_distributor,
                                                  number_left=number_left,
                                                  distributor_name=distributor_name,
                                                  lock_telco=lock_telco,
                                                  proxy=proxy)
    else:
        phone_number.number_in_distributor = number_in_distributor
        phone_number.number_left = number_left
        phone_number.distributor_name = distributor_name
        phone_number.lock_telco = lock_telco
        phone_number.proxy = proxy

    phone_number.set_lock_provider(lock_telco)
    phone_number.save()
    phone_number_status = PhoneNumberStatus.objects.filter(name__iexact='Đang nghi ngờ', company_id=company.id,
                                                           deleted_at__isnull=True).first()
    if not phone_number_status:
        return
    phone_number.phone_number_status = phone_number_status
    request = FakeRequest()
    User = get_user_model()
    root_user = User.objects.get(username__iexact='root')
    if request.user is None:
        request.user = root_user
    else:
        request.user.is_superuser = True
        request.user.id = root_user.id
    service = update_phone_number.UpdatePhoneNumberService()

    cookies = Cookies()
    # User = get_user_model()
    # root_user = User.objects.get(username__iexact='root')
    # request.user.is_superuser = True
    # request.user.id = root_user.id

    service.serve(request, cookies, *vars(phone_number), **vars(phone_number))


@shared_task
def fetch_call_log_data(call_log_id):
    try:
        call_log = CallLog.objects.get(pk=call_log_id)

    except CallLog.DoesNotExist:
        print('Not found call log id: ' + str(call_log_id))
