from django.contrib.auth import get_user_model

from api.const import PAYMENT_STATUS
from api.models.base import BaseModel
from django.db import models

from api.models.organization import Company

User = get_user_model()


class CallCenter(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=True)
    charge_by = models.CharField(max_length=128)
    payment_method = models.CharField(max_length=128)
    payment_date = models.DateField()
    payment_notify = models.DateField()
    agent_fee = models.FloatField()
    minute_fee = models.TextField(max_length=1024)
    external_fee = models.FloatField()
    sip_fee_calculation = models.CharField(max_length=128)
    discount_type = models.CharField(max_length=128, null=True)
    discount_value = models.IntegerField(default=0)
    is_enable = models.BooleanField(default=True)
    payment_start_date = models.DateField()
    payment_status = models.CharField(max_length=128, default=PAYMENT_STATUS.UNPAID)
    total_payment_amount = models.IntegerField(default=0)
    credit_payment_amount = models.IntegerField(default=0)
    external_payment_amount = models.IntegerField(default=0)
    discount_amount = models.IntegerField(default=0)
    deposit = models.IntegerField(default=0)
    deposit_warning_threshold = models.IntegerField(default=0)
    last_report_time = models.DateTimeField(null=True)
    trial_expired = models.BooleanField(default=False)
    trial_warning = models.BooleanField(default=False)

    class Meta:
        db_table = 'call_center'


class SipServiceInfo(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    token = models.CharField(max_length=1024)
    sip_company_id = models.IntegerField()

    class Meta:
        db_table = 'sip_service_info'


class AgentRegister(BaseModel):
    number = models.IntegerField()
    use_from = models.DateField()
    use_to = models.DateField()
    charge_from = models.DateField()
    charge_to = models.DateField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        db_table = 'agent_register'


class CallAgent(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    secret = models.CharField(max_length=256)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    agent_register = models.ForeignKey(AgentRegister, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=256)

    class Meta:
        db_table = 'call_agent'

class ExtFileHistory(BaseModel):
    file_name = models.CharField(max_length=256)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    class Meta:
        db_table = 'ext_files'

class CallCenterPaymentHistory(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    charge_by = models.CharField(max_length=128)
    payment_method = models.CharField(max_length=128)
    payment_date = models.DateField()
    payment_notify = models.DateField()
    agent_fee = models.FloatField()
    minute_fee = models.TextField(max_length=1024)
    external_fee = models.FloatField()
    sip_fee_calculation = models.CharField(max_length=128)
    discount_type = models.CharField(max_length=128, null=True)
    discount_value = models.IntegerField(default=0)
    is_enable = models.BooleanField(default=True)
    payment_start_date = models.DateField()
    payment_status = models.CharField(max_length=128, default=PAYMENT_STATUS.UNPAID)
    total_payment_amount = models.IntegerField(default=0)
    credit_payment_amount = models.IntegerField(default=0)
    external_payment_amount = models.IntegerField(default=0)
    discount_amount = models.IntegerField(default=0)

    class Meta:
        db_table = 'callcenter_payment_history'


class CallLog(BaseModel):
    callid = models.CharField(max_length=256, db_index=True)
    calldate = models.DateTimeField(null=True)
    extension = models.CharField(max_length=256, db_index=True)
    phone = models.CharField(max_length=32)
    duration = models.IntegerField(null=True)
    status = models.CharField(max_length=128, null=True)
    recording = models.CharField(max_length=2048, null=True)
    direction = models.CharField(max_length=32, null=True)
    is_telco = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
    chargeable_time = models.IntegerField(default=0)
    provider = models.CharField(max_length=128, default='')
    billsec = models.IntegerField(null=True)
    accountcode = models.CharField(max_length=128, default='')
    ip = models.CharField(max_length=128, default='')
    dstchannel = models.CharField(max_length=128, default='')
    userfield = models.CharField(max_length=128, default='')

    class Meta:
        db_table = 'call_log'
        index_together = [['extension', 'phone', 'status']]


class ExportCallLogsHistory(BaseModel):
    file = models.FileField(upload_to='export_call_logs', null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        db_table = 'export_call_log_histories'


class CallCenterReport(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    call_center = models.ForeignKey(CallCenter, on_delete=models.CASCADE)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    credit_payment_amount = models.IntegerField(default=0)
    external_payment_amount = models.IntegerField(default=0)
    total_payment_amount = models.IntegerField(default=0)
    current_prices = models.IntegerField(default=0)
    current_minutes = models.IntegerField(default=0)

    class Meta:
        db_table = 'call_center_reports'
