import datetime

import json

from dateutil.relativedelta import relativedelta
from django.core.cache import cache

from api.const import TELECOM_NUMBER, CALL_AGENT_STATUS, PARAM_KEY, CACHE_KEY, CALL_DIRECTION
from api.models.call_center import CallAgent, CallLog, CallCenter
from api.models.package import Package
from api.models.param import Param
import api.utils.call_center as call_center_utils
from api.utils.date import get_first_of_month, get_last_of_month


def init_ext_company():
    call_agents = CallAgent.objects.filter(deleted_at__isnull=True)
    call_agent_cache = dict()
    for call_agent in call_agents:
        call_agent_cache[call_agent.name] = call_agent.company_id

    cache.set(CACHE_KEY.COMPANY_EXTENSION, call_agent_cache)
    return call_agent_cache


def get_ext_company(ext):
    company_extension_cache = cache.get(CACHE_KEY.COMPANY_EXTENSION, None)
    if company_extension_cache is None:
        company_extension_cache = init_ext_company()

    if ext not in company_extension_cache:
        return 0

    return company_extension_cache[ext]


def init_package():
    packages = Package.objects.filter(deleted_at__isnull=True)
    package_cache = dict()
    for package in packages:
        package_cache[package.company_id] = package

    cache.set(CACHE_KEY.PACKAGE, package_cache)

    general_package = Param.objects.get(key=PARAM_KEY.GENERAL_PACKAGE)
    config_price = json.loads(general_package.value)
    package = Package(viettel=json.dumps(config_price['viettel']),
                      vinaphone=json.dumps(config_price['vinaphone']),
                      mobifone=json.dumps(config_price['mobifone']),
                      other=json.dumps(config_price['other']))
    cache.set(CACHE_KEY.GENERAL_PACKAGE, package)
    return package_cache


def update_package_from_db(company_id=None):
    if company_id:
        package_cache = cache.get(CACHE_KEY.PACKAGE, None)
        if package_cache is None:
            return False

        package = Package.objects.filter(deleted_at__isnull=True, company_id=company_id)
        if package:
            package_cache[company_id] = package.first()
            cache.set(CACHE_KEY.PACKAGE, package_cache)
            return True
    else:
        general_package = Param.objects.get(key=PARAM_KEY.GENERAL_PACKAGE)
        config_price = json.loads(general_package.value)
        package = Package(viettel=json.dumps(config_price['viettel']),
                          vinaphone=json.dumps(config_price['vinaphone']),
                          mobifone=json.dumps(config_price['mobifone']),
                          other=json.dumps(config_price['other']))
        cache.set(CACHE_KEY.GENERAL_PACKAGE, package)
        return True

    return False


def get_package(company_id):
    package_cache = cache.get(CACHE_KEY.PACKAGE, None)
    if package_cache is None:
        package_cache = init_package()

    if company_id not in package_cache:
        if update_package_from_db(company_id):
            return cache.get(CACHE_KEY.PACKAGE)[company_id]

    return cache.get(CACHE_KEY.GENERAL_PACKAGE)


def _init_call_center_minute_month(month, cache_key):
    first_of_month = get_first_of_month(month)
    last_of_month = get_last_of_month(month)
    call_logs = CallLog.objects.filter(deleted_at__isnull=True, calldate__gte=first_of_month,
                                       calldate__lte=last_of_month, chargeable_time__gt=0,
                                       direction=CALL_DIRECTION.OUTGOING)
    call_center_minute = dict()
    for call_log in call_logs:
        company_id = get_ext_company(call_log.extension)
        if company_id not in call_center_minute:
            call_center_minute[company_id] = {
                TELECOM_NUMBER.VIETTEL: 0,
                TELECOM_NUMBER.VINA: 0,
                TELECOM_NUMBER.MOBI: 0,
                TELECOM_NUMBER.OTHER: 0
            }

        call_center_minute[company_id][call_log.provider] += call_log.chargeable_time

    cache.set(cache_key, call_center_minute)
    return call_center_minute


