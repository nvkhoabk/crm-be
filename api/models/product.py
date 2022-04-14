from api.models.base import BaseModel
from django.db import models

from api.models.organization import Company


class Product(BaseModel):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    price = models.FloatField()
    payment_method = models.CharField(max_length=128)
    period_fee = models.FloatField()
    date_in_month_payment = models.IntegerField()
    number_of_date_notify = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product'
        unique_together = ('name', 'company')
