import json
from datetime import datetime

from api.const import PRODUCT_PAYMENT_METHOD
from api.models.phone_number import MainPhoneNumber, PhoneNumber, Provider, Legal, PhoneNumberStatus, PhoneNumberClient, \
    PhoneNumberActivity, PhoneNumberMonthlyFee, PhoneNumberLockHistory
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneNumberLockHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberLockHistory
        fields = ['id', 'phone_number', 'company', 'checking_lock_date', 'confirm_lock_date', 'unlock_lock_date',
                  'cancel_date', 'created_at']


class MainPhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainPhoneNumber
        fields = ['id', 'name', 'company', 'index', 'color', 'created_at', 'choose_by_default']


class CreateMainPhoneNumberRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreateMainPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = MainPhoneNumberSerializer()


class GetMainPhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetMainPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = MainPhoneNumberSerializer()


class UpdateMainPhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='MainPhoneNumber id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdateMainPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = MainPhoneNumberSerializer()


class FilterMainPhoneNumberRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterMainPhoneNumberRequestSerializer(BasePagingSerializer):
    filter = FilterMainPhoneNumberRequestParamSerializer()


class FilterMainPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=MainPhoneNumberSerializer())


class DeleteMainPhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='MainPhoneNumber id')


class DeleteMainPhoneNumberResponseSerializer(BaseResponseSerializer):
    pass


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['id', 'name', 'company', 'index', 'color', 'created_at', 'choose_by_default']


class CreateProviderRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreateProviderResponseSerializer(BaseResponseSerializer):
    data = ProviderSerializer()


class GetProviderRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetProviderResponseSerializer(BaseResponseSerializer):
    data = ProviderSerializer()


class UpdateProviderRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Provider id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdateProviderResponseSerializer(BaseResponseSerializer):
    data = ProviderSerializer()


class FilterProviderRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterProviderRequestSerializer(BasePagingSerializer):
    filter = FilterProviderRequestParamSerializer()


class FilterProviderResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ProviderSerializer())


class DeleteProviderRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Provider id')


class DeleteProviderResponseSerializer(BaseResponseSerializer):
    pass


class LegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legal
        fields = ['id', 'name', 'company', 'index', 'color', 'created_at', 'choose_by_default']


class CreateLegalRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreateLegalResponseSerializer(BaseResponseSerializer):
    data = LegalSerializer()


class GetLegalRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetLegalResponseSerializer(BaseResponseSerializer):
    data = LegalSerializer()


class UpdateLegalRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Legal id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdateLegalResponseSerializer(BaseResponseSerializer):
    data = LegalSerializer()


class FilterLegalRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterLegalRequestSerializer(BasePagingSerializer):
    filter = FilterLegalRequestParamSerializer()


class FilterLegalResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=LegalSerializer())


class DeleteLegalRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Legal id')


class DeleteLegalResponseSerializer(BaseResponseSerializer):
    pass


class PhoneNumberClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberClient
        fields = ['id', 'name', 'company', 'index', 'color', 'created_at', 'choose_by_default']


class CreatePhoneNumberClientRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreatePhoneNumberClientResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberClientSerializer()


class GetPhoneNumberClientRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetPhoneNumberClientResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberClientSerializer()


class UpdatePhoneNumberClientRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumberClient id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdatePhoneNumberClientResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberClientSerializer()


class FilterPhoneNumberClientRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterPhoneNumberClientRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberClientRequestParamSerializer()


class FilterPhoneNumberClientResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberClientSerializer())


class DeletePhoneNumberClientRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumberClient id')


class DeletePhoneNumberClientResponseSerializer(BaseResponseSerializer):
    pass


class PhoneNumberStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberStatus
        fields = ['id', 'name', 'company', 'index', 'color', 'created_at', 'choose_by_default']


class CreatePhoneNumberStatusRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=True)
    choose_by_default = serializers.BooleanField(required=True)


class CreatePhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberStatusSerializer()


class GetPhoneNumberStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetPhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberStatusSerializer()


class UpdatePhoneNumberStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumberStatus id', required=True)
    name = serializers.CharField(max_length=1024, required=False)
    color = serializers.CharField(max_length=32, required=False)
    index = serializers.IntegerField(required=False)
    choose_by_default = serializers.BooleanField(required=False)


class UpdatePhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberStatusSerializer()


class FilterPhoneNumberStatusRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterPhoneNumberStatusRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberStatusRequestParamSerializer()


class FilterPhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberStatusSerializer())


class DeletePhoneNumberStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumberStatus id')


class DeletePhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    pass


########

class PhoneNumberSerializer(serializers.ModelSerializer):
    # def get_age(self, phone_number):
    #     if phone_number.active_date is None:
    #         return 0
    #
    #     if phone_number.cancel_date is None:
    #         return (datetime.today() - phone_number.active_date).days + 1
    #     return (phone_number.cancel_date - phone_number.active_date).days + 1
    #

    def get_lock_histories(self, phone_number):
        history_list = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, phone_number_id=phone_number.id).order_by(
            'id')[:5]
        return PhoneNumberLockHistorySerializer(history_list, many=True).data

    lock_histories = serializers.SerializerMethodField(source='get_lock_histories')

    class Meta:
        model = PhoneNumber
        fields = ['id', 'phone_number', 'company', 'main_phone_number', 'provider', 'legal', 'phone_number_client',
                  'phone_number_status', 'pickup_date', 'brand', 'lock_provider', 'lock_count', 'phone_number_avg_age',
                  'cancel_date', 'init_fee', 'operate_fee', 'open_fee', 'other_fee', 'created_at', 'note',
                  'init_payment_date', 'open_payment_date', 'operate_payment_date', 'other_payment_date',
                  'client_use_date', 'lock_histories', 'number_in_distributor', 'number_left', 'distributor_name',
                  'lock_telco', 'proxy']


class CreatePhoneNumberRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)
    phone_number = serializers.CharField(max_length=255)
    main_phone_number_id = serializers.IntegerField()
    provider_id = serializers.IntegerField()
    legal_id = serializers.IntegerField()
    phone_number_client_id = serializers.IntegerField(allow_null=True, required=False)
    phone_number_status_id = serializers.IntegerField()
    pickup_date = serializers.DateField()
    client_use_date = serializers.DateField(allow_null=True, required=False)
    brand = serializers.CharField(max_length=512, default='', allow_blank=True)
    lock_provider = serializers.CharField(max_length=512, default='')
    lock_count = serializers.IntegerField(default=0)
    phone_number_avg_age = serializers.FloatField(default=0)
    cancel_date = serializers.DateField(allow_null=True)
    init_fee = serializers.FloatField(default=0)
    operate_fee = serializers.FloatField(default=0)
    open_fee = serializers.FloatField(default=0)
    other_fee = serializers.FloatField(default=0)
    init_payment_date = serializers.DateField()
    open_payment_date = serializers.DateField()
    operate_payment_date = serializers.DateField()
    other_payment_date = serializers.DateField()
    note = serializers.CharField(max_length=1048, default='', allow_blank=True)


class CreatePhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class GetPhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class UpdatePhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumber id', required=True)
    main_phone_number_id = serializers.IntegerField(required=False)
    provider_id = serializers.IntegerField(required=False)
    legal_id = serializers.IntegerField(required=False)
    phone_number_client_id = serializers.IntegerField(allow_null=True, required=False)
    phone_number_status_id = serializers.IntegerField(required=False)
    pickup_date = serializers.DateField(required=False)
    client_use_date = serializers.DateField(allow_null=True, required=False)
    brand = serializers.CharField(max_length=512, default='', required=False, allow_blank=True)
    lock_provider = serializers.CharField(max_length=512, default='', required=False, allow_blank=True)
    lock_count = serializers.IntegerField(default=0, required=False)
    phone_number_avg_age = serializers.FloatField(default=0, required=False)
    cancel_date = serializers.DateField(allow_null=True, required=False)
    init_fee = serializers.FloatField(default=0, required=False)
    operate_fee = serializers.FloatField(default=0, required=False)
    open_fee = serializers.FloatField(default=0, required=False)
    other_fee = serializers.FloatField(default=0, required=False)
    init_payment_date = serializers.DateField(allow_null=True, required=False)
    open_payment_date = serializers.DateField(allow_null=True, required=False)
    operate_payment_date = serializers.DateField(allow_null=True, required=False)
    other_payment_date = serializers.DateField(allow_null=True, required=False)
    note = serializers.CharField(max_length=1048, required=False, default='', allow_blank=True)


class UpdatePhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class FilterPhoneNumberRequestParamSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)
    pickup_date_from = serializers.DateField(required=False, allow_null=True)
    pickup_date_to = serializers.DateField(required=False, allow_null=True)
    lock_date_from = serializers.DateField(required=False, allow_null=True)
    lock_date_to = serializers.DateField(required=False, allow_null=True)
    cancel_date_from = serializers.DateField(required=False, allow_null=True)
    cancel_date_to = serializers.DateField(required=False, allow_null=True)
    payment_date_from = serializers.DateField(required=False, allow_null=True)
    payment_date_to = serializers.DateField(required=False, allow_null=True)
    main_phone_number_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    provider_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    legal_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    phone_number_client_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    phone_number_status_id_list = serializers.ListField(child=serializers.IntegerField(), required=False,
                                                        allow_null=True)
    phone_number_avg_age = serializers.FloatField(required=False, allow_null=True)
    lock_count = serializers.IntegerField(required=False, allow_null=True)
    fee_type_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)


class FilterPhoneNumberRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberRequestParamSerializer()


class FilterPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberSerializer())


class DeletePhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumber id')


class DeletePhoneNumberResponseSerializer(BaseResponseSerializer):
    pass


class PhoneNumberMonthlyFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberMonthlyFee
        fields = ['id', 'phone_number', 'company', 'payment_date', 'on_net_fee', 'off_net_fee', 'created_at',
                  'billing_month']


class CreatePhoneNumberMonthlyFeeRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=True)
    phone_number_id = serializers.IntegerField(required=True)
    on_net_fee = serializers.FloatField(default=0)
    off_net_fee = serializers.FloatField(default=0)
    billing_month = serializers.DateField(required=True)
    payment_date = serializers.DateField(required=True)


class CreatePhoneNumberMonthlyFeeResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberMonthlyFeeSerializer()


class GetPhoneNumberMonthlyFeeRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetPhoneNumberMonthlyFeeResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberMonthlyFeeSerializer()


class UpdatePhoneNumberMonthlyFeeRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumberMonthlyFee id', required=True)
    on_net_fee = serializers.FloatField(required=False)
    off_net_fee = serializers.FloatField(required=False)
    billing_month = serializers.DateField(required=False)
    payment_date = serializers.DateField(required=False)


class UpdatePhoneNumberMonthlyFeeResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberMonthlyFeeSerializer()


class DeletePhoneNumberMonthlyFeeRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumberMonthlyFee id')


class DeletePhoneNumberMonthlyFeeResponseSerializer(BaseResponseSerializer):
    pass


class FilterPhoneNumberMonthlyFeeRequestParamSerializer(serializers.Serializer):
    phone_number_id = serializers.IntegerField()


class FilterPhoneNumberMonthlyFeeRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberMonthlyFeeRequestParamSerializer()


class FilterPhoneNumberMonthlyFeeResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberMonthlyFeeSerializer())


class PhoneNumberActivitySerializer(serializers.ModelSerializer):
    def get_user_id(self, call_agent):
        return call_agent.user_id

    def get_user_name(self, call_agent):
        if call_agent.user is None:
            return None
        return call_agent.user.username

    user_id = serializers.SerializerMethodField(source='get_user_id')
    user_name = serializers.SerializerMethodField(source='get_user_name')

    class Meta:
        model = PhoneNumberActivity
        fields = ['id', 'user_name', 'user_id', 'diff', 'created_at']


class FilterPhoneNumberActivityRequestParamSerializer(serializers.Serializer):
    phone_number_id = serializers.IntegerField()


class FilterPhoneNumberActivityRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberActivityRequestParamSerializer()


class FilterPhoneNumberActivityResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberActivitySerializer())


class BulkUpdatePhoneNumberStatusRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberRequestParamSerializer()
    status = serializers.IntegerField()


class BulkUpdatePhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    pass


class UpdateListPhoneNumberStatusRequestSerializer(serializers.Serializer):
    phone_number_id_list = serializers.ListField(child=serializers.IntegerField())
    phone_number_status_id = serializers.IntegerField()


class UpdateListPhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    pass
