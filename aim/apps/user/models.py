from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    mail = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    class Meta:
        db_table = 'user'
