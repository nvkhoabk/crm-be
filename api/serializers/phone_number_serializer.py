import json
from datetime import datetime

from api.const import PRODUCT_PAYMENT_METHOD
from api.models.phone_number import MainPhoneNumber, PhoneNumber, Provider, Legal, PhoneNumberStatus, PhoneNumberClient, \
    PhoneNumberActivity, PhoneNumberMonthlyFee, PhoneNumberLockHistory, PhoneNumberTechnicalActivity
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.serializers.data_serializer import ExportOrderRequestRecordSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneNumberLockHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumberLockHistory
        fields = ['id', 'phone_number', 'company', 'checking_lock_date', 'confirm_lock_date', 'unlock_lock_date',
                  'cancel_date', 'created_at', 'viettel_lock_date', 'mobifone_lock_date', 'vinaphone_lock_date',
                  'other_lock_date', 'send_provider_date']


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
    def get_pic_name(self, client):
        if client.pic is None:
            return ''
        return User.objects.get(pk=client.pic_id).username

    pic_name = serializers.SerializerMethodField(source='get_pic')

    class Meta:
        model = PhoneNumberClient
        fields = ['id', 'name', 'company', 'index', 'color', 'pic_id', 'pic_name', 'created_at', 'choose_by_default']


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
    def get_lock_histories(self, phone_number):
        id_list = [phone_number.lock_history_id, phone_number.viettel_lock_history_id,
                   phone_number.mobifone_lock_history_id, phone_number.vinaphone_lock_history_id,
                   phone_number.other_lock_history_id]
        history_list = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, id__in=id_list).order_by('-id')
        return PhoneNumberLockHistorySerializer(history_list, many=True).data

    # def get_last_viettel_unlock_date(self, phone_number):
    #     lock = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, phone_number=phone_number).exclude(
    #         viettel_lock_date__isnull=True).exclude(unlock_lock_date__isnull=True).order_by('-id')
    #     if lock:
    #         return lock.first().unlock_lock_date
    #     return None
    # def get_last_mobifone_unlock_date(self, phone_number):
    #     lock = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, phone_number=phone_number).exclude(
    #         mobifone_lock_date__isnull=True).exclude(unlock_lock_date__isnull=True).order_by('-id')
    #     if lock:
    #         return lock.first().unlock_lock_date
    #     return None
    # def get_last_vinaphone_unlock_date(self, phone_number):
    #     lock = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, phone_number=phone_number).exclude(
    #         vinaphone_lock_date__isnull=True).exclude(unlock_lock_date__isnull=True).order_by('-id')
    #     if lock:
    #         return lock.first().unlock_lock_date
    #     return None
    # def get_last_other_unlock_date(self, phone_number):
    #     lock = PhoneNumberLockHistory.objects.filter(deleted_at__isnull=True, phone_number=phone_number).exclude(
    #         other_lock_date__isnull=True).exclude(unlock_lock_date__isnull=True).order_by('-id')
    #     if lock:
    #         return lock.first().unlock_lock_date
    #     return None
    #
    # last_viettel_unlock_date = serializers.SerializerMethodField(source='get_last_viettel_unlock_date')
    # last_mobifone_unlock_date = serializers.SerializerMethodField(source='get_last_mobifone_unlock_date')
    # last_vinaphone_unlock_date = serializers.SerializerMethodField(source='get_last_vinaphone_unlock_date')
    # last_other_unlock_date = serializers.SerializerMethodField(source='get_last_other_unlock_date')
    lock_histories = serializers.SerializerMethodField(source='get_lock_histories')

    class Meta:
        model = PhoneNumber
        fields = ['id', 'phone_number', 'company', 'main_phone_number', 'provider', 'legal', 'phone_number_client',
                  'phone_number_status', 'pickup_date', 'brand', 'lock_provider', 'lock_count', 'phone_number_avg_age',
                  'cancel_date', 'init_fee', 'operate_fee', 'open_fee', 'other_fee', 'created_at', 'note',
                  'init_payment_date', 'open_payment_date', 'operate_payment_date', 'other_payment_date',
                  'client_use_date', 'lock_histories', 'number_in_distributor', 'number_left', 'distributor_name',
                  'lock_telco', 'proxy', 'pic_id', 'active_date', 'lock_history_id', 'viettel_lock_history_id',
                  'mobifone_lock_history_id', 'vinaphone_lock_history_id', 'other_lock_history_id',
                  'viettel_lock_count', 'mobifone_lock_count', 'vinaphone_lock_count', 'other_lock_count',
                  'updated_at', 'viettel_using_status', 'mobifone_using_status', 'vinaphone_using_status',
                  'other_using_status', 'viettel_unlocking_status', 'mobifone_unlocking_status',
                  'vinaphone_unlocking_status', 'other_unlocking_status', 'provider_cancel_date',
                  'last_viettel_unlock_date', 'last_mobifone_unlock_date', 'last_vinaphone_unlock_date',
                  'last_other_unlock_date', 'last_viettel_lock_date', 'last_mobifone_lock_date',
                  'last_vinaphone_lock_date', 'last_other_lock_date', 'last_viettel_send_provider_date',
                  'last_mobifone_send_provider_date', 'last_vinaphone_send_provider_date',
                  'last_other_send_provider_date', 'device', 'port']


class PhoneNumberTechnicalActivitySerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='phone_number.phone_number', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = PhoneNumberTechnicalActivity
        fields = ['id', 'phone_number', 'phone_number_id', 'company', 'user_name', 'user_id', 'viettel_using_status',
                  'mobifone_using_status', 'vinaphone_using_status',
                  'other_using_status', 'viettel_unlocking_status', 'mobifone_unlocking_status',
                  'vinaphone_unlocking_status', 'other_unlocking_status', 'viettel_lock_date',
                  'mobifone_lock_date', 'vinaphone_lock_date', 'other_lock_date', 'viettel_unlock_date',
                  'mobifone_unlock_date', 'created_at', 'vinaphone_unlock_date',
                  'other_unlock_date', 'phone_number_status_id', 'old_mobifone_using_status', 'old_vinaphone_using_status',
                  'old_other_using_status', 'old_viettel_unlocking_status', 'old_mobifone_unlocking_status',
                  'old_vinaphone_unlocking_status', 'old_other_unlocking_status',
                  'old_viettel_lock_date', 'old_mobifone_lock_date', 'old_vinaphone_lock_date', 'old_other_lock_date',
                  'old_viettel_unlock_date', 'old_mobifone_unlock_date',
                  'old_vinaphone_unlock_date', 'old_other_unlock_date', 'old_phone_number_status_id']


class CreatePhoneNumberRequestSerializer(serializers.Serializer):
    USING_STATUS_CHOICES = (
        ('IN_QUEUE', 'IN_QUEUE'),
        ('OPEN', 'OPEN'),
        ('LOCK', 'LOCK'),
        ('USING', 'USING'),
    )

    UNLOCKING_STATUS_CHOICES = (
        ('AVAILABLE', 'AVAILABLE'),
        ('SENT_PROVIDER', 'SENT_PROVIDER'),
        ('OPENED', 'OPENED'),
        ('WRONG_REPORT', 'WRONG_REPORT'),
    )

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
    lock_provider = serializers.CharField(max_length=512, allow_blank=True)
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
    viettel_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, default='IN_QUEUE')
    mobifone_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, default='IN_QUEUE')
    vinaphone_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, default='IN_QUEUE')
    other_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, default='IN_QUEUE')
    viettel_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, default='AVAILABLE')
    mobifone_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, default='AVAILABLE')
    vinaphone_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, default='AVAILABLE')
    other_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, default='AVAILABLE')
    provider_cancel_date = serializers.DateField(allow_null=True, required=False)
    device = serializers.CharField(max_length=512, default='')
    port = serializers.IntegerField(allow_null=True, required=False)


class CreatePhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class GetPhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class UpdatePhoneNumberRequestSerializer(serializers.Serializer):
    USING_STATUS_CHOICES = (
        ('IN_QUEUE', 'IN_QUEUE'),
        ('OPEN', 'OPEN'),
        ('LOCK', 'LOCK'),
        ('USING', 'USING'),
    )

    UNLOCKING_STATUS_CHOICES = (
        ('AVAILABLE', 'AVAILABLE'),
        ('SENT_PROVIDER', 'SENT_PROVIDER'),
        ('OPENED', 'OPENED'),
        ('WRONG_REPORT', 'WRONG_REPORT'),
    )

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
    viettel_lock_date = serializers.DateField(allow_null=True, required=False)
    mobifone_lock_date = serializers.DateField(allow_null=True, required=False)
    vinaphone_lock_date = serializers.DateField(allow_null=True, required=False)
    other_lock_date = serializers.DateField(allow_null=True, required=False)
    viettel_unlock_date = serializers.DateField(allow_null=True, required=False)
    mobifone_unlock_date = serializers.DateField(allow_null=True, required=False)
    vinaphone_unlock_date = serializers.DateField(allow_null=True, required=False)
    other_unlock_date = serializers.DateField(allow_null=True, required=False)
    viettel_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, required=False)
    mobifone_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, required=False)
    vinaphone_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, required=False)
    other_using_status = serializers.ChoiceField(choices=USING_STATUS_CHOICES, required=False)
    viettel_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, required=False)
    mobifone_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, required=False)
    vinaphone_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, required=False)
    other_unlocking_status = serializers.ChoiceField(choices=UNLOCKING_STATUS_CHOICES, required=False)
    provider_cancel_date = serializers.DateField(allow_null=True, required=False)
    device = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    port = serializers.IntegerField(allow_null=True, required=False)


class UpdatePhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class FilterPhoneNumberRequestParamSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)
    pickup_date_from = serializers.DateField(required=False, allow_null=True)
    pickup_date_to = serializers.DateField(required=False, allow_null=True)
    client_use_date_from = serializers.DateField(required=False, allow_null=True)
    client_use_date_to = serializers.DateField(required=False, allow_null=True)
    lock_date_from = serializers.DateField(required=False, allow_null=True)
    lock_date_to = serializers.DateField(required=False, allow_null=True)
    cancel_date_from = serializers.DateField(required=False, allow_null=True)
    cancel_date_to = serializers.DateField(required=False, allow_null=True)
    payment_date_from = serializers.DateField(required=False, allow_null=True)
    payment_date_to = serializers.DateField(required=False, allow_null=True)
    main_phone_number_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    provider_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    legal_id_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    phone_number_client_list = serializers.ListField(child=serializers.IntegerField(allow_null=True), required=False, allow_null=True)
    phone_number_status_id_list = serializers.ListField(child=serializers.IntegerField(), required=False,
                                                        allow_null=True)
    phone_number_avg_age = serializers.FloatField(required=False, allow_null=True)
    lock_count = serializers.IntegerField(required=False, allow_null=True)
    lock_count_type = serializers.ListField(child=serializers.CharField(), default=[0], required=False)
    fee_type_list = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    pics = serializers.ListField(child=serializers.IntegerField(allow_null=True), required=False, allow_null=True)
    sale_pics = serializers.ListField(child=serializers.IntegerField(allow_null=True), required=False, allow_null=True)
    viettel_using_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    mobifone_using_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    vinaphone_using_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    other_using_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    viettel_unlocking_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    mobifone_unlocking_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    vinaphone_unlocking_status = serializers.CharField(max_length=100, required=False, allow_null=True,
                                                       allow_blank=True)
    other_unlocking_status = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    device = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    port = serializers.IntegerField(allow_null=True, required=False)


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


class FilterPhoneNumberLockHistoryResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberLockHistorySerializer())


class BulkUpdatePhoneNumberStatusRequestSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberRequestParamSerializer()
    status = serializers.IntegerField()
    telco_list = serializers.ListField(child=serializers.CharField(), default=[])


class BulkUpdatePhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    pass


class UpdateListPhoneNumberStatusRequestSerializer(serializers.Serializer):
    phone_number_id_list = serializers.ListField(child=serializers.IntegerField())
    phone_number_status_id = serializers.IntegerField()
    mark_delete = serializers.BooleanField(default=False)
    telco_list = serializers.ListField(child=serializers.CharField(), default=[])


class UpdateListPhoneNumberStatusResponseSerializer(BaseResponseSerializer):
    pass


class TechnicalStaffStatisticSerializer(serializers.Serializer):
    user = serializers.CharField()
    count = serializers.IntegerField()


