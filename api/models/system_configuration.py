from django.db import models

from api.models.base import BaseModel
from api.models.organization import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyEmail(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.CharField(max_length=1024)
    password = models.CharField(max_length=1024, null=True)

    class Meta:
        db_table = 'company_emails'


class DataStatus(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'data_status'


class DataSubStatus(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data_status = models.ForeignKey(DataStatus, related_name='data_sub_status', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    color = models.CharField(max_length=32)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'data_substatus'
        unique_together = ('name', 'data_status', 'company')


class DataSource(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True)
    index = models.IntegerField(default=0)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'data_sources'


class DataChannel(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, related_name='data_channels', on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    index = models.IntegerField(default=0)
    choose_by_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'data_channels'
        unique_together = ('name', 'data_source', 'company')


class EmailSyntax(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    code = models.CharField(max_length=64)
    column_name = models.CharField(max_length=256)
    description = models.TextField(default='')

    class Meta:
        db_table = 'email_syntax'
        unique_together = ('code', 'company')


class EmailTemplate(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    code = models.CharField(max_length=128)
    email_name = models.TextField()
    content = models.TextField()

    class Meta:
        db_table = 'email_templates'
        unique_together = ('code', 'company')


class CompanyLogo(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, unique=True)
    logo = models.FileField(upload_to='uploads/%Y/%m/%d/')

    class Meta:
        db_table = 'company_logos'