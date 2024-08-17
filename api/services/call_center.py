import csv
import json
import math
import mimetypes
from urllib import parse
from wsgiref.util import FileWrapper
from datetime import datetime
import pandas as pd

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import IntegrityError, transaction
from django.http import HttpResponse, FileResponse
from django.utils import timezone
import api.utils.cache as cache

from api.common.common import Common
from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import CALL_DIRECTION, TELECOM_NUMBER, DISCOUNT_TYPE, PAYMENT_STATUS, CALL_AGENT_STATUS, PARAM_KEY, \
    PRICE_TYPE, CALL_CENTER_PAYMENT_METHOD, CALL_CENTER_CHARGE_METHOD
from api.models.call_center import CallCenter, CallAgent, AgentRegister, CallCenterPaymentHistory, \
    CallLog, ExtFileHistory, ExportCallLogsHistory
from api.models.organization import Company, UserRole
import api.serializers.call_center_serializer as call_center_serial
from api.services.exceptions import (CallCenterDuplicated, CallCenterNotFound, ManageCompanyNotFound, CallAgentNotFound,
                                     AgentRegisterNotFound, CallLogNotFound, CallCenterPaymentNotDue,
                                     ReportNotFound, NumberAgentRegisterNotMatch, TrialExpired)
import api.services.manage as manage
from api.tasks import insert_call_answered, fetch_call_log_data
import api.utils.call_center as call_center_utils
from api.utils.date import get_first_of_month, get_last_of_month
from api.utils.order_detail import floor_rate
from api.utils.phone import classify_telecom_number
from crm.settings import MEDIA_ROOT

User = get_user_model()


def is_external_number(number):
    if len(number) == 10:
        return number[0:2] == '02' or number[0:2] == '05'

    if len(number) == 11:
        return number[0:2] == '02' or number[0:3] == '080' or number[0:3] == '087' or number[
                                                                                      0:3] == '092' or number[
                                                                                                       0:3] == '099'
    return False


class CreateCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        with transaction.atomic():
            try:
                Company.objects.get(pk=kwargs['company_id'])
                if kwargs.get('minute_fee') is not None:
                    kwargs['minute_fee'] = json.dumps(kwargs.get('minute_fee')).replace("'", "\"")
                call_center = CallCenter.objects.create(**kwargs)
                cache.update_package_from_db(call_center.company_id)
                return call_center
            except IntegrityError as e:
                raise CallCenterDuplicated()
            except Company.DoesNotExist:
                raise ManageCompanyNotFound()


class EnableCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])
            call_center.is_enable = True
            call_center.save()

            call_agents = CallAgent.objects.filter(company_id=kwargs['company_id'])

            for agent in call_agents:
                agent.status = CALL_AGENT_STATUS.ACTIVE

            call_agents.bulk_update(call_agents, fields=['status'])

            return call_center
        except CallCenter.DoesNotExist as e:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class DisableCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])
            call_center.is_enable = False
            call_center.save()

            call_agents = CallAgent.objects.filter(company_id=kwargs['company_id'])

            for agent in call_agents:
                agent.status = CALL_AGENT_STATUS.INACTIVE

            call_agents.bulk_update(call_agents, fields=['status'])
            return call_center
        except CallCenter.DoesNotExist as e:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class CalculatePaymentCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        call_center_list = CallCenter.objects.filter(deleted_at__isnull=True, is_enable=True)
        start_date = get_first_of_month(datetime.now())
        end_date = datetime.now()

        for call_center in call_center_list:
            payment_calculator = CallCenterPaymentCalculatorService(call_center, start_date, end_date)
            payment_calculator.calculate()
            call_center.total_payment_amount = payment_calculator.get_total_payment_amount()
            call_center.credit_payment_amount = payment_calculator.get_credit_payment_amount()
            call_center.external_payment_amount = payment_calculator.get_external_payment_amount()
            call_center.discount_amount = payment_calculator.get_discount_amount()
            call_center.updated_at = timezone.now()

        CallCenter.objects.bulk_update(call_center_list, fields=['total_payment_amount', 'credit_payment_amount',
                                                                 'external_payment_amount', 'discount_amount',
                                                                 'updated_at'])


class GetCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            return CallCenter.objects.get(company_id=kwargs['company_id'])
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class FilterCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = CallCenter.objects.filter(deleted_at__isnull=True)

        filters = ['company_id', 'charge_by', 'payment_method', 'sip_fee_calculation', 'discount_type', 'from_date',
                   'to_date']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id' and value is not None:
                query_set = query_set.filter(
                    company_id=value,
                )
            if key == 'charge_by' and value is not None:
                query_set = query_set.filter(
                    charge_by=value,
                )
            if key == 'payment_method' and value is not None:
                query_set = query_set.filter(
                    payment_method=value,
                )
            if key == 'sip_fee_calculation' and value is not None:
                query_set = query_set.filter(
                    sip_fee_calculation=value,
                )
            if key == 'discount_type' and value is not None:
                query_set = query_set.filter(
                    discount_type=value,
                )
            if key == 'from_date' and value is not None:
                query_set = query_set.filter(
                    payment_date__gte=value
                )
            if key == 'to_date' and value is not None:
                query_set = query_set.filter(
                    payment_date__lte=value
                )

        return query_set


class UpdateCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            old_call_center = CallCenter.objects.get(company_id=kwargs['company_id'])
            CallCenter.objects.filter(company_id=kwargs['company_id']).update(**kwargs)
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])
            # if kwargs.get('charge_by'):
            #     call_center.charge_by = kwargs.get('charge_by')
            #
            # if kwargs.get('payment_method'):
            #     call_center.payment_method = kwargs.get('payment_method')
            #
            # if kwargs.get('payment_date'):
            #     call_center.payment_date = kwargs.get('payment_date')
            #
            # if kwargs.get('payment_notify'):
            #     call_center.payment_notify = kwargs.get('payment_notify')
            #
            # if kwargs.get('agent_fee'):
            #     call_center.agent_fee = kwargs.get('agent_fee')
            #
            # if kwargs.get('minute_fee'):
            #     call_center.minute_fee = json.dumps(kwargs.get('minute_fee')).replace("'", "\"")
            #
            # if kwargs.get('external_fee'):
            #     call_center.external_fee = kwargs.get('external_fee')
            #
            # if kwargs.get('sip_fee_calculation'):
            #     call_center.sip_fee_calculation = kwargs.get('sip_fee_calculation')
            #
            # if kwargs.get('discount_type'):
            #     call_center.discount_type = kwargs.get('discount_type')
            #     call_center.discount_value = 0
            #
            # if kwargs.get('discount_value', None) is not None:
            #     call_center.discount_value = kwargs.get('discount_value')
            #
            # if kwargs.get('payment_start_date'):
            #     call_center.payment_start_date = kwargs.get('payment_start_date')
            #
            # if kwargs.get('deposit_warning_threshold'):
            #     call_center.deposit_warning_threshold = kwargs.get('deposit_warning_threshold')
            #
            # if kwargs.get('deposit'):
            #     call_center.deposit = kwargs.get('deposit')

            if kwargs.get('payment_status') and kwargs.get('payment_status') == PAYMENT_STATUS.PAID:
                self.pay_call_center(call_center, old_call_center)

            if call_center.deposit == 0 or call_center.deposit_warning_threshold == 0:
                call_center.trial_expired = False
                call_center.trial_warning = False

            call_center.save()

            if call_center.deposit != old_call_center.deposit or \
                    call_center.deposit_warning_threshold != old_call_center.deposit_warning_threshold:
                cache.call_center_deposit_changed(call_center.company_id)

            return call_center

        except CallCenter.DoesNotExist as e:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()

    def pay_call_center(self, call_center, old_call_center):
        if timezone.now().date() < get_first_of_month(old_call_center.payment_date):
            raise CallCenterPaymentNotDue()

        CallCenterPaymentHistory.objects.create(company_id=old_call_center.company_id,
                                                charge_by=old_call_center.charge_by,
                                                payment_method=old_call_center.payment_method,
                                                payment_date=old_call_center.payment_date,
                                                payment_notify=old_call_center.payment_notify,
                                                agent_fee=old_call_center.agent_fee,
                                                minute_fee=old_call_center.minute_fee,
                                                external_fee=old_call_center.external_fee,
                                                sip_fee_calculation=old_call_center.sip_fee_calculation,
                                                discount_type=old_call_center.discount_type,
                                                discount_value=old_call_center.discount_value,
                                                is_enable=old_call_center.is_enable,
                                                payment_start_date=old_call_center.payment_start_date,
                                                payment_status=PAYMENT_STATUS.PAID)


class GetAgentsService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        return CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True,
                                        status=CALL_AGENT_STATUS.ACTIVE)


class UpdateAgentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            call_agents = []
            for updating_value in kwargs.get('data'):
                call_agent = CallAgent.objects.get(pk=updating_value['id'])
                call_agent.user_id = updating_value['user_id']
                call_agent.save()
                call_agents.append(call_agent)
                cache.init_ext_company()

            return call_agents
        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()