class StatisticPhoneNumberSerializer(serializers.Serializer):
    age_avg = serializers.FloatField()
    total_init_fee = serializers.FloatField()
    total_operate_fee = serializers.FloatField()
    total_open_fee = serializers.FloatField()
    total_other_fee = serializers.FloatField()
    technical_staff = serializers.ListField(child=TechnicalStaffStatisticSerializer())


class GetStatisticPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = StatisticPhoneNumberSerializer()


class PhoneNumberFileSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    phone_number = serializers.CharField(max_length=255)
    main_phone_number = serializers.CharField(required=False)
    provider = serializers.CharField(required=False)
    legal = serializers.CharField(required=False)
    phone_number_client = serializers.CharField(allow_null=True, required=False)
    phone_number_status = serializers.CharField(required=False)
    pickup_date = serializers.DateField(required=False)
    cancel_date = serializers.DateField(allow_null=True, required=False)
    init_fee = serializers.FloatField(default=0)
    operate_fee = serializers.FloatField(default=0)
    open_fee = serializers.FloatField(default=0)
    other_fee = serializers.FloatField(default=0)
    init_payment_date = serializers.DateField(required=False)
    open_payment_date = serializers.DateField(required=False)
    operate_payment_date = serializers.DateField(required=False)
    other_payment_date = serializers.DateField(required=False)
    note = serializers.CharField(max_length=1048, default='', allow_blank=True, required=False)
    payment_date = serializers.DateField(required=False)
    on_net_fee = serializers.FloatField(default=0)
    off_net_fee = serializers.FloatField(default=0)
    billing_month = serializers.DateField(required=False)
    error_codes = serializers.ListField(child=serializers.IntegerField())
    row_number = serializers.IntegerField()


class ImportPhoneNumberRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rows = serializers.ListField(child=PhoneNumberFileSerializer())


class ImportPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = ImportPhoneNumberRecordSerializer()


class ImportPhoneNumberRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    file = serializers.FileField(allow_empty_file=False)
    type = serializers.CharField()


class ConfirmImportPhoneNumberRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    id = serializers.IntegerField()
    type = serializers.CharField()


class ConfirmImportPhoneNumberResponseSerializer(BaseResponseSerializer):
    pass


class CheckPhoneNumberRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumber id', required=True)
    phone_number_status_id = serializers.IntegerField(required=True)
    viettel_lock_date = serializers.DateField(allow_null=True, required=False)
    mobifone_lock_date = serializers.DateField(allow_null=True, required=False)
    vinaphone_lock_date = serializers.DateField(allow_null=True, required=False)
    other_lock_date = serializers.DateField(allow_null=True, required=False)
    viettel_unlock_date = serializers.DateField(allow_null=True, required=False)
    mobifone_unlock_date = serializers.DateField(allow_null=True, required=False)
    vinaphone_unlock_date = serializers.DateField(allow_null=True, required=False)
    other_unlock_date = serializers.DateField(allow_null=True, required=False)


class CheckPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class FilterPhoneNumberTechnicalActivityParamSerializer(serializers.Serializer):
    created_at_from = serializers.DateTimeField(required=False, allow_null=True)
    created_at_to = serializers.DateTimeField(required=False, allow_null=True)
    pics = serializers.ListField(child=serializers.IntegerField(allow_null=True))
    phone_number = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)


class FilterPhoneNumberTechnicalActivityRequestParamSerializer(BasePagingSerializer):
    filter = FilterPhoneNumberTechnicalActivityParamSerializer()


class FilterPhoneNumberTechnicalActivityResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PhoneNumberTechnicalActivitySerializer())


class RevertPhoneNumberTechnicalActivityRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='PhoneNumber id', required=True)

class RevertPhoneNumberTechnicalActivityResponseSerializer(BaseResponseSerializer):
    data = PhoneNumberSerializer()


class ExportPhoneNumberRequestSerializer(FilterPhoneNumberRequestParamSerializer):
    pass


class ExportPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = ExportOrderRequestRecordSerializer()


class CopyPhoneNumberResponseSerializer(BaseResponseSerializer):
    data = serializers.CharField()
