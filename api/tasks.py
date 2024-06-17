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
import api.utils.cache as cache
from api.common.cookies import Cookies

from api.const import CALL_DIRECTION
from api.models.call_center import CallLog, CallCenter, CallAgent
from api.models.organization import Company
import api.utils.call_center as call_center_utils
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
    class FakeUser:
        def __int__(self):
            self.is_superuser = True

    def __int__(self):
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
                         userfield, callid):
    call_log = CallLog.objects.filter(callid=callid, phone=phone,
                                      deleted_at__isnull=True).order_by('-created_at')
    if not call_log:
        print('Call log not found')
        return

    print('Running: {}-{}-{}-{}-{}-{}-{}-{}-{}-{}'.format(phone, extension, calldate, duration, status, recording, billsec, accountcode, ip, dstchannel))
    call_log = call_log.first()

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
def fetch_call_log_data(call_log_id):
    try:
        call_log = CallLog.objects.get(pk=call_log_id)

    except CallLog.DoesNotExist:
        print('Not found call log id: ' + str(call_log_id))