class GetCompanyCallHistoryService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)
            from_date = kwargs['filter']['from_date'].strftime('%Y-%m-%d')
            to_date = (kwargs['filter']['to_date'] + relativedelta(days=1)).strftime('%Y-%m-%d')

            call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
            call_logs = CallLog.objects.filter(calldate__gte=from_date, calldate__lt=to_date).order_by('-created_at')

            filters = ['number', 'user_id']
            params = dict(kwargs.get('filter', []))
            for key, value in params.items():
                if key not in filters:
                    continue

                if key == 'number' and value is not None:
                    call_logs = call_logs.filter(
                        phone__icontains=value
                    )

                if key == 'user_id' and value is not None:
                    call_agents = call_agents.filter(
                        user_id=value,
                    )

            call_logs = call_logs.filter(extension__in=call_agents.values_list('name', flat=True))
            if 'call_status' in params and params['call_status']:
                call_logs = call_logs.filter(status__icontains=params['call_status'])

            call_history_list = []
            for call_log in call_logs:
                call_history_list.append({
                    'dest_number': call_log.phone,
                    'calldate': call_log.calldate,
                    'record_url': call_log.recording,
                    'direction': call_log.direction,
                    'duration': call_log.billsec
                })

            return call_history_list

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()


class GetUserCallHistoryService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        phone_number = kwargs['phone_number']
        user_roles = UserRole.objects.filter(**filter)

        call_agent = CallAgent.objects.filter(user_id=user_roles.first().user_id, deleted_at__isnull=True,
                                              status=CALL_AGENT_STATUS.ACTIVE)
        if not call_agent:
            raise CallAgentNotFound()

        call_agent = call_agent.first()

        call_logs = []
        if phone_number is not None and phone_number != "":
            call_logs = CallLog.objects.filter(extension=call_agent.name, phone__icontains=phone_number).order_by(
                '-created_at')
        else:
            call_logs = CallLog.objects.filter(extension=call_agent.name).order_by('-created_at')

        call_history_list = []
        for call_log in call_logs:
            call_history_list.append({
                'id': call_log.id,
                'dest_number': call_log.phone,
                'calldate': call_log.calldate,
                'record_url': call_log.recording,
                'direction': call_log.direction,
                'duration': call_log.billsec
            })

        return call_history_list


class GetCallReportService(BaseService):
    def __init__(self):
        self.report = dict()

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)
        from_date = kwargs['filter']['from_date'].strftime('%Y-%m-%d')
        to_date = (kwargs['filter']['to_date'] + relativedelta(days=1)).strftime('%Y-%m-%d')

        call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
        self.init_call_report(call_agents)

        call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                           created_at__gte=from_date, created_at__lt=to_date, status__isnull=False)
        if 'call_status' in kwargs['filter'] and kwargs['filter']['call_status']:
            call_logs = call_logs.filter(status__icontains=kwargs['filter']['call_status'])

        call_history_list = []
        for call_log in call_logs:
            call_history_list.append({
                'ext': call_log.extension,
                'dest_number': call_log.phone,
                'calldate': call_log.calldate,
                'record_url': call_log.recording,
                'direction': call_log.direction,
                'duration': call_log.billsec
            })

        self.process_call_report(call_history_list)
        return list(self.report.values())

    def init_call_report(self, call_agents):
        for call_agent in call_agents:
            self.report[call_agent.name] = {
                'agent_name': call_agent.name,
                'number_call_out': 0,
                'duration_call_out': 0,
                'number_call_in': 0,
                'duration_call_in': 0,
                'total_duration': 0
            }

    def process_call_report(self, call_history):
        for history in call_history:
            if history['direction'] == 'outgoing':
                self.report[history['ext']]['number_call_out'] += 1
                self.report[history['ext']]['duration_call_out'] += history['duration']

            if history['direction'] == 'incoming':
                self.report[history['ext']]['number_call_in'] += 1
                self.report[history['ext']]['duration_call_in'] += history['duration']

            self.report[history['ext']]['total_duration'] += history['duration']


class CreateAgentRegisterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            return AgentRegister.objects.create(**kwargs)
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class DeleteAgentRegisterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            agent_register = AgentRegister.objects.get(pk=kwargs['id'])
            agent_register.deleted_at = datetime.now()
            agent_register.save()
        except AgentRegister.DoesNotExist:
            raise AgentRegisterNotFound()


class FilterAgentRegisterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = AgentRegister.objects.all()

        filters = ['company_id']
        params = dict(kwargs.get('filter', []))

        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'company_id':
                query_set = query_set.filter(
                    company_id=value, deleted_at__isnull=True
                )

        return query_set


