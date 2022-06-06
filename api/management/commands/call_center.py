from dateutil.relativedelta import relativedelta
from datetime import datetime

from api.const import CALL_AGENT_STATUS
from api.models.call_center import CallCenter, AgentRegister, CallAgent
from django.core.management.base import BaseCommand
from pytz import timezone

from api.services.call_center import DisableCallCenterService


class Command(BaseCommand):
    help = 'Runs a job'

    def disable_call_center(self, tomorrow):
        call_centers = CallCenter.objects.filter(payment_date=tomorrow, deleted_at__isnull=True, is_enable=True)

        print("Call center:", call_centers)
        for call_center in call_centers:
            service = DisableCallCenterService()
            service.serve(**{'company_id': call_center.company_id})

    def disable_call_agent(self, tomorrow):
        agent_registers = AgentRegister.objects.filter(deleted_at__isnull=True, use_to=tomorrow)
        CallAgent.objects.filter(deleted_at__isnull=True, status=CALL_AGENT_STATUS.ACTIVE,
                                 agent_register_id__in=agent_registers.values_list('id',
                                                                                   flat=True)).update(
            status=CALL_AGENT_STATUS.INACTIVE)

    def handle(self, *args, **options):
        print("Now:" , datetime.now(timezone('Asia/Ho_Chi_Minh')))
        tomorrow = datetime.now(timezone('Asia/Ho_Chi_Minh')).date() - relativedelta(days=1)
        print("tomorrow:", tomorrow)
        self.disable_call_center(tomorrow)
        self.disable_call_center(tomorrow)

