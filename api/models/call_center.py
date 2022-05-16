from django.contrib.auth import get_user_model

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
    call_center_user = models.CharField(max_length=256)
    call_center_password = models.CharField(max_length=1024)
    discount_type = models.CharField(max_length=128, null=True)
    discount_value = models.IntegerField(default=0)
    is_enable = models.BooleanField(default=True)

    class Meta:
        db_table = 'call_center'


class CallAgent(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    secret = models.CharField(max_length=256)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    sip_id = models.IntegerField()

    class Meta:
        db_table = 'call_agent'


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


class CallCenterPaymentHistory(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=True)
    charge_by = models.CharField(max_length=128)
    payment_method = models.CharField(max_length=128)
    payment_date = models.DateField()
    payment_notify = models.DateField()
    agent_fee = models.FloatField()
    minute_fee = models.TextField(max_length=1024)
    external_fee = models.FloatField()
    sip_fee_calculation = models.CharField(max_length=128)
    call_center_user = models.CharField(max_length=256)
    call_center_password = models.CharField(max_length=1024)
    discount_type = models.CharField(max_length=128, null=True)
    discount_value = models.IntegerField(default=0)

    class Meta:
        db_table = 'callcenter_payment_history'


class CallLog(BaseModel):
    callid = models.CharField(max_length=256)
    calldate = models.DateTimeField()
    extension = models.CharField(max_length=256)
    phone = models.CharField(max_length=32)
    duration = models.IntegerField()
    status = models.CharField(max_length=128)
    recordingfile = models.CharField(max_length=2048)
    is_telco = models.BooleanField(default=False)

    class Meta:
        db_table = 'call_log'