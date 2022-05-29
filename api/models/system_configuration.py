from django.db import models

from api.models import BaseModel
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
    name = models.CharField(max_length=1024, unique=True)

    class Meta:
        db_table = 'data_status'


class DataSubStatus(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.ForeignKey(DataStatus, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)

    class Meta:
        db_table = 'data_substatus'
        unique_together = ('name', 'status', 'company')


class DataSource(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024, unique=True)

    class Meta:
        db_table = 'data_sources'


class DataChannel(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)

    class Meta:
        db_table = 'data_channels'
        unique_together = ('name', 'data_source', 'company')
