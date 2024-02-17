"""
Celery tasks
"""
import json
import time

import requests
from celery import shared_task
from celery.result import AsyncResult
from celery.signals import worker_ready

from api.models.call_center import CallLog
from api.models.organization import Company
from crm import settings
import redis
from crm.celery import app

# connect to our Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)

INTERVAL_WRITE_DATA_KEY = 'interval_write_call_log'
WRITE_DATA_INTERVAL = 100
CALL_LOG_CACHE_NAME = 'call_log_cache'


def bulk_insert_call_logs():
    call_logs = redis_instance.lrange(CALL_LOG_CACHE_NAME, 0, -1)
    if call_logs:
        return

    crm_call_log_list = []
    for call_log in call_logs:
        crm_call_log_list.append(CallLog(call_log))

    CallLog.objects.bulk_create(crm_call_log_list)

@worker_ready.connect
def start_periodic_task(sender, **kwargs):
    # Start the periodic task when Celery worker starts
    print("This task start at init")
    task_id = interval_write_call_log.apply_async(countdown=WRITE_DATA_INTERVAL)


@shared_task
def interval_write_call_log():
    #bulk_insert_call_logs()
    interval_write_call_log.apply_async(countdown=WRITE_DATA_INTERVAL)


@shared_task
def insert_new_call_log(call_log_str):
    call_log = CallLog(json.load(call_log_str))
    company_id = call_log.status

@shared_task
def get_company_information(id):
    company = Company.objects.get(pk=id)
    print(company.name)



