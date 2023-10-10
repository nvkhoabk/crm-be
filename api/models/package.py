from api.models.base import BaseModel
from django.db import models
from api.models.organization import Company


class Package(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    viettel = models.CharField(max_length=2048, default='')
    vinaphone = models.CharField(max_length=2048, default='')
    mobifone = models.CharField(max_length=2048, default='')
    other = models.CharField(max_length=2048, default='')

    class Meta:
        db_table = 'packages'
        unique_together = ('company', 'deleted_at',)
