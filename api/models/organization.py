from api.models.base import BaseModel
from django.db import models


class Company(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    type = models.CharField(max_length=255, db_index=True, unique=True)
    owner = models.CharField(max_length=255, db_index=True, unique=True)
    phone = models.CharField(max_length=255, db_index=True, unique=True)
    class Meta:
        unique_together = ('name', 'deleted_at',)
        

class Department(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)

    class Meta:
        unique_together = ('name', 'deleted_at',)
