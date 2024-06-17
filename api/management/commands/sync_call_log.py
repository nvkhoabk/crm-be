import requests

from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from pytz import timezone

from api.const import CALL_DIRECTION
from api.models.call_center import CallLog
from api.utils.phone import classify_telecom_number
from crm.settings import TIME_ZONE
import logging
from logging.handlers import RotatingFileHandler

from crm.settings import LOG_ROOT, LOG_LEVEL

import api.utils.call_center as call_center_utils
from django.utils.timezone import make_aware


class Command(BaseCommand):
    help = 'Job sync call log from crm and ITY'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.logger = None

    def initializer_logger(self):
        logging.basicConfig(handlers=[RotatingFileHandler(filename=LOG_ROOT + 'crm.sync_call_log.log',
                                                          maxBytes=512000, backupCount=4)], level=LOG_LEVEL,
                            format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        self.logger = logging.getLogger(__name__)

    def add_arguments(self, parser):
        parser.add_argument('--date', help='Processing date', default='')
        parser.add_argument(
            '--sync',
            action='store_true',
            dest='sync',
            default=False,
            help='Do sync data',
        )

    def sync_call_log(self, syncing_date, sync, account_code = 'ITY'):
        session = requests.Session()
        session.auth = ('ITY', 'Crm1ty@1305Fri')

        url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&fromdate={}&todate={}&status=answered&accountcode={}&page=1'.format(
            syncing_date.strftime('%Y-%m-%d'), syncing_date.strftime('%Y-%m-%d'), account_code)
        response = session.get(url)
        response_json = response.json()
        total = response_json['total']
        self.logger.info('Total cdr: {}'.format(total))
        max_page = response_json['max_page']
        total_cdr = []
        for page in range(1, max_page + 1):
            url = 'https://vnsale.siptrunk.vn/wsapi/crm_ity/ws_cdr.php?flag=all&fromdate={}&todate={}&status=answered&accountcode={}&page={}'.format(
                syncing_date.strftime('%Y-%m-%d'), syncing_date.strftime('%Y-%m-%d'), account_code, page)
            response = session.get(url)
            response_json = response.json()
            total_cdr.extend(response_json['cdr'])

        start_time = syncing_date
        end_time = syncing_date + relativedelta(days=1)
        call_logs = CallLog.objects.filter(calldate__gte=start_time, calldate__lt=end_time, chargeable_time__gt=0,
                                           direction=CALL_DIRECTION.OUTGOING, accountcode=account_code, deleted_at__isnull=True)
        dict_call_logs = {log.callid: log for log in call_logs}
        dict_cdr = {cdr['callid']: cdr for cdr in total_cdr}

        missing_log = []
        missing_cdr = []
        diff_crm = dict()
        diff_cdr = dict()
        for cdr in total_cdr:
            if cdr['callid'] in dict_call_logs:
                call_log = dict_call_logs[cdr['callid']]
                if cdr['phone'] != call_log.phone and cdr['billsec'] != call_log.billsec and cdr[
                    'extension'] != call_log.extension:
                    diff_cdr[cdr['callid']] = cdr
                    diff_crm[cdr['callid']] = call_log
            else:
                if int(cdr['billsec']) > 0:
                    missing_cdr.append(cdr)

        for call_log in call_logs:
            if call_log.callid not in dict_cdr:
                missing_log.append(call_log)

        if len(diff_cdr):
            self.logger.info('===========DATA DIFF===========')
            callid_list_diff = [key for key in diff_cdr]
            self.logger.info(callid_list_diff.__str__())

        if len(missing_log):
            self.logger.info('===========MISSING IN CDR===========')
            callid_list_diff = [log.callid for log in missing_log]
            self.logger.info(callid_list_diff.__str__())

        if len(missing_cdr):
            self.logger.info('===========MISSING IN CRM===========')
            callid_list_diff = [cdr['callid'] for cdr in missing_cdr]
            self.logger.info(callid_list_diff.__str__())

        if sync:
            for cdr in missing_cdr:
                self.create_call_log_from_cdr(cdr)
            for cdr in diff_cdr:
                self.update_call_log_from_cdr(cdr)

    def create_call_log_from_cdr(self, cdr):
        data = cdr
        call_log = CallLog(callid=data['callid'], phone=data['phone'],
                           extension=data['extension'])
        call_log.direction = CALL_DIRECTION.OUTGOING

        call_log.calldate = make_aware(datetime.strptime(data['calldate'], '%Y-%m-%d %H:%M:%S'))
        call_log.duration = int(data['duration'])
        call_log.billsec = int(data['billsec'])
        call_log.status = data['status']
        call_log.recording = data['recordingfile']
        call_log.accountcode = data['accountcode']
        call_log.ip = data['ip']
        call_log.dstchannel = data['dstchannel']
        call_log.userfield = data['userfield']
        call_log.extension = data['extension']
        call_log.phone = data['phone']
        call_log.provider = classify_telecom_number(call_log.dstchannel)
        call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
        call_log.save()

    def update_call_log_from_cdr(self, cdr):
        data = cdr
        call_log = CallLog.objects.filter(callid=cdr['callid'], deleted_at__isnull=True).first()
        if call_log is not None:
            call_log.calldate = make_aware(datetime.strptime(data['calldate'], '%Y-%m-%d %H:%M:%S'))
            call_log.duration = int(data['duration'])
            call_log.billsec = int(data['billsec'])
            call_log.status = data['status']
            call_log.recording = data['recordingfile']
            call_log.accountcode = data['accountcode']
            call_log.ip = data['ip']
            call_log.dstchannel = data['dstchannel']
            call_log.userfield = data['userfield']
            call_log.extension = data['extension']
            call_log.phone = data['phone']
            call_log.provider = classify_telecom_number(call_log.dstchannel)
            call_log.chargeable_time = call_center_utils.calculate_chargeable_time(call_log)
            call_log.save()
        else:
            self.logger.info('Not found callid {} from crm'.format(cdr['callid']))


    def handle(self, *args, **options):
        self.initializer_logger()
        processing_date = datetime.now(timezone(TIME_ZONE)).date() if options['date'] == '' else datetime.strptime(
            options['date'], '%Y%m%d').date()
        self.logger.info(
            'Processing date is {}, job will sync call log from previous day, sync={}'.format(processing_date.__str__(),
                                                                                              options[
                                                                                                  'sync'].__str__()))
        self.sync_call_log(processing_date - relativedelta(days=1), options['sync'])
