from django.db import models
from aim.apps.address.models import City, District

# Create your models here.
class AssetType(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'asset_type'


class AssetStatus(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'asset_status'


class Asset(models.Model):
    name = models.CharField(max_length=255)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    asset_status = models.ForeignKey(AssetStatus, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    address = models.TextField(null=True)
    description = models.TextField(null=True)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)
    district = models.ForeignKey(District, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(null=False)
    updated_at = models.DateTimeField(auto_now=True)
    update_by = models.IntegerField(null=False)

    class Meta:
        db_table = 'asset'
