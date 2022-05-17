import json

import requests
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import CALL_DIRECTION
from api.models.call_center import CallCenter, CallAgent, SipServiceInfo, AgentRegister, CallCenterPaymentHistory, \
    CallLog
from api.models.organization import Company, UserRole
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (CallCenterDuplicated, CallCenterNotFound, ManageCompanyNotFound, CallAgentNotFound,
                                     AgentRegisterNotFound, SipAPIError, CallLogNotFound)
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import IntegrityError, transaction
from groups_manager.models import Group, GroupType, Member

from api.services.sip import SipService

User = get_user_model()


class CreateCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        with transaction.atomic():
            try:
                Company.objects.get(pk=kwargs['company_id'])
                if kwargs.get('minute_fee') is not None:
                    kwargs['minute_fee'] = json.dumps(kwargs.get('minute_fee')).replace("'", "\"")

                call_center = CallCenter.objects.create(**kwargs)
                #self.create_agent_list(call_center)

                return call_center
            except IntegrityError as e:
                raise CallCenterDuplicated()
            except Company.DoesNotExist:
                raise ManageCompanyNotFound()

    # def create_agent_list(self, call_center):
    #     sip_service = SipService()
    #     sip_service.login(call_center.call_center_user, call_center.call_center_password, call_center.company_id)
    #     agent_list = sip_service.get_agent_list(call_center.company_id)
    #     call_agents = []
    #     for agent in agent_list:
    #         call_agents.append(CallAgent(company_id=call_center.company_id, name=agent['ext'], secret=agent['secret'],
    #                                      sip_id=agent['sip_id']))
    #
    #     CallAgent.objects.bulk_create(call_agents)
#
#
# class BaseService(BaseService):
#     def serve(self, request, cookies: Cookies, *args, **kwargs):
#         pass
#
#     def serve(self, request, cookies: Cookies, *args, **kwargs):
#         try:
#             return self.serve(request, cookies, *args, **kwargs)
#         except SipAPIError:
#             # Try to login
#             filter = {
#                 'user': request.user,
#                 'deleted_at__isnull': True
#             }
#             user_roles = UserRole.objects.filter(**filter)
#             call_center = CallCenter.objects.get(company_id=user_roles.first().company_id, deleted_at__isnull=True)
#             SipService().login(call_center.call_center_user, call_center.call_center_password, call_center.company_id)
#
#         return self.serve(request, cookies, *args, **kwargs)


class EnableCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])
            call_center.is_enable = True
            call_center.save()

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
                agent.deleted_at = timezone.now()

            call_agents.bulk_update(call_agents, fields=['deleted_at'])
            return call_center
        except CallCenter.DoesNotExist as e:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class GetCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            return CallCenter.objects.get(company_id=kwargs['company_id'])
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class UpdateCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])

            if kwargs.get('charge_by'):
                call_center.charge_by = kwargs.get('charge_by')

            if kwargs.get('payment_method'):
                call_center.payment_method = kwargs.get('payment_method')

            if kwargs.get('payment_date'):
                call_center.payment_date = kwargs.get('payment_date')

            if kwargs.get('payment_notify'):
                call_center.payment_notify = kwargs.get('payment_notify')

            if kwargs.get('agent_fee'):
                call_center.agent_fee = kwargs.get('agent_fee')

            if kwargs.get('minute_fee'):
                call_center.minute_fee = kwargs.get('minute_fee')

            if kwargs.get('external_fee'):
                call_center.external_fee = kwargs.get('external_fee')

            if kwargs.get('sip_fee_calculation'):
                call_center.sip_fee_calculation = kwargs.get('sip_fee_calculation')

            if kwargs.get('discount_type'):
                call_center.discount_type = kwargs.get('discount_type')
                call_center.discount_value = 0

            if kwargs.get('discount_value'):
                call_center.discount_value = kwargs.get('discount_value')

            call_center.save()
            return call_center

        except CallCenter.DoesNotExist as e:
            raise CallCenterNotFound()
        except Company.DoesNotExist:
            raise ManageCompanyNotFound()


