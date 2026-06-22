import json

from api.const import PRODUCT_PAYMENT_METHOD, PRODUCT_DELETE_TYPE
from api.models.product import Product
from api.models.package import Package
from api.models.param import Param
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'payment_method', 'period_fee', 'date_in_month_payment',
                  'number_of_date_notify', 'company', 'deleted_at']


class CreateProductRequestSerializer(serializers.Serializer):
    PAYMENT_METHOD_CHOICES = (
        (PRODUCT_PAYMENT_METHOD.CREDIT, PRODUCT_PAYMENT_METHOD.CREDIT),
        (PRODUCT_PAYMENT_METHOD.DEBIT, PRODUCT_PAYMENT_METHOD.DEBIT)
    )

    name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.FloatField(required=True)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, default='DEBIT')
    period_fee = serializers.FloatField(required=False)
    date_in_month_payment = serializers.IntegerField(required=False)
    number_of_date_notify = serializers.IntegerField(required=False)
    company_id = serializers.IntegerField(required=True)


class CreateProductResponseSerializer(BaseResponseSerializer):
    data = ProductSerializer()


class GetProductRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetProductResponseSerializer(BaseResponseSerializer):
    data = ProductSerializer()


class UpdateProductRequestSerializer(serializers.Serializer):
    PAYMENT_METHOD_CHOICES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT')
    )
    id = serializers.IntegerField(help_text='Product id', required=True)
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.FloatField(required=False)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=False)
    period_fee = serializers.FloatField(required=False)
    date_in_month_payment = serializers.IntegerField(required=False)
    number_of_date_notify = serializers.IntegerField(required=False)
    company_id = serializers.IntegerField(required=False)


class UpdateProductResponseSerializer(BaseResponseSerializer):
    data = ProductSerializer()


class FilterProductRequestParamSerializer(serializers.Serializer):
    PAYMENT_METHOD_CHOICES = (
        ('CREDIT', 'CREDIT'),
        ('DEBIT', 'DEBIT')
    )
    PRODUCT_DELETE_TYPE_CHOICES = (
        (PRODUCT_DELETE_TYPE.ALL, PRODUCT_DELETE_TYPE.ALL),
        (PRODUCT_DELETE_TYPE.DELETED, PRODUCT_DELETE_TYPE.DELETED),
        (PRODUCT_DELETE_TYPE.ACTIVE, PRODUCT_DELETE_TYPE.ACTIVE)
    )
    name = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=False, allow_null=True)
    product_delete_type = serializers.ChoiceField(choices=PRODUCT_DELETE_TYPE_CHOICES,
                                                  default=PRODUCT_DELETE_TYPE.ACTIVE)


class FilterProductRequestSerializer(BasePagingSerializer):
    filter = FilterProductRequestParamSerializer()


class FilterProductResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ProductSerializer())


class DeleteProductRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Product id')


class DeleteProductResponseSerializer(BaseResponseSerializer):
    pass