from django.db import models

from api.models import BaseModel
from api.models.organization import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyEmail(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email = models.CharField(max_length=1024)
    password = models.CharField(max_length=1024, null=True)


class Status(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)


class SubStatus(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)


class DataSource(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)


class DataChannel(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
