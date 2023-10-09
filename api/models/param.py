from api.models.base import BaseModel
from django.db import models


class Param(BaseModel):
    key = models.CharField(max_length=255, db_index=True, unique=True)
    value = models.CharField(max_length=2048)
    description = models.CharField(max_length=512, unique=False)
    group = models.CharField(max_length=512, unique=False)

    class Meta:
        db_table = 'params'
        unique_together = ('key', 'deleted_at',)
        