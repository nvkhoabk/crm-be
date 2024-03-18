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
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=255, db_index=True, unique=True)
    main_phone_number = models.ForeignKey(MainPhoneNumber, on_delete=models.CASCADE)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    legal = models.ForeignKey(Legal, on_delete=models.CASCADE)
    phone_number_client = models.ForeignKey(PhoneNumberClient, on_delete=models.CASCADE)
    phone_number_status = models.ForeignKey(PhoneNumberStatus, on_delete=models.CASCADE)
    pickup_date = models.DateField()
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

    class Meta:
        db_table = 'phone_numbers'


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
    user = User()
    diff = models.CharField(max_length=4096, default='')

    class Meta:
        db_table = 'phone_number_activities'