class GetExternalPaymentReportService(BaseService):
    def __init__(self):
        self.report = list()

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            from_date = timezone.now()
            to_date = timezone.now()

            call_center = CallCenter.objects.get(company_id=user_roles.first().company_id, deleted_at__isnull=True)

            if kwargs['report_type'] == 'CURRENT_MONTH':
                # call_center = CallCenter.objects.get(company_id=user_roles.first().company_id, deleted_at__isnull=True)
                # from_date = call_center.payment_start_date
                # to_date = call_center.payment_date
                from_date = get_first_of_month(timezone.now())
                to_date = get_last_of_month(timezone.now())

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                # call_center = CallCenterPaymentHistory.objects.filter(
                #     company_id=user_roles.first().company_id, deleted_at__isnull=True).order_by('-id').first()
                # from_date = call_center.payment_start_date
                # to_date = call_center.payment_date
                from_date = get_first_of_month(timezone.now() - relativedelta(months=1))
                to_date = get_last_of_month(timezone.now() - relativedelta(months=1))

            call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
            call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                               calldate__gte=from_date, calldate__lte=to_date,
                                               provider=kwargs.get('provider', None),
                                               direction=CALL_DIRECTION.OUTGOING).order_by('created_at')

            call_history_list = []
            for call_log in call_logs:
                call_history_list.append({
                    'number': call_log.phone,
                    'call_date': call_log.calldate,
                    'duration': call_log.billsec,
                    'fee': call_center.external_fee if call_center is not None else 0,
                    'chargeable_time': call_log.chargeable_time
                })

            return call_history_list

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except CallCenterPaymentHistory.DoesNotExist:
            raise CallCenterNotFound()


class GetCreditPaymentReportService(BaseService):
    def __init__(self):
        self.report = list()

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)
                company_id = user_roles.first().company_id
            else:
                company_id = kwargs.get('company_id', 0)

            start_date = None
            end_date = None
            call_center = CallCenter.objects.get(company_id=company_id, deleted_at__isnull=True)

            if kwargs['report_type'] == 'CURRENT_MONTH':
                start_date = get_first_of_month(datetime.now())
                end_date = datetime.now()

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                start_date = get_first_of_month(datetime.now() - relativedelta(months=1))
                end_date = get_last_of_month(start_date)

            if call_center is None:
                raise ReportNotFound()
            payment_calculator = CallCenterPaymentCalculatorService(call_center, start_date, end_date, last_month=(
                        kwargs['report_type'] == 'PREVIOUS_MONTH'))
            payment_calculator.calculate()

            return {
                'credit_payment_amount': payment_calculator.get_credit_payment_amount(),
                'external_payment_amount': payment_calculator.get_external_payment_amount(),
                'payment_method': call_center.payment_method,
                'payment_date': call_center.payment_date,
                'discount_amount': payment_calculator.get_discount_amount(),
                'discount_type': call_center.discount_type,
                'discount_value': call_center.discount_value,
                'total_payment_amount': payment_calculator.get_total_payment_amount(),
                'charge_type': call_center.charge_by,
                'current_prices': payment_calculator.get_current_prices(),
                'current_minutes': payment_calculator.get_current_minutes(),
                'status': 'UNPAID'
            }

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except CallCenterPaymentHistory.DoesNotExist:
            raise CallCenterNotFound()


class IncomingCallService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            call_log = CallLog(callid=request.GET.get('callid', None), phone=request.GET.get('phone', None),
                               extension=request.GET.get('extension', None))
            call_log.direction = CALL_DIRECTION.INCOMING
            call_log.save()
            return call_log
        except Exception as e:
            cache.log_error(request.GET.get('callid', 'None_callid') + '_' + str(e))


class OutgoingCallService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            call_log = CallLog(callid=request.GET.get('callid', None), phone=request.GET.get('phone', None),
                               extension=request.GET.get('extension', None))
            call_log.direction = CALL_DIRECTION.OUTGOING
            call_log.save()
            return call_log
        except Exception as e:
            cache.log_error(request.GET.get('callid', 'None_callid') + '_' + str(e))


