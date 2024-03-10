import json
import math
from datetime import datetime

from api.const import PRICE_TYPE, PARAM_KEY, TELECOM_NUMBER, CALL_CENTER_PAYMENT_METHOD, CALL_CENTER_CHARGE_METHOD, \
    CALL_AGENT_STATUS
from api.models.call_center import AgentRegister, CallAgent, CallCenter
from api.models.organization import Company
from api.models.package import Package
from api.models.param import Param
import api.utils.cache as cache
import api.services.call_center as call_center_api
import api.services.manage as manage


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


def is_company_created(companies, accountcode):
    for company in companies:
        if company.name == accountcode:
            return company

    return None


def handle_new_extension(extension, accountcode, request, cookies):
    company_name = accountcode + '_call_center_only'
    companies = Company.objects.filter(deleted_at__isnull=True, name=company_name)
    company = None
    if companies:
        company = is_company_created(companies, company_name)

    if company is None:
        company = create_company(company_name, request, cookies)
        create_company_admin(company, request, cookies)
        create_call_center(company, request, cookies)

    ag = AgentRegister.objects.create(company=company, number=1, use_from=datetime.now(), use_to=datetime.now(),
                                      charge_from=datetime.now(), charge_to=datetime.now())
    CallAgent.objects.create(company_id=company.id, name=extension,
                             secret=extension,
                             agent_register_id=ag.id,
                             status=CALL_AGENT_STATUS.ACTIVE)

    cache.init_ext_company()


def create_call_center(company, request, cookies):
    data = {
        "company_id": company.id,
        "charge_by": "MINUTE",
        "payment_method": "CREDIT",
        "payment_date": "2023-12-08",
        "payment_notify": "2023-12-01",
        "agent_fee": 0,
        "minute_fee": {
            "Viettel": 0,
            "Mobi": 0,
            "Vina": 0
        },
        "external_fee": 0,
        "sip_fee_calculation": "6+1",
        "is_enable": True,
        "discount_type": "VALUE",
        "discount_value": 0,
        "payment_start_date": "2023-02-01",
        "payment_status": "UNPAID",
        "total_payment_amount": 0,
        "credit_payment_amount": 0,
        "external_payment_amount": 0,
        "discount_amount": 0,
        "deposit": 0,
        "deposit_warning_threshold": 0,
        "trial_warning": False,
        "trial_expired": False
    }
    service = call_center_api.CreateCallCenterService()
    service.serve(request, cookies, *[], **data)


def create_company(name, request, cookies):
    # Create company
    data = {
        'name': name,
        'type': name,
        'owner': name,
        'phone': '',
    }

    service = manage.CreateCompanyService()
    service.serve(request, cookies, *name, **data)
    company = Company.objects.get(name=name, deleted_at__isnull=True)
    return company


def create_company_admin(company, request, cookies):
    data = {
        'company_id': company.id,
        'username': company.name,
        'password': 'forC@llcent3r' + company.name,
    }

    request.user.is_superuser = True
    service = manage.CreateUserService()
    service.serve(request, cookies, *[], **data)


def calculate_by_6_1(duration):
    return duration if duration > 6 else 6


def calculate_by_60_1(duration):
    return 60 * (math.floor((duration - 1) / 60) + 1)


def calculate_chargeable_time(call_log):
    if call_log.billsec == 0:
        return 0
    try:
        company_id = cache.get_ext_company(call_log.extension)

        call_center = CallCenter.objects.get(company_id=company_id)
        if call_center.sip_fee_calculation == '6+1':
            return calculate_by_6_1(call_log.billsec)

        if call_center.sip_fee_calculation == '60+1':
            return calculate_by_60_1(call_log.billsec)

    except CallAgent.DoesNotExist:
        return 0
    except CallCenter.DoesNotExist:
        return 0
    return 0