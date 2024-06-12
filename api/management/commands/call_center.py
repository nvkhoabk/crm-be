import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime

from api.const import CALL_AGENT_STATUS
from api.models.call_center import CallCenter, AgentRegister, CallAgent, CallLog
from django.core.management.base import BaseCommand
from pytz import timezone

from api.services.call_center import DisableCallCenterService
from api.utils import cache
from api.utils.phone import classify_telecom_number
from crm.settings import TIME_ZONE
import api.utils.call_center as call_center_utils

import logging
from logging.handlers import RotatingFileHandler

from crm.settings import LOG_ROOT, LOG_LEVEL


class Command(BaseCommand):
    help = 'Runs a job'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.logger = None

    def initializer_logger(self):
        logging.basicConfig(handlers=[RotatingFileHandler(filename=LOG_ROOT + 'crm.call_center.log',
                                                          maxBytes=512000, backupCount=4)], level=LOG_LEVEL,
                            format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')

        self.logger = logging.getLogger(__name__)

    def disable_call_center(self, tomorrow):
        call_centers = CallCenter.objects.filter(payment_date=tomorrow, deleted_at__isnull=True, is_enable=True)
        self.logger.info('Number of call centers: ' + str(len(call_centers)))

        for call_center in call_centers:
            service = DisableCallCenterService()
            service.serve(request=None, cookies=None, **{'company_id': call_center.company_id})

    def disable_call_agent(self, tomorrow):
        agent_registers = AgentRegister.objects.filter(deleted_at__isnull=True, use_to=tomorrow)

        self.logger.info('Number of agent_registers: ' + str(len(agent_registers)))

        CallAgent.objects.filter(deleted_at__isnull=True, status=CALL_AGENT_STATUS.ACTIVE,
                                 agent_register_id__in=agent_registers.values_list('id',
                                                                                   flat=True)).update(
            status=CALL_AGENT_STATUS.INACTIVE)


    def reset_call_center_cache(self):
        if datetime.now(timezone(TIME_ZONE)).day == 1:
            cache.reset_call_center_cache()


    def fetch_null_status_call_log(self):
        time_from = datetime.now(timezone(TIME_ZONE)) - relativedelta(days=1)
        self.logger.info('[call_log]Fetching data for: ' + str(time_from))
        call_logs = CallLog.objects.filter(status__isnull=True, created_at__gte=time_from)
        session = requests.Session()
        session.auth = ('ITY', 'Crm1ty@1305Fri')
        self.logger.info('[call_log]Number of call log missing: ' + str(len(call_logs)))
        for call_log in call_logs:
            url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&callid={}&fromdate=2024-02-05 00:00:00'.format(
                call_log.callid)
            response = session.get(url)

            # Print the response
            response_json = response.json()
            if len(response_json['cdr']) == 1:
                data = response_json['cdr'][0]
                call_log.calldate = datetime.strptime(data['calldate'], '%Y-%m-%d %H:%M:%S')
                call_log.duration = int(data['duration'])
                call_log.billsec = int(data['billsec'])
                call_log.status = data['status']
                call_log.recording = data['recordingfile']
                call_log.accountcode = data['accountcode']
                call_log.ip = data['ip']
                call_log.dstchannel = data['dstchannel']
                call_log.userfield = data['userfield']
                call_log.provider = classify_telecom_number(call_log.dstchannel)
                call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
                call_log.save()
                self.logger.info('[call_log]Fetching data for callid: ' + call_log.callid)
            else:
                self.logger.info('[call_log]Cannot get data for callid: ' + call_log.callid)

    def handle(self, *args, **options):
        self.initializer_logger()
        tomorrow = datetime.now(timezone(TIME_ZONE)).date() - relativedelta(days=1)

        self.logger.info('Running call_center job, tomorrow: ' + str(tomorrow))
        self.disable_call_center(tomorrow)
        self.disable_call_agent(tomorrow)
        self.reset_call_center_cache()
        self.fetch_null_status_call_log()
