import json
import math

from api.const import PAYMENT_STATUS, TELECOM_NUMBER
from api.models.call_center import CallCenter, CallAgent, AgentRegister, ExportCallLogsHistory
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from rest_framework import serializers

import api.utils.call_center as call_center_utils


class CallCenterSerializer(serializers.ModelSerializer):
    def get_minute_fee(self, call_center):
        minute_fee = call_center_utils.get_minute_fee(call_center)
        return {
            'Viettel': minute_fee[TELECOM_NUMBER.VIETTEL],
            'Mobi': minute_fee[TELECOM_NUMBER.MOBI],
            'Vina': minute_fee[TELECOM_NUMBER.VINA]
        }

    def get_company_name(self, call_center):
        return call_center.company.name

    minute_fee = serializers.SerializerMethodField(source='get_minute_fee')
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = CallCenter
        fields = ['id', 'company_id', 'charge_by', 'payment_method', 'payment_date', 'payment_notify', 'agent_fee',
                  'minute_fee', 'external_fee', 'sip_fee_calculation', 'is_enable', 'discount_type', 'discount_value',
                  'company_name', 'payment_start_date', 'payment_status', 'total_payment_amount',
                  'credit_payment_amount', 'external_payment_amount', 'discount_amount', 'deposit',
                  'deposit_warning_threshold', 'trial_warning', 'trial_expired']


class CallAgentSerializer(serializers.ModelSerializer):
    def get_user_id(self, call_agent):
        return call_agent.user_id

    def get_user_name(self, call_agent):
        if call_agent.user is None:
            return None
        return call_agent.user.username

    user_id = serializers.SerializerMethodField(source='get_user_id')
    user_name = serializers.SerializerMethodField(source='get_user_name')

    class Meta:
        model = CallAgent
        fields = ['id', 'name', 'user_id', 'user_name']


class CreateCallCenterRequestSerializer(serializers.Serializer):
    CHARGE_CHOICES = (
        ('AGENT', 'AGENT'),
        ('MINUTE', 'MINUTE')
    )
    PAYMENT_METHOD_CHOICES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT')
    )
    SIP_FEE_CALCULATION_CHOICES = (
        ('6+1', '6+1'),
        ('60+1', '60+1')
    )
    DISCOUNT_TYPE_CHOICES = (
        ('VALUE', 'VALUE'),
        ('PERCENT', 'PERCENT')
    )

    company_id = serializers.IntegerField(required=True)
    charge_by = serializers.ChoiceField(choices=CHARGE_CHOICES, allow_blank=False, required=True)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, allow_blank=False, required=True)
    payment_date = serializers.DateField(required=True)
    payment_notify = serializers.DateField(required=True)
    agent_fee = serializers.FloatField(required=False)
    minute_fee = serializers.DictField(required=False)
    external_fee = serializers.FloatField(required=False)
    sip_fee_calculation = serializers.ChoiceField(choices=SIP_FEE_CALCULATION_CHOICES, required=False, allow_blank=True)
    discount_type = serializers.ChoiceField(choices=DISCOUNT_TYPE_CHOICES, allow_blank=False, required=False)
    discount_value = serializers.IntegerField(required=False)
    payment_start_date = serializers.DateField(required=True)
    deposit = serializers.IntegerField(required=False)
    deposit_warning_threshold = serializers.IntegerField(required=False)


class CreateCallCenterResponseSerializer(BaseResponseSerializer):
    data = CallCenterSerializer()


class UpdateCallCenterRequestSerializer(serializers.Serializer):
    CHARGE_CHOICES = (
        ('AGENT', 'AGENT'),
        ('MINUTE', 'MINUTE')
    )
    PAYMENT_METHOD_CHOICES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT')
    )
    SIP_FEE_CALCULATION_CHOICES = (
        ('6+1', '6+1'),
        ('60+1', '60+1')
    )
    DISCOUNT_TYPE_CHOICES = (
        ('VALUE', 'VALUE'),
        ('PERCENT', 'PERCENT')
    )
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_STATUS.PAID, PAYMENT_STATUS.PAID),
        (PAYMENT_STATUS.UNPAID, PAYMENT_STATUS.UNPAID)
    )

    company_id = serializers.IntegerField(required=True)
    charge_by = serializers.ChoiceField(choices=CHARGE_CHOICES, allow_blank=False, required=False)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, allow_blank=False, required=False)
    payment_date = serializers.DateField(required=False)
    payment_notify = serializers.DateField(required=False)
    agent_fee = serializers.FloatField(required=False)
    minute_fee = serializers.DictField(required=False)
    external_fee = serializers.FloatField(required=False)
    sip_fee_calculation = serializers.ChoiceField(choices=SIP_FEE_CALCULATION_CHOICES, required=False, allow_blank=False)
    discount_type = serializers.ChoiceField(choices=DISCOUNT_TYPE_CHOICES, allow_blank=False, required=False)
    discount_value = serializers.IntegerField(required=False)
    payment_start_date = serializers.DateField(required=False)
    payment_status = serializers.ChoiceField(choices=PAYMENT_STATUS_CHOICES)
    deposit = serializers.IntegerField(required=False)
    deposit_warning_threshold = serializers.IntegerField(required=False)


