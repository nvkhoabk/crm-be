from api.models.base import BaseModel
from django.db import models


class Company(BaseModel):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    type = models.CharField(max_length=255, db_index=True, unique=True)
    owner = models.CharField(max_length=255, db_index=True, unique=True)
    phone = models.CharField(max_length=255, db_index=True, unique=True)
    class Meta:
        db_table = 'companies'
        unique_together = ('name', 'deleted_at',)
        

class Department(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'departments'


class Role(BaseModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'roles'