class GetAgentsService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        return CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)


class UpdateAgentService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            call_agents = []
            for updating_value in kwargs.get('data'):
                call_agent = CallAgent.objects.get(pk=updating_value['id'])
                call_agent.user_id = updating_value['user_id']
                call_agent.save()
                call_agents.append(call_agent)

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
            to_date = kwargs['filter']['to_date'].strftime('%Y-%m-%d')

            call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
            call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                          created_at__gte=from_date, created_at__lte=to_date).order_by('created_at')

            call_history_list = []
            for call_log in call_logs:
                call_history_list.append({
                    'dest_number': call_log.phone,
                    'calldate': call_log.calldate,
                    'record_url': call_log.recording,
                    'direction': call_log.direction,
                    'duration': call_log.duration
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
        user_roles = UserRole.objects.filter(**filter)

        call_agent = CallAgent.objects.filter(user_id=user_roles.first().user_id, deleted_at__isnull=True)
        if not call_agent:
            raise CallAgentNotFound()

        call_agent = call_agent.first()

        call_logs = CallLog.objects.filter(extension=call_agent.name).order_by('created_at')

        call_history_list = []
        for call_log in call_logs:
            call_history_list.append({
                'dest_number': call_log.phone,
                'calldate': call_log.calldate,
                'record_url': call_log.recording,
                'direction': call_log.direction,
                'duration': call_log.duration
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
        to_date = kwargs['filter']['to_date'].strftime('%Y-%m-%d')

        call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
        call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                           created_at__gte=from_date, created_at__lte=to_date).order_by(
            'created_at')

        call_history_list = []
        for call_log in call_logs:
            call_history_list.append({
                'dest_number': call_log.phone,
                'calldate': call_log.calldate,
                'record_url': call_log.recording,
                'direction': call_log.direction,
                'duration': call_log.duration
            })

        self.process_call_report(call_history_list)
        return self.report

    def process_call_report(self, call_history):
        for history in call_history:
            if history['ext'] not in self.report:
                self.report[history['ext']] = {
                    'agent_name': history['ext'],
                    'number_call_out': 0,
                    'duration_call_out': 0,
                    'number_call_in': 0,
                    'duration_call_in': 0,
                    'total_duration': 0
                }

            if history['direction'] == 'outgoing':
                self.report[history['ext']]['number_call_out'] += 1
                self.report[history['ext']]['duration_call_out'] += int(history['duration'])

            if history['direction'] == 'incoming':
                self.report[history['ext']]['number_call_in'] += 1
                self.report[history['ext']]['duration_call_in'] += int(history['duration'])

            self.report[history['ext']]['total_duration'] += int(history['duration'])


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
            AgentRegister.objects.get(pk=kwargs['id']).delete()
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
                    company_id=value,
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

            if kwargs['report_type'] == 'CURRENT_MONTH':
                call_center = CallCenter.objects.get(company_id=user_roles.first().company_id)
                from_date = call_center.created_at - relativedelta(months=1)
                to_date = call_center.payment_date

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                call_center_history = CallCenterPaymentHistory.objects.filter(company_id=sip_info.company_id).order_by('-id').first()
                from_date = call_center_history.created_at
                to_date = call_center_history.payment_date

            month = from_date
            while month < to_date:
                month_str = month.strftime('%Y%m')

                call_history = SipService().filter_call_history(sip_info.company_id, kwargs.get('page_size'),
                                                                kwargs.get('page'), month_str, from_date, to_date)
                self.process_external_call(call_history)
                month += relativedelta(months=1)

            return self.report

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except CallCenterPaymentHistory.DoesNotExist:
            raise CallCenterNotFound()

    def process_external_call(self, call_history):
        for call in call_history:
            if call['direction'] == CALL_DIRECTION.OUTGOING and self.is_external_number(call['dest_number']):
                self.report.append(call)

    @staticmethod
    def is_external_number(number):
        if len(number) == 10:
            return number[0:2] == '02' or number[0:2] == '05'

        if len(number) == 11:
            return number[0:2] == '02' or number[0:3] == '080' or number[0:3] == '087' or number[
                                                                                          0:3] == '092' or number[
                                                                                                           0:3] == '099'
        return False


class GetCreditPaymentReportService(BaseService):
    def __init__(self):
        self.report = list()

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            sip_info = SipServiceInfo.objects.get(company_id=user_roles.first().company_id)

            from_date = timezone.now()
            to_date = timezone.now()
            charge_by = ''

            if kwargs['report_type'] == 'CURRENT_MONTH':
                call_center = CallCenter.objects.get(company_id=sip_info.company_id)
                from_date = call_center.created_at - relativedelta(months=1)
                to_date = call_center.payment_date
                charge_by = call_center.charge_by

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                call_center_history = CallCenterPaymentHistory.objects.filter(company_id=sip_info.company_id).order_by(
                    '-id').first()
                from_date = call_center_history.created_at - relativedelta(months=1)
                to_date = call_center_history.payment_date
                charge_by = call_center_history.charge_by

            if charge_by == 'AGENT':
                self.calculate_by_agent(call_center)

            if charge_by == 'MINUTE':
                month = from_date
                while month < to_date:
                    month_str = month.strftime('%Y%m')

                    call_history = SipService().filter_call_history(sip_info.company_id, kwargs.get('page_size'),
                                                                    kwargs.get('page'), month_str, from_date, to_date)
                    self.process_external_call(call_history)
                    month += relativedelta(months=1)

            return self.report

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()
        except CallCenter.DoesNotExist:
            raise CallCenterNotFound()
        except CallCenterPaymentHistory.DoesNotExist:
            raise CallCenterNotFound()

    def calculate_by_agent(self, call_center):
        agent_register_list = AgentRegister.objects.filter(company_id=call_center.company_id)
        total = 0
        for agent_register in agent_register_list:
            total += agent_register.number * self.calculate_agent_fee(agent_register.charge_from,
                                                                      agent_register.charge_to, call_center.agent_fee)

        return total

    def calculate_agent_fee(self, start_date, end_date, fee_per_month):
        pass

    def process_external_call(self, call_history):
        for call in call_history:
            if call['direction'] == CALL_DIRECTION.OUTGOING and self.is_external_number(call['dest_number']):
                self.report.append(call)

    @staticmethod
    def is_external_number(number):
        if len(number) == 10:
            return number[0:2] == '02' or number[0:2] == '05'

        if len(number) == 11:
            return number[0:2] == '02' or number[0:3] == '080' or number[0:3] == '087' or number[
                                                                                          0:3] == '092' or number[
                                                                                                           0:3] == '099'
        return False


def is_external_number(number):
    if len(number) == 10:
        return number[0:2] == '02' or number[0:2] == '05'

    if len(number) == 11:
        return number[0:2] == '02' or number[0:3] == '080' or number[0:3] == '087' or number[
                                                                                      0:3] == '092' or number[
                                                                                                       0:3] == '099'
    return False


class IncomingCallService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        call_log = CallLog(**kwargs)
        call_log.is_telco = is_external_number(call_log.phone)
        call_log.direction = 'incoming'
        call_log.save()
        return call_log


class OutgoingCallService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        call_log = CallLog(**kwargs)
        call_log.is_telco = is_external_number(call_log.phone)
        call_log.direction = 'outgoing'
        call_log.save()
        return call_log


class CallAnsweredService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            call_log = CallLog.objects.get(callid=kwargs.get('callid', None))
            call_log.calldate = kwargs.get('calldate', None)
            call_log.duration = kwargs.get('duration', None)
            call_log.status = kwargs.get('status', None)
            call_log.recording = kwargs.get('recording', None)
            call_log.save()

            return call_log
        except CallLog.DoesNotExist:
            raise CallLogNotFound()
