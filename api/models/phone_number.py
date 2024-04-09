import json

from django.contrib.auth import get_user_model

from api.const import PAYMENT_STATUS
from api.models.base import BaseModel, ModelDiffMixin
from django.db import models

from api.models.organization import Company

User = get_user_model()


class MainPhoneNumber(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'main_phone_numbers'


class Provider(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'providers'


class Legal(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'legals'


class PhoneNumberClient(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'phone_number_clients'


class PhoneNumberStatus(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'phone_number_status'


class PhoneNumber(BaseModel, ModelDiffMixin):
    def set_lock_provider(self, provider):
        current_lock = '{"Viettel": false, "Mobifone": false, "Vinaphone": false, "Other": false}' if self.lock_provider == '' else self.lock_provider
        current_lock = json.loads(current_lock)
        if provider in current_lock:
            current_lock[provider] = True
            self.lock_provider = json.dumps(current_lock)
            return

        print('Not found provider')

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=255, db_index=True)
    main_phone_number = models.ForeignKey(MainPhoneNumber, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    legal = models.ForeignKey(Legal, on_delete=models.CASCADE)
    phone_number_client = models.ForeignKey(PhoneNumberClient, null=True, on_delete=models.SET_NULL)
    phone_number_status = models.ForeignKey(PhoneNumberStatus, on_delete=models.CASCADE)
    pickup_date = models.DateField()
    client_use_date = models.DateField(null=True)
    brand = models.CharField(max_length=512, default='')
    lock_provider = models.CharField(max_length=512, default='')
    lock_count = models.IntegerField(default=0)
    phone_number_avg_age = models.FloatField(default=0)
    cancel_date = models.DateField(null=True)
    init_fee = models.FloatField(default=0)
    operate_fee = models.FloatField(default=0)
    open_fee = models.FloatField(default=0)
    other_fee = models.FloatField(default=0)
    init_payment_date = models.DateField(null=True)
    open_payment_date = models.DateField(null=True)
    operate_payment_date = models.DateField(null=True)
    other_payment_date = models.DateField(null=True)
    note = models.CharField(max_length=1048, default='')
    lock_history_id = models.IntegerField(default=0)
    active_date = models.DateField(null=True)
    number_in_distributor = models.CharField(max_length=512, default='')
    number_left = models.CharField(max_length=512, default='')
    distributor_name = models.CharField(max_length=512, default='')
    lock_telco = models.CharField(max_length=512, default='')
    proxy = models.CharField(max_length=512, default='')
    pic = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='pic_id')

    class Meta:
        db_table = 'phone_numbers'
        unique_together = ('company', 'phone_number')


class PhoneNumberLockHistory(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    checking_lock_date = models.DateField()
    confirm_lock_date = models.DateField(null=True)
    unlock_lock_date = models.DateField(null=True)
    cancel_date = models.DateField(null=True)

    class Meta:
        db_table = 'phone_number_lock_histories'


class PhoneNumberMonthlyFee(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    on_net_fee = models.FloatField(default=0)
    off_net_fee = models.FloatField(default=0)
    billing_month = models.DateField()
    payment_date = models.DateField()

    class Meta:
        db_table = 'phone_number_monthly_fees'


class PhoneNumberActivity(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diff = models.CharField(max_length=4096, default='')

    class Meta:
        db_table = 'phone_number_activities'


# class ImportPhoneNumberRecords(BaseModel):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE)
#     file = models.FileField(upload_to='uploads/%Y/%m/%d/')
#
#     class Meta:
#         db_table = 'import_order_records'