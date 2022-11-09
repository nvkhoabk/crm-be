import csv
import json
import math
import mimetypes
from wsgiref.util import FileWrapper

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import IntegrityError, transaction
from django.http import HttpResponse, FileResponse
from django.utils import timezone

from api.common.common import Common
from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.const import CALL_DIRECTION, TELECOM_NUMBER, DISCOUNT_TYPE, PAYMENT_STATUS, CALL_AGENT_STATUS
from api.models.call_center import CallCenter, CallAgent, AgentRegister, CallCenterPaymentHistory, \
    CallLog, ExtFileHistory
from api.models.organization import Company, UserRole
from api.serializers.call_center_serializer import UploadExtFileRequestSerializer, DownloadExtFileRequestSerializer
from api.services.exceptions import (CallCenterDuplicated, CallCenterNotFound, ManageCompanyNotFound, CallAgentNotFound,
                                     AgentRegisterNotFound, CallLogNotFound, CallCenterPaymentNotDue,
                                     ReportNotFound, NumberAgentRegisterNotMatch)
from api.utils.date import get_first_of_month, get_last_of_month
from api.utils.phone import classify_telecom_number

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
        for call_center in call_center_list:
            payment_calculator = CallCenterPaymentCalculatorService(call_center)
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

        filters = ['company_id', 'charge_by', 'payment_method', 'sip_fee_calculation', 'discount_type', 'from_date', 'to_date']
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
            call_center = CallCenter.objects.get(company_id=kwargs['company_id'])

            old_call_center = CallCenter.objects.get(company_id=kwargs['company_id'])

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
                call_center.minute_fee = json.dumps(kwargs.get('minute_fee')).replace("'", "\"")

            if kwargs.get('external_fee'):
                call_center.external_fee = kwargs.get('external_fee')

            if kwargs.get('sip_fee_calculation'):
                call_center.sip_fee_calculation = kwargs.get('sip_fee_calculation')

            if kwargs.get('discount_type'):
                call_center.discount_type = kwargs.get('discount_type')
                call_center.discount_value = 0

            if kwargs.get('discount_value'):
                call_center.discount_value = kwargs.get('discount_value')

            if kwargs.get('payment_start_date'):
                call_center.payment_start_date = kwargs.get('payment_start_date')

            if kwargs.get('payment_status') and kwargs.get('payment_status') == PAYMENT_STATUS.PAID:
                self.pay_call_center(call_center, old_call_center)

            call_center.save()
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
        phone_number = kwargs['phone_number']
        user_roles = UserRole.objects.filter(**filter)

        call_agent = CallAgent.objects.filter(user_id=user_roles.first().user_id, deleted_at__isnull=True)
        if not call_agent:
            raise CallAgentNotFound()

        call_agent = call_agent.first()

        call_logs = []
        if phone_number is not None and phone_number != "":
            call_logs = CallLog.objects.filter(extension=call_agent.name, phone__icontains=phone_number).order_by('-created_at')
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
        to_date = (kwargs['filter']['to_date'] + relativedelta(days=1)).strftime('%Y-%m-%d')

        call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
        self.init_call_report(call_agents)

        call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                           created_at__gte=from_date, created_at__lt=to_date, status__isnull=False)

        call_history_list = []
        for call_log in call_logs:
            call_history_list.append({
                'ext': call_log.extension,
                'dest_number': call_log.phone,
                'calldate': call_log.calldate,
                'record_url': call_log.recording,
                'direction': call_log.direction,
                'duration': call_log.duration
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

            call_center = None

            if kwargs['report_type'] == 'CURRENT_MONTH':
                call_center = CallCenter.objects.get(company_id=user_roles.first().company_id)
                from_date = call_center.payment_date - relativedelta(months=1)
                to_date = call_center.payment_date

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                call_center = CallCenterPaymentHistory.objects.filter(
                    company_id=user_roles.first().company_id).order_by('-id').first()
                from_date = call_center.payment_date - relativedelta(months=1)
                to_date = call_center.payment_date

            call_agents = CallAgent.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)
            call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                               calldate__gte=from_date, calldate__lte=to_date, is_telco=True,
                                               direction=CALL_DIRECTION.OUTGOING).order_by('created_at')

            call_history_list = []
            for call_log in call_logs:
                call_history_list.append({
                    'number': call_log.phone,
                    'call_date': call_log.calldate,
                    'duration': call_log.duration,
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
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)
            call_center = None

            if kwargs['report_type'] == 'CURRENT_MONTH':
                call_center = CallCenter.objects.get(company_id=user_roles.first().company_id)

            if kwargs['report_type'] == 'PREVIOUS_MONTH':
                call_center = CallCenterPaymentHistory.objects.filter(
                    company_id=user_roles.first().company_id).order_by('-id').first()
            if call_center is None:
                raise ReportNotFound()
            payment_calculator = CallCenterPaymentCalculatorService(call_center)
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
        call_log = CallLog(callid=request.GET.get('callid', None), phone=request.GET.get('phone', None),
                           extension=request.GET.get('extension', None))
        call_log.is_telco = is_external_number(call_log.phone)
        call_log.direction = 'incoming'
        call_log.save()
        return call_log


class OutgoingCallService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        call_log = CallLog(callid=request.GET.get('callid', None), phone=request.GET.get('phone', None),
                           extension=request.GET.get('extension', None))
        call_log.is_telco = is_external_number(call_log.phone)
        call_log.direction = 'outgoing'
        call_log.save()
        return call_log


class CallAnsweredService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        call_log = CallLog.objects.filter(extension=kwargs.get('extension', None), phone=kwargs.get('phone', None),
                                          status__isnull=True).order_by('-created_at')
        if not call_log:
            raise CallLogNotFound()

        call_log = call_log.first()

        call_log.calldate = kwargs.get('calldate', None)
        call_log.duration = kwargs.get('duration', None)
        call_log.status = kwargs.get('status', None)
        call_log.recording = kwargs.get('recording', None)
        call_log.chargeable_time = self.calculate_chargeable_time(call_log)
        call_log.save()

        return call_log

    def calculate_chargeable_time(self, call_log):
        if call_log.duration == 0:
            return 0
        try:
            filter = {
                'user': CallAgent.objects.get(name=call_log.extension, deleted_at__isnull=True,
                                              status=CALL_AGENT_STATUS.ACTIVE).user_id,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)
            if not user_roles:
                return 0

            call_center = CallCenter.objects.get(company_id=user_roles.first().company_id)
            if call_center.sip_fee_calculation == '6+1':
                return self.calculate_by_6_1(call_log.duration)

            if call_center.sip_fee_calculation == '60+1':
                return self.calculate_by_60_1(call_log.duration)

        except CallAgent.DoesNotExist:
            return 0
        except CallCenter.DoesNotExist:
            return 0
        return 0

    def calculate_by_6_1(self, duration):
        return duration if duration > 6 else 6

    def calculate_by_60_1(self, duration):
        return 60 * (math.floor((duration - 1) / 60) + 1)

class DownloadExtFileService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        ext_file = ExtFileHistory.objects.filter(company_id=kwargs['company_id']).order_by('-created_at').first()
        csv_file = default_storage.open(ext_file.file_name, 'r')
        response = HttpResponse(csv_file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % csv_file.name
        return response



class UploadExtFileService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        serializer_class = UploadExtFileRequestSerializer(data=request.data)
        if 'file' not in request.FILES or not serializer_class.is_valid():
            return 'failed'
        else:
            common = Common()
            file = request.FILES['file']
            file_name = common.upload_ext_file(file, 'files/ext_files/')
            ext_file = ExtFileHistory(file_name='files/ext_files/' + file_name, company_id=serializer_class.data['company_id'])
            ext_file.save()
            with default_storage.open('files/ext_files/' + file_name, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                call_agents = []
                error_call_agents = []
                existed_call_agents = CallAgent.objects.filter(company_id=serializer_class.data['company_id'])
                for row in csv_reader:
                    if len(row) == 3:
                        call_agent = CallAgent(company_id=serializer_class.data['company_id'], name=row[1], secret=row[2],
                                  agent_register_id=serializer_class.data['agent_register_id'],
                                  status=CALL_AGENT_STATUS.ACTIVE)
                        if not self.exists_call_agent(existed_call_agents=existed_call_agents, ext_name=row[1]):
                            call_agents.append(call_agent)
                        else:
                            error_call_agents.append(row[1])
                self.validate(len(call_agents) + len(error_call_agents), serializer_class.data['agent_register_id'])
                CallAgent.objects.bulk_create(call_agents)
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


class CallCenterPaymentCalculatorService:
    def __init__(self, call_center):
        self.call_center = call_center
        self.total_payment_amount = 0
        self.credit_payment_amount = 0
        self.external_payment_amount = 0
        self.discount_amount = 0

    def get_credit_payment_amount(self):
        return self.credit_payment_amount

    def get_total_payment_amount(self):
        return self.total_payment_amount

    def get_external_payment_amount(self):
        return self.external_payment_amount

    def get_discount_amount(self):
        return self.discount_amount

    def calculate(self):
        if self.call_center.payment_method == 'CREDIT':
            if self.call_center.charge_by == 'AGENT':
                self.credit_payment_amount = self.calculate_by_agent()

            if self.call_center.charge_by == 'MINUTE':
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
        due_date = get_last_of_month(self.call_center.payment_date - relativedelta(months=1))
        call_agents = CallAgent.objects.filter(company_id=self.call_center.company_id, deleted_at__isnull=True)
        call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                           calldate__gte=self.call_center.payment_start_date, calldate__lte=due_date,
                                           is_telco=False, direction=CALL_DIRECTION.OUTGOING)

        total_viettel_duration = 0
        total_mobi_duration = 0
        total_vina_duration = 0
        for call_log in call_logs:
            if classify_telecom_number(call_log.phone) == TELECOM_NUMBER.VIETTEL:
                total_viettel_duration += call_log.chargeable_time

            if classify_telecom_number(call_log.phone) == TELECOM_NUMBER.MOBI:
                total_mobi_duration += call_log.chargeable_time

            if classify_telecom_number(call_log.phone) == TELECOM_NUMBER.VINA:
                total_vina_duration += call_log.chargeable_time

        viettel_minute = math.floor((total_viettel_duration - 1) / 60) + 1
        mobi_minute = math.floor((total_mobi_duration - 1) / 60) + 1
        vina_minute = math.floor((total_vina_duration - 1) / 60) + 1
        minute_fee = json.loads(self.call_center.minute_fee)

        viettel_fee = minute_fee.get(TELECOM_NUMBER.VIETTEL, 0)
        mobi_fee = minute_fee.get(TELECOM_NUMBER.MOBI, 0)
        vina_fee = minute_fee.get(TELECOM_NUMBER.VINA, 0)
        return viettel_fee * viettel_minute + mobi_fee * mobi_minute + vina_fee * vina_minute

    def calculate_by_agent(self):
        agent_register_list = AgentRegister.objects.filter(company_id=self.call_center.company_id)
        total = 0
        due_date = get_last_of_month(self.call_center.payment_date - relativedelta(months=1))
        for agent_register in agent_register_list:
            charge_from = max(agent_register.charge_from, self.call_center.payment_start_date)
            charge_to = min(agent_register.charge_to, due_date)
            total += agent_register.number * self.calculate_agent_fee(charge_from,
                                                                      charge_to,
                                                                      self.call_center.agent_fee)

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
        due_date = get_last_of_month(self.call_center.payment_date - relativedelta(months=1))
        call_agents = CallAgent.objects.filter(company_id=self.call_center.company_id, deleted_at__isnull=True)
        call_logs = CallLog.objects.filter(extension__in=call_agents.values_list('name', flat=True),
                                           calldate__gte=self.call_center.payment_start_date, calldate__lte=due_date,
                                           is_telco=True, direction=CALL_DIRECTION.OUTGOING)

        total_duration = 0
        for call_log in call_logs:
            total_duration += call_log.chargeable_time

        total_minute = math.floor((total_duration - 1) / 60) + 1
        return self.call_center.external_fee * total_minute