class FilterCallCenterParamSerializer(serializers.Serializer):
    CHARGE_CHOICES = (
        ('AGENT', 'AGENT'),
        ('MINUTE', 'MINUTE')
    )
    PAYMENT_METHOD_CHOICES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT')
    )
    SIP_FEE_CALCULATION_CHOICES = (
        ('6+1', '6+1'),
        ('60+1', '60+1')
    )
    DISCOUNT_TYPE_CHOICES = (
        ('VALUE', 'VALUE'),
        ('PERCENT', 'PERCENT')
    )

    company_id = serializers.IntegerField(required=False, allow_null=True)
    charge_by = serializers.ChoiceField(choices=CHARGE_CHOICES, allow_blank=False, required=False, allow_null=True)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, allow_blank=False, required=False,
                                             allow_null=True)
    sip_fee_calculation = serializers.ChoiceField(choices=SIP_FEE_CALCULATION_CHOICES, required=False,
                                                  allow_blank=False, allow_null=True)
    discount_type = serializers.ChoiceField(choices=DISCOUNT_TYPE_CHOICES, allow_blank=False, required=False,
                                            allow_null=True)

    from_date = serializers.DateField(allow_null=True, required=False)
    to_date = serializers.DateField(allow_null=True, required=False)


class FilterCallCenterResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CallCenterSerializer())


class FilterCallCenterRequestSerializer(BasePagingSerializer):
    filter = FilterCallCenterParamSerializer()


class UpdateCallCenterResponseSerializer(BaseResponseSerializer):
    data = CallCenterSerializer()


class EnableCallCenterRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)


class EnableCallCenterResponseSerializer(BaseResponseSerializer):
    data = CallCenterSerializer()


class DisableCallCenterRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)


class DisableCallCenterResponseSerializer(BaseResponseSerializer):
    data = CallCenterSerializer()


class CalculatePayemntCallCenterResponseSerializer(BaseResponseSerializer):
    pass


class GetCallCenterRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)


class GetCallCenterResponseSerializer(BaseResponseSerializer):
    data = CallCenterSerializer()


class GetAgentsRequestSerializer(serializers.Serializer):
    pass


class GetAgentsResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CallAgentSerializer())


class UpdateAgentsParamSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, help_text='call agent id')
    user_id = serializers.IntegerField(required=False, allow_null=True)


class UpdateAgentsRequestSerializer(serializers.Serializer):
    data = serializers.ListField(child=UpdateAgentsParamSerializer())


class UpdateAgentsResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CallAgentSerializer())


class CallHistorySerializer(serializers.Serializer):
    dest_number = serializers.CharField()
    calldate = serializers.DateTimeField()
    record_url = serializers.CharField()
    direction = serializers.CharField()
    duration = serializers.IntegerField()


class GetCompanyCallHistoryRequestParam(serializers.Serializer):
    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)
    number = serializers.CharField(required=False)
    user_id = serializers.IntegerField(required=False, allow_null=True)


class GetCompanyCallHistoryRequestSerializer(BasePagingSerializer):
    filter = GetCompanyCallHistoryRequestParam()


class GetCompanyCallHistoryResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CallHistorySerializer())


class GetUserCallHistoryRequestSerializer(BasePagingSerializer):
    phone_number = serializers.CharField(allow_blank=True, allow_null=True, required=False)


class GetUserCallHistoryResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CallHistorySerializer())


class CallReportSerializer(serializers.Serializer):
    agent_name = serializers.CharField()
    number_call_out = serializers.IntegerField()
    duration_call_out = serializers.IntegerField()
    number_call_in = serializers.IntegerField()
    duration_call_in = serializers.IntegerField()
    total_duration = serializers.IntegerField()


class GetCallReportRequestParamSerializer(serializers.Serializer):
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)


class GetCallReportRequestSerializer(BasePagingSerializer):
    filter = GetCallReportRequestParamSerializer()


class GetCallReportResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CallReportSerializer())


class AgentRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRegister
        fields = ['id', 'number', 'use_from', 'use_to', 'charge_from', 'charge_to']


class CreateAgentResiterRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)
    number = serializers.IntegerField(required=True)
    use_from = serializers.DateField(required=True)
    use_to = serializers.DateField(required=True)
    charge_from = serializers.DateField(required=True)
    charge_to = serializers.DateField(required=True)


class CreateAgentRegisterResponseSerializer(BaseResponseSerializer):
    data = AgentRegisterSerializer()


class DeleteAgentRegisterRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Agent Register id')


class DeleteAgentRegisterResponseSerializer(serializers.Serializer):
    pass


class FilterAgentRegisterRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()


class FilterAgentRegisterRequestSerializer(BasePagingSerializer):
    filter = FilterAgentRegisterRequestParamSerializer()


class FilterAgentRegisterResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=AgentRegisterSerializer())


class ExternalPaymentReportSerializer(serializers.Serializer):
    call_date = serializers.DateTimeField()
    number = serializers.CharField(max_length=128)
    duration = serializers.IntegerField()
    fee = serializers.IntegerField()
    chargeable_time = serializers.IntegerField()


class GetExternalPaymentReportRequestSerializer(BasePagingSerializer):
    REPORT_TYPE_CHOICES = (
        ('CURRENT_MONTH', 'CURRENT_MONTH'),
        ('PREVIOUS_MONTH', 'PREVIOUS_MONTH')
    )
    PROVIDER = (
        (TELECOM_NUMBER.OTHER, TELECOM_NUMBER.OTHER),
        (TELECOM_NUMBER.VIETTEL, TELECOM_NUMBER.VIETTEL),
        (TELECOM_NUMBER.MOBI, TELECOM_NUMBER.MOBI),
        (TELECOM_NUMBER.VINA, TELECOM_NUMBER.VINA),
    )
    report_type = serializers.ChoiceField(choices=REPORT_TYPE_CHOICES)
    provider = serializers.ChoiceField(choices=PROVIDER)


class GetExternalPaymentReportResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ExternalPaymentReportSerializer())


class GetCreditPaymentRequestSerializer(serializers.Serializer):
    REPORT_TYPE_CHOICES = (
        ('CURRENT_MONTH', 'CURRENT_MONTH'),
        ('PREVIOUS_MONTH', 'PREVIOUS_MONTH')
    )
    report_type = serializers.ChoiceField(choices=REPORT_TYPE_CHOICES)
    company_id = serializers.IntegerField(required=False, default=0)


class ExportCallLogsRequestSerializer(serializers.Serializer):
    REPORT_TYPE_CHOICES = (
        ('CURRENT_MONTH', 'CURRENT_MONTH'),
        ('PREVIOUS_MONTH', 'PREVIOUS_MONTH')
    )
    report_type = serializers.ChoiceField(choices=REPORT_TYPE_CHOICES)
    company_id = serializers.IntegerField(required=False, default=0)

class CallCenterPriceSerializer(serializers.Serializer):
    viettel = serializers.IntegerField()
    vinaphone = serializers.IntegerField()
    mobifone = serializers.IntegerField()
    other = serializers.IntegerField()


class CreditPaymentReportSerializer(serializers.Serializer):
    credit_payment_amount = serializers.IntegerField()
    external_payment_amount = serializers.IntegerField()
    payment_method = serializers.CharField(max_length=256)
    payment_date = serializers.DateField()
    status = serializers.CharField(max_length=128)
    discount_type = serializers.CharField(max_length=128)
    discount_value = serializers.IntegerField()
    discount_amount = serializers.IntegerField()
    total_payment_amount = serializers.IntegerField()
    current_prices = CallCenterPriceSerializer()
    current_minutes = CallCenterPriceSerializer()


class GetCreditPaymentResponseSerializer(BaseResponseSerializer):
    data = CreditPaymentReportSerializer()


class CallLogRequestSerializer(serializers.Serializer):
    callid = serializers.CharField(max_length=256, required=True)
    calldate = serializers.DateTimeField(required=True)
    extension = serializers.CharField(max_length=256, required=True)
    phone = serializers.CharField(max_length=32, required=True)
    duration = serializers.IntegerField(required=True)
    status = serializers.CharField(max_length=128)
    recording = serializers.CharField(max_length=2048, required=True)
    billsec = serializers.IntegerField(required=False, default=0)
    accountcode = serializers.CharField(required=False, default='', allow_blank=True, max_length=128)
    ip = serializers.CharField(required=False, default='', allow_blank=True, max_length=128)
    dstchannel = serializers.CharField(required=False, default='', allow_blank=True, max_length=128)
    userfield = serializers.CharField(required=False, default='', allow_blank=True, max_length=1024)


class CallLogResponseSerializer(BaseResponseSerializer):
    None

class ErrorExtFileSerializer(serializers.Serializer):
    error_call_agents = serializers.ListField(child=serializers.CharField())

class UploadExtFileResponseSerializer(BaseResponseSerializer):
    data = ErrorExtFileSerializer()

class UploadExtFileRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)
    agent_register_id = serializers.IntegerField(required=True)
    file = serializers.FileField(max_length=None, allow_empty_file=False)

class DownloadExtFileRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)

class ExportCallLogsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExportCallLogsHistory
        fields = ['id', 'file']

class ExportCallLogsResponseSerializer(BaseResponseSerializer):
    data = ExportCallLogsHistorySerializer()

class EndCallOutRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(default='')