class CallAnsweredService(BaseService):
    def serve_get(self, request, cookies: Cookies, *args, **kwargs):
        try:
            phone = parse.unquote(request.GET.get('phone', None))
            extension = parse.unquote(request.GET.get('extension', None))
            calldate = parse.unquote(request.GET.get('calldate', None))
            duration = parse.unquote(request.GET.get('duration', None))
            status = parse.unquote(request.GET.get('status', None))
            recording = parse.unquote(request.GET.get('recording', None))
            billsec = parse.unquote(request.GET.get('billsec', 0))
            accountcode = parse.unquote(request.GET.get('accountcode', ''))
            ip = parse.unquote(request.GET.get('ip', ''))
            dstchannel = parse.unquote(request.GET.get('dstchannel', ''))
            userfield = parse.unquote(request.GET.get('userfield', ''))
            callid = request.GET.get('callid', '')

            insert_call_answered.delay(phone, extension, calldate, duration, status, recording, billsec, accountcode,
                                       ip, dstchannel, userfield, callid)
        except Exception as e:
            cache.log_error(request.GET.get('callid', 'None_callid') + '_' + str(e))

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            extension = kwargs.get('extension', None)
            accountcode = kwargs.get('accountcode', '')

            # if cache.get_ext_company(extension) == 0:
            #     self.handle_new_extension(extension, accountcode, request, cookies)

                # recalculate chargeable_time because company is not existed in previous time
                # call_log.chargeable_time = self.calculate_chargeable_time(call_log)
                # call_log.save()

            insert_call_answered.delay(kwargs.get('phone', None), kwargs.get('extension', None),
                                        kwargs.get('calldate', None), kwargs.get('duration', None),
                                        kwargs.get('status', None), kwargs.get('recording', None),
                                        kwargs.get('billsec', 0), kwargs.get('accountcode', ''),
                                        kwargs.get('ip', ''), kwargs.get('dstchannel', ''),
                                        kwargs.get('userfield', ''), request.GET.get('callid', ''))
            # call_log = CallLog.objects.filter(extension=kwargs.get('extension', None), phone=kwargs.get('phone', None),
            #                                   status__isnull=True).order_by('-created_at')
            # if not call_log:
            #     raise CallLogNotFound()
            #
            # call_log = call_log.first()
            #
            # call_log.calldate = kwargs.get('calldate', None)
            # call_log.duration = kwargs.get('duration', None)
            # call_log.status = kwargs.get('status', None)
            # call_log.recording = kwargs.get('recording', None)
            # call_log.billsec = kwargs.get('billsec', 0)
            # call_log.accountcode = kwargs.get('accountcode', '')
            # call_log.ip = kwargs.get('ip', '')
            # call_log.dstchannel = kwargs.get('dstchannel', '')
            # call_log.userfield = kwargs.get('userfield', '')
            # call_log.provider = classify_telecom_number(call_log.dstchannel)
            # call_log.chargeable_time = self.calculate_chargeable_time(call_log)
            # call_log.save()

            # if call_log.direction == CALL_DIRECTION.OUTGOING and call_log.chargeable_time > 0:
            #     cache.update_call_center_month_minute(call_log)

        except Exception as e:
            cache.log_error(request.GET.get('callid', 'None_callid') + '_' + str(e))

    def calculate_chargeable_time(self, call_log):
        if call_log.billsec == 0:
            return 0
        try:
            company_id = cache.get_ext_company(call_log.extension)

            call_center = CallCenter.objects.get(company_id=company_id)
            if call_center.sip_fee_calculation == '6+1':
                return self.calculate_by_6_1(call_log.billsec)

            if call_center.sip_fee_calculation == '60+1':
                return self.calculate_by_60_1(call_log.billsec)

        except CallAgent.DoesNotExist:
            return 0
        except CallCenter.DoesNotExist:
            return 0
        return 0

    def calculate_by_6_1(self, duration):
        return duration if duration > 6 else 6

    def calculate_by_60_1(self, duration):
        return 60 * (math.floor((duration - 1) / 60) + 1)

    def is_company_created(self, companies, accountcode):
        for company in companies:
            if company.name == accountcode:
                return company

        return None

    def handle_new_extension(self, extension, accountcode, request, cookies):
        company_name = accountcode + '_call_center_only'
        companies = Company.objects.filter(deleted_at__isnull=True, name=company_name)
        company = None
        if companies:
            company = self.is_company_created(companies, company_name)

        if company is None:
            company = self.create_company(company_name, request, cookies)
            self.create_company_admin(company, request, cookies)
            self.create_call_center(company, request, cookies)

        ag = AgentRegister.objects.create(company=company, number=1, use_from=datetime.now(), use_to=datetime.now(),
                                     charge_from=datetime.now(), charge_to=datetime.now())
        CallAgent.objects.create(company_id=company.id, name=extension,
                  secret=extension,
                  agent_register_id=ag.id,
                  status=CALL_AGENT_STATUS.ACTIVE)


        cache.init_ext_company()

    def create_call_center(self, company, request, cookies):
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
        service = CreateCallCenterService()
        service.serve(request, cookies, *[], **data)

    def create_company(self, name, request, cookies):
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

    def create_company_admin(self, company, request, cookies):
        data = {
            'company_id': company.id,
            'username': company.name,
            'password': 'forC@llcent3r' + company.name,
        }

        request.user.is_superuser = True
        service = manage.CreateUserService()
        service.serve(request, cookies, *[], **data)


