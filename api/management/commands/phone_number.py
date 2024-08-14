from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.core.management.base import BaseCommand
from pytz import timezone

from api.models.phone_number import PhoneNumber
from crm.settings import TIME_ZONE
import logging
from logging.handlers import RotatingFileHandler

from crm.settings import LOG_ROOT, LOG_LEVEL

NUMBER_OF_DAY_DELETE = 3


class Command(BaseCommand):
    help = 'Job delete phone number'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.logger = None

    def initializer_logger(self):
        logging.basicConfig(handlers=[RotatingFileHandler(filename=LOG_ROOT + 'crm.delete_phone_number_log.log',
                                                          maxBytes=512000, backupCount=4)], level=LOG_LEVEL,
                            format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')
        self.logger = logging.getLogger(__name__)

    def delete_phone_number(self, processing_date):
        delete_date = processing_date - relativedelta(days=NUMBER_OF_DAY_DELETE)
        phone_numbers = PhoneNumber.objects.filter(deleted_at__isnull=True, updated_at__lte=delete_date,
                                                   phone_number_status__name__icontains='Đánh dấu xóa')
        for phone_number in phone_numbers:
            phone_number.deleted_at = datetime.now(timezone(TIME_ZONE))
            self.logger.info('Deleting phone number {}'.format(phone_number.phone_number.__str__()))

        phone_numbers.bulk_update(phone_numbers, fields=['deleted_at'])

    def handle(self, *args, **options):
        self.initializer_logger()
        processing_date = datetime.now(timezone(TIME_ZONE)).date()
        self.logger.info('Processing date is {}'.format(processing_date.__str__()))
        self.delete_phone_number(processing_date)