def update_call_center_minute_from_db(company_id, month, cache_key):
    ext_list = CallAgent.objects.filter(company_id=company_id, deleted_at__isnull=True,
                                        status=CALL_AGENT_STATUS.ACTIVE).values_list('name', flat=True)

    first_of_month = get_first_of_month(month)
    last_of_month = get_last_of_month(month)
    call_logs = CallLog.objects.filter(deleted_at__isnull=True, calldate__gte=first_of_month,
                                       calldate__lte=last_of_month,
                                       extension__in=ext_list, direction=CALL_DIRECTION.OUTGOING, chargeable_time__gt=0)
    call_center_minute = cache.get(cache_key, None)
    call_center_minute[company_id] = {
        TELECOM_NUMBER.VIETTEL: 0,
        TELECOM_NUMBER.VINA: 0,
        TELECOM_NUMBER.MOBI: 0,
        TELECOM_NUMBER.OTHER: 0
    }

    for call_log in call_logs:
        call_center_minute[company_id][call_log.provider] += call_log.chargeable_time

    cache.set(cache_key, call_center_minute)
    return call_center_minute


def get_call_center_month_minute(company_id, provider):
    call_center_minute_cache = cache.get(CACHE_KEY.CALL_CENTER_MINUTE, None)
    if call_center_minute_cache is None:
        call_center_minute_cache = _init_call_center_minute_month(datetime.datetime.now(), CACHE_KEY.CALL_CENTER_MINUTE)

    if company_id not in call_center_minute_cache:
        update_call_center_minute_from_db(company_id, datetime.datetime.now(), CACHE_KEY.CALL_CENTER_MINUTE)
        call_center_minute_cache = cache.get(CACHE_KEY.CALL_CENTER_MINUTE, None)

    return call_center_minute_cache[company_id][provider]


def get_call_center_last_month_minute(company_id, provider):
    call_center_minute_cache = cache.get(CACHE_KEY.LAST_MONTH_CALL_CENTER_MINUTE, None)
    if call_center_minute_cache is None:
        call_center_minute_cache = _init_call_center_minute_month(datetime.datetime.now() - relativedelta(months=1),
                                                                  CACHE_KEY.LAST_MONTH_CALL_CENTER_MINUTE)

    if company_id not in call_center_minute_cache:
        update_call_center_minute_from_db(company_id, datetime.datetime.now() - relativedelta(months=1),
                                          CACHE_KEY.LAST_MONTH_CALL_CENTER_MINUTE)
        call_center_minute_cache = cache.get(CACHE_KEY.LAST_MONTH_CALL_CENTER_MINUTE, None)

    return call_center_minute_cache[company_id][provider]


def _warning_deposit_threshold(company_id):
    call_center = CallCenter.objects.get(company_id=company_id, deleted_at__isnull=True)

    if not call_center_utils.is_trial(call_center):
        return

    minute_fee = call_center_utils.get_minute_fee(call_center)
    total = minute_fee[TELECOM_NUMBER.VIETTEL] + minute_fee[TELECOM_NUMBER.MOBI] + minute_fee[TELECOM_NUMBER.VINA] + \
            minute_fee[TELECOM_NUMBER.OTHER]

    if total >= call_center.deposit:
        call_center.trial_expired = True
        call_center.save()
    elif call_center.trial_expired:
        call_center.trial_expired = False
        call_center.save()

    if (total * 100 / call_center.deposit) >= call_center.deposit_warning_threshold:
        call_center.trial_warning = True
        call_center.save()
    elif call_center.trial_warning:
        call_center.trial_warning = False
        call_center.save()


def call_center_deposit_changed(company_id):
    _warning_deposit_threshold(company_id)


def update_call_center_month_minute(call_log):
    company_id = get_ext_company(call_log.extension)
    month_minute = get_call_center_month_minute(company_id, call_log.provider) + call_log.chargeable_time

    call_center_minute_cache = cache.get(CACHE_KEY.CALL_CENTER_MINUTE, None)
    call_center_minute_cache[company_id][call_log.provider] = month_minute
    cache.set(CACHE_KEY.CALL_CENTER_MINUTE, call_center_minute_cache)

    _warning_deposit_threshold(company_id)
    return month_minute


def reset_call_center_cache():
    cache.delete(CACHE_KEY.CALL_CENTER_MINUTE)
    cache.delete(CACHE_KEY.LAST_MONTH_CALL_CENTER_MINUTE)


def log_error(mess):
    error_cache = cache.get(CACHE_KEY.ERROR, [])
    cache.set(CACHE_KEY.ERROR, error_cache)
