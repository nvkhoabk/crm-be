from api.models.base import BaseModel
from django.db import models


class Package(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    price = models.IntegerField()

    class Meta:
        db_table = 'packages'
        unique_together = ('name', 'deleted_at',)
