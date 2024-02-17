import json
import math

from api.const import PRICE_TYPE, PARAM_KEY, TELECOM_NUMBER, CALL_CENTER_PAYMENT_METHOD, CALL_CENTER_CHARGE_METHOD
from api.models.package import Package
from api.models.param import Param
import api.utils.cache as cache


def provider_to_price_type(provider):
    if provider == TELECOM_NUMBER.VIETTEL:
        return PRICE_TYPE.VIETTEL

    if provider == TELECOM_NUMBER.MOBI:
        return PRICE_TYPE.MOBIFONE

    if provider == TELECOM_NUMBER.VINA:
        return PRICE_TYPE.VINAPHONE

    return PRICE_TYPE.OTHER


def get_current_fee(type, total_minutes, company_id):
    prices = {"viettel": [{"endAt": "", "unitPrice": 0}],
              "vinaphone": [{"endAt": "", "unitPrice": 0}],
              "mobifone": [{"endAt": "", "unitPrice": 0}],
              "other": [{"endAt": "", "unitPrice": 0}]}

    package = cache.get_package(company_id)
    prices[PRICE_TYPE.VIETTEL] = json.loads(package.viettel)
    prices[PRICE_TYPE.VINAPHONE] = json.loads(package.vinaphone)
    prices[PRICE_TYPE.MOBIFONE] = json.loads(package.mobifone)
    prices[PRICE_TYPE.OTHER] = json.loads(package.other)

    price = prices[type]
    if not price:
        return 0

    if len(price) == 1:
        return price[0]['unitPrice']

    index = 0
    while True:
        if price[index]['endAt'] < total_minutes:
            index += 1
            if price[index]['endAt'] == "":
                return price[index]['unitPrice']
        else:
            break

    return price[index]['unitPrice']


def is_trial(call_center):
    if call_center.payment_method != CALL_CENTER_PAYMENT_METHOD.CREDIT:
        return False

    if call_center.charge_by != CALL_CENTER_CHARGE_METHOD.MINUTE:
        return False

    if call_center.deposit == 0:
        return False

    if call_center.deposit_warning_threshold < 0 or call_center.deposit_warning_threshold > 100:
        return False

    return True


def get_minute_fee(call_center):
    viettel_minute = math.floor((cache.get_call_center_month_minute(call_center.company_id,
                                                              TELECOM_NUMBER.VIETTEL) - 1) / 60) + 1
    mobi_minute = math.floor(
        (cache.get_call_center_month_minute(call_center.company_id, TELECOM_NUMBER.MOBI) - 1) / 60) + 1
    vina_minute = math.floor(
        (cache.get_call_center_month_minute(call_center.company_id, TELECOM_NUMBER.VINA) - 1) / 60) + 1
    other_minute = math.floor(
        (cache.get_call_center_month_minute(call_center.company_id, TELECOM_NUMBER.OTHER) - 1) / 60) + 1

    minute_fee = {TELECOM_NUMBER.VIETTEL: viettel_minute,
                  TELECOM_NUMBER.MOBI: mobi_minute,
                  TELECOM_NUMBER.VINA: vina_minute,
                  TELECOM_NUMBER.OTHER: other_minute}

    minute_fee[TELECOM_NUMBER.VIETTEL] *= get_current_fee(provider_to_price_type(TELECOM_NUMBER.VIETTEL),
                                                          minute_fee[TELECOM_NUMBER.VIETTEL],
                                                          call_center.company_id)
    minute_fee[TELECOM_NUMBER.VINA] *= get_current_fee(provider_to_price_type(TELECOM_NUMBER.VINA),
                                                       minute_fee[TELECOM_NUMBER.VINA],
                                                       call_center.company_id)
    minute_fee[TELECOM_NUMBER.MOBI] *= get_current_fee(provider_to_price_type(TELECOM_NUMBER.MOBI),
                                                       minute_fee[TELECOM_NUMBER.MOBI],
                                                       call_center.company_id)
    minute_fee[TELECOM_NUMBER.OTHER] *= get_current_fee(provider_to_price_type(TELECOM_NUMBER.OTHER),
                                                        minute_fee[TELECOM_NUMBER.OTHER],
                                                        call_center.company_id)
    return minute_fee