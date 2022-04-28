import json

import requests
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.call_center import CallCenter, CallAgent, SipServiceInfo, AgentRegister
from api.models.organization import Company, UserRole
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (CallCenterDuplicated, CallCenterNotFound, ManageCompanyNotFound, CallAgentNotFound,
                                     AgentRegisterNotFound)
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
                    kwargs['minute_fee'] = json.dumps(kwargs.get('minute_fee'))

                call_center = CallCenter.objects.create(**kwargs)
                self.create_agent_list(call_center)

                return call_center
            except IntegrityError as e:
                raise CallCenterDuplicated()
            except Company.DoesNotExist:
                raise ManageCompanyNotFound()

    def create_agent_list(self, call_center):
        sip_service = SipService()
        sip_service.login(call_center.call_center_user, call_center.call_center_password, call_center.company_id)
        agent_list = sip_service.get_agent_list(call_center.company_id)
        call_agents = []
        for agent in agent_list:
            call_agents.append(CallAgent(company_id=call_center.company_id, name=agent['ext'], secret=agent['secret'],
                                         sip_id=agent['sip_id']))

        CallAgent.objects.bulk_create(call_agents)


class EnableCallCenterService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['company_id'])
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])
            call_center.is_enable = False
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
            call_center.is_enable = True
            call_center.save()
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

            if kwargs.get('call_center_user'):
                call_center.call_center_user = kwargs.get('call_center_user')

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

            sip_info = SipServiceInfo.objects.get(company_id=user_roles.first().company_id)

            from_date = kwargs['filter']['from_date'].strftime('%Y-%m-%d')
            to_date = kwargs['filter']['to_date'].strftime('%Y-%m-%d')
            month = kwargs['filter']['from_date'].strftime('%Y%m')

            call_history = SipService().filter_call_history(sip_info.company_id, kwargs.get('page_size'),
                                                            kwargs.get('page'), month, from_date, to_date)

            filter_history = []
            for history in call_history:
                if kwargs['filter'].get('number') and kwargs['filter'].get('number') not in history['dest_number']:
                    continue

                if kwargs['filter'].get('user_id'):
                    call_agent = CallAgent.objects.get(user_id=kwargs['filter'].get('user_id'))
                    if history['src_user'] != str(call_agent.sip_id):
                        continue

                filter_history.append(history)

            return filter_history
        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()


class GetUserCallHistoryService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        call_agent = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
        if not call_agent:
            raise CallAgentNotFound()
        call_agent = call_agent.first()
        sip_info = SipServiceInfo.objects.get(company_id=call_agent.company_id)

        from_date = kwargs.get('from_date')
        to_date = kwargs.get('to_date')
        month = timezone.now().strftime('%Y%m')
        return SipService().filter_call_history(sip_info.company_id, kwargs.get('page_size'), kwargs.get('page'), month,
                                                from_date, to_date, call_agent.sip_id)


class GetCallReportService(BaseService):
    def __init__(self):
        self.report = dict()

    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            sip_info = SipServiceInfo.objects.get(company_id=user_roles.first().company_id)

            from_date = kwargs['filter']['from_date'].strftime('%Y-%m-%d')
            to_date = kwargs['filter']['to_date'].strftime('%Y-%m-%d')
            month = kwargs['filter']['from_date']
            while month < kwargs['filter']['to_date']:
                month_str = month.strftime('%Y%m')

                call_history = SipService().filter_call_history(sip_info.company_id, kwargs.get('page_size'),
                                                                kwargs.get('page'), month_str, from_date, to_date)
                self.process_call_report(call_history)
                month += relativedelta(months=1)

            return list(self.report.values())

        except CallAgent.DoesNotExist:
            raise CallAgentNotFound()

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