class StartCallOutService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_superuser:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)
            company_id = user_roles.first().company_id
        else:
            company_id = kwargs.get('company_id', 0)

        call_center = CallCenter.objects.get(company_id=company_id, deleted_at__isnull=True)
        if call_center_utils.is_trial(call_center) and call_center.trial_expired:
            raise TrialExpired()


class EndCallOutService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)
        company_id = user_roles.first().company_id

        phone = kwargs.get('phone', '')
        ext = CallAgent.objects.filter(user_id=request.user.id, deleted_at__isnull=True,
                                       status=CALL_AGENT_STATUS.ACTIVE, company_id=company_id)

        if phone and ext:
            call_log = CallLog.objects.filter(phone=phone, extension=ext.first().name).order_by('-id')
            if call_log and call_log.first().status is None:
                fetch_call_log_data.delay(call_log.first().id)


class DownloadExtFileService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        ext_file = ExtFileHistory.objects.filter(company_id=kwargs['company_id']).order_by('-created_at').first()
        csv_file = default_storage.open(ext_file.file_name, 'r')
        response = HttpResponse(csv_file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % csv_file.name
        return response


class UploadExtFileService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        serializer_class = call_center_serial.UploadExtFileRequestSerializer(data=request.data)
        if 'file' not in request.FILES or not serializer_class.is_valid():
            return 'failed'
        else:
            common = Common()
            file = request.FILES['file']
            file_name = common.upload_ext_file(file, 'files/ext_files/')
            ext_file = ExtFileHistory(file_name='files/ext_files/' + file_name,
                                      company_id=serializer_class.data['company_id'])
            ext_file.save()
            with default_storage.open('files/ext_files/' + file_name, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                call_agents = []
                error_call_agents = []
                existed_call_agents = CallAgent.objects.filter(company_id=serializer_class.data['company_id'])
                for row in csv_reader:
                    if len(row) >= 3 and row[1] != '' and row[2] != '':
                        call_agent = CallAgent(company_id=serializer_class.data['company_id'], name=row[1],
                                               secret=row[2],
                                               agent_register_id=serializer_class.data['agent_register_id'],
                                               status=CALL_AGENT_STATUS.ACTIVE)
                        if not self.exists_call_agent(existed_call_agents=existed_call_agents, ext_name=row[1]):
                            call_agents.append(call_agent)
                        else:
                            error_call_agents.append(row[1])
                self.validate(len(call_agents) + len(error_call_agents), serializer_class.data['agent_register_id'])
                CallAgent.objects.bulk_create(call_agents)
                cache.init_ext_company()
            return {
                'error_call_agents': error_call_agents
            }

    def exists_call_agent(self, existed_call_agents, ext_name):
        for existed_call_agent in existed_call_agents:
            if existed_call_agent.name == ext_name:
                return True
        return False

    def exists_ext_file(self, ext_files, ext_file_name):
        for ext_file in ext_files:
            if ext_file.file_name == ext_file_name:
                return True
        return False

    def validate(self, total_ext, agent_register_id):
        try:
            if total_ext != AgentRegister.objects.get(pk=agent_register_id).number:
                raise NumberAgentRegisterNotMatch()
        except AgentRegister.DoesNotExist:
            raise AgentRegisterNotFound()


# class CallCenterReportBuildService:
#     def __init__(self, call_center):
#         self.call_center = call_center
#         self.start_date = get_first_of_month(datetime.now())
#         self.end_date = get_last_of_month(datetime.now())
#
#     def calculate(self):
#         if self.call_center.payment_method == 'CREDIT' and self.call_center.charge_by == 'MINUTE':
#             CallCenterReport


class CallCenterPaymentCalculatorService:
    def __init__(self, call_center, start_date, end_date, last_month=False):
        self.call_center = call_center
        self.total_payment_amount = 0
        self.credit_payment_amount = 0
        self.external_payment_amount = 0
        self.discount_amount = 0
        self.start_date = start_date
        self.end_date = end_date
        self.last_month = last_month
        self.current_prices = {
            PRICE_TYPE.VIETTEL: 0,
            PRICE_TYPE.VINAPHONE: 0,
            PRICE_TYPE.MOBIFONE: 0,
            PRICE_TYPE.OTHER: 0
        }
        self.current_minutes = {
            PRICE_TYPE.VIETTEL: 0,
            PRICE_TYPE.VINAPHONE: 0,
            PRICE_TYPE.MOBIFONE: 0,
            PRICE_TYPE.OTHER: 0
        }

    def get_credit_payment_amount(self):
        return self.credit_payment_amount

    def get_total_payment_amount(self):
        return self.total_payment_amount

    def get_external_payment_amount(self):
        return self.external_payment_amount

    def get_discount_amount(self):
        return self.discount_amount

    def get_current_prices(self):
        return self.current_prices

    def get_current_minutes(self):
        return self.current_minutes

    def calculate(self):
        if self.call_center.payment_method == CALL_CENTER_PAYMENT_METHOD.CREDIT:
            if self.call_center.charge_by == CALL_CENTER_CHARGE_METHOD.AGENT:
                self.credit_payment_amount = self.calculate_by_agent()

            if self.call_center.charge_by == CALL_CENTER_CHARGE_METHOD.MINUTE:
                self.credit_payment_amount = self.calculate_by_sip_minute()

        self.external_payment_amount = self.calculate_external_payment_amount()

        self.discount_amount = self.calculate_discount_amount(self.external_payment_amount + self.credit_payment_amount)

        self.total_payment_amount = self.external_payment_amount + self.credit_payment_amount - self.discount_amount

    def calculate_discount_amount(self, total_payment_amount):
        if self.call_center.discount_type == DISCOUNT_TYPE.PERCENT:
            return self.call_center.discount_value * total_payment_amount / 100

        if self.call_center.discount_type == DISCOUNT_TYPE.VALUE:
            return self.call_center.discount_value

        return 0

    def calculate_by_sip_minute(self):
        # call_agents = CallAgent.objects.filter(company_id=self.call_center.company_id, deleted_at__isnull=True)
        # call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
        #                                    calldate__gte=self.start_date, calldate__lte=self.end_date,
        #                                    is_telco=False, direction=CALL_DIRECTION.OUTGOING)
        #
        # total_viettel_duration = 0
        # total_mobi_duration = 0
        # total_vina_duration = 0
        # for call_log in call_logs:
        #     if call_log.provider == TELECOM_NUMBER.VIETTEL:
        #         total_viettel_duration += call_log.chargeable_time
        #
        #     if call_log.provider == TELECOM_NUMBER.MOBI:
        #         total_mobi_duration += call_log.chargeable_time
        #
        #     if call_log.provider == TELECOM_NUMBER.VINA:
        #         total_vina_duration += call_log.chargeable_time
        if self.last_month:
            total_viettel_duration = cache.get_call_center_last_month_minute(self.call_center.company_id,
                                                                             TELECOM_NUMBER.VIETTEL)
            total_mobi_duration = cache.get_call_center_last_month_minute(self.call_center.company_id,
                                                                          TELECOM_NUMBER.MOBI)
            total_vina_duration = cache.get_call_center_last_month_minute(self.call_center.company_id,
                                                                          TELECOM_NUMBER.VINA)
        else:
            total_viettel_duration = cache.get_call_center_month_minute(self.call_center.company_id,
                                                                        TELECOM_NUMBER.VIETTEL)
            total_mobi_duration = cache.get_call_center_month_minute(self.call_center.company_id, TELECOM_NUMBER.MOBI)
            total_vina_duration = cache.get_call_center_month_minute(self.call_center.company_id, TELECOM_NUMBER.VINA)

        viettel_minute = math.floor((total_viettel_duration - 1) / 60) + 1
        mobi_minute = math.floor((total_mobi_duration - 1) / 60) + 1
        vina_minute = math.floor((total_vina_duration - 1) / 60) + 1

        viettel_fee = call_center_utils.get_current_fee(PRICE_TYPE.VIETTEL, viettel_minute, self.call_center.company_id)
        mobi_fee = call_center_utils.get_current_fee(PRICE_TYPE.MOBIFONE, mobi_minute, self.call_center.company_id)
        vina_fee = call_center_utils.get_current_fee(PRICE_TYPE.VINAPHONE, vina_minute, self.call_center.company_id)
        self.current_prices[PRICE_TYPE.VIETTEL] = viettel_fee
        self.current_prices[PRICE_TYPE.MOBIFONE] = mobi_fee
        self.current_prices[PRICE_TYPE.VINAPHONE] = vina_fee
        self.current_minutes[PRICE_TYPE.VIETTEL] = viettel_minute
        self.current_minutes[PRICE_TYPE.MOBIFONE] = mobi_minute
        self.current_minutes[PRICE_TYPE.VINAPHONE] = vina_minute

        return viettel_fee * viettel_minute + mobi_fee * mobi_minute + vina_fee * vina_minute

    def calculate_by_agent(self):
        total = 0
        due_date = get_last_of_month(self.end_date)
        agent_register_list = AgentRegister.objects.filter(company_id=self.call_center.company_id,
                                                           deleted_at__isnull=True)

        for agent_register in agent_register_list:
            if agent_register.charge_from <= due_date and agent_register.charge_to >= self.start_date:
                calculate_from = max(self.start_date, agent_register.charge_from)
                calculate_to = min(due_date, agent_register.charge_to)
                rate = (calculate_to - calculate_from).days / (
                        get_last_of_month(calculate_to) - get_first_of_month(calculate_to)).days
                rate = floor_rate(rate)
                total += agent_register.number * rate * self.call_center.agent_fee

        return total

    def calculate_agent_fee(self, start_date, end_date, fee_per_month):
        total = 0
        while start_date.month < end_date.month:
            total += fee_per_month * (get_last_of_month(start_date) - start_date).days / (
                    get_last_of_month(start_date) - get_first_of_month(start_date)).days
            start_date = get_first_of_month(start_date + relativedelta(months=1))

        total += fee_per_month * (end_date - start_date).days / (
                get_last_of_month(start_date) - get_first_of_month(start_date)).days
        return total

    def calculate_external_payment_amount(self):
        # call_agents = CallAgent.objects.filter(company_id=self.call_center.company_id, deleted_at__isnull=True)
        # call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
        #                                    calldate__gte=self.start_date, calldate__lte=self.end_date,
        #                                    is_telco=True, direction=CALL_DIRECTION.OUTGOING)

        # for call_log in call_logs:
        #     total_duration += call_log.chargeable_time
        if self.last_month:
            total_duration = cache.get_call_center_last_month_minute(self.call_center.company_id, TELECOM_NUMBER.OTHER)
        else:
            total_duration = cache.get_call_center_month_minute(self.call_center.company_id, TELECOM_NUMBER.OTHER)

        total_minute = math.floor((total_duration - 1) / 60) + 1

        self.current_prices[PRICE_TYPE.OTHER] = call_center_utils.get_current_fee(PRICE_TYPE.OTHER, total_minute,
                                                                self.call_center.company_id)
        self.current_minutes[PRICE_TYPE.OTHER] = total_minute
        return self.current_prices[PRICE_TYPE.OTHER] * total_minute


class ExportCallLogsService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)
                company_id = user_roles.first().company_id
            else:
                company_id = kwargs.get('company_id', 0)

            start_date = None
            end_date = None
            call_center = CallCenter.objects.get(company_id=company_id, deleted_at__isnull=True)

            if kwargs['report_type'] == 'CURRENT_MONTH':
                start_date = get_first_of_month(datetime.now())
                end_date = datetime.now()

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                start_date = get_first_of_month(datetime.now() - relativedelta(months=1))
                end_date = get_last_of_month(start_date)

            if call_center is None:
                raise ReportNotFound()

            call_agents = CallAgent.objects.filter(company_id=call_center.company_id, deleted_at__isnull=True)
            call_logs = CallLog.objects.filter(deleted_at__isnull=True,
                                               extension__in=call_agents.values_list('name', flat=True),
                                               calldate__gte=start_date, calldate__lte=end_date,
                                               direction=CALL_DIRECTION.OUTGOING).order_by('id')

            export_request = ExportCallLogsHistory.objects.create(company_id=company_id)
            file_path = MEDIA_ROOT + '/' + 'export_call_logs' + '/' + str(export_request.id) + '_' + str(
                export_request.created_at.timestamp()) + '.xls'

            export_data = []
            for call_log in call_logs:
                export_data.append(self.normalize_call_log_row(call_log))

            df = pd.DataFrame(export_data, columns=['Mã cuộc gọi',
                                                    'Thời gian',
                                                    'Extension',
                                                    'Số gọi đi',
                                                    'Thời lượng',
                                                    'Trạng thái',
                                                    'File ghi âm',
                                                    'Loại cuộc gọi',
                                                    'Thời gian tính phí'])
            df.to_excel(file_path, index=False, header=True)
            export_request.file.name = file_path[len(MEDIA_ROOT):]
            export_request.save()

            return export_request

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except CallCenterPaymentHistory.DoesNotExist:
            raise CallCenterNotFound()

    def normalize_call_log_row(self, call_log):
        return [
            call_log.callid.__str__(),
            call_log.calldate.__str__() if call_log.calldate is not None else '',
            call_log.extension if call_log.extension is not None else '',
            call_log.phone if call_log.phone is not None else '',
            call_log.duration.__str__() if call_log.duration is not None else '',
            call_log.status if call_log.status is not None else '',
            call_log.recording if call_log.recording is not None else '',
            'Ngoại mạng' if call_log.provider == TELECOM_NUMBER.OTHER else 'Nội mạng',
            call_log.chargeable_time.__str__() if call_log.chargeable_time is not None else '']

