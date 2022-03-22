from api.models.base import BaseModel
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role_name = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'roles'


class Category(BaseModel):
    category_name = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = 'categories'


class Permission(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    edit_permissions = models.TextField(max_length=4096)
    read_permissions = models.TextField(max_length=4096)

    class Meta:
        db_table = 'permissions'
        unique_together = ('company', 'department', 'role', )


class UserRole(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_roles'
        