import json

from api.const import ORDER_DETAIL_TYPE, DEBT_STATUS, ORDER_PAYMENT_STATUS, PAYMENT_METHOD
from api.models.data import CrawlData, Order, OrderDetail, Customer, FBPage, FBUser, Payment
from api.models.system_configuration import DataChannel
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.serializers.data_serializer import FilterOrderRequestParamSerializer
from api.serializers.manage_serializer import CustomerSerializer
from api.serializers.product_serializer import ProductSerializer
from api.serializers.system_configuration_serializer import DataStatusSerializer, DataSubStatusSerializer, \
    DataSourceSerializer, DataChannelSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ReportSerializer(serializers.Serializer):
    pic = serializers.CharField()
    total_order = serializers.IntegerField()
    total_confirmed_order = serializers.IntegerField()
    conversion_rate = serializers.FloatField()
    turnover = serializers.FloatField()
    debt = serializers.FloatField()
    waiting_approved_debt = serializers.FloatField()
    average_confirmed_time = serializers.IntegerField()
    top = serializers.IntegerField


class FilterReportParamRequestSerializer(serializers.Serializer):
    ORDER_BY_CHOICES = (
        ('desc', 'desc'),
        ('asc', 'asc'),
    )
    order = FilterOrderRequestParamSerializer(required=False)
    order_by = serializers.ChoiceField(choices=ORDER_BY_CHOICES, default='asc')


class FilterReportRequestSerializer(BasePagingSerializer):
    filter = FilterReportParamRequestSerializer()


class FilterReportResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ReportSerializer())


class AnnualOrderReportSerializer(serializers.Serializer):
    pic = serializers.CharField()
    total_order = serializers.IntegerField()
    total_debt = serializers.FloatField()
    paid_amount = serializers.FloatField()
    remaining_debt = serializers.FloatField()
    waiting_approved_remaining_debt = serializers.FloatField()
    top = serializers.IntegerField


class FilterAnnualOrderReportParamRequestSerializer(serializers.Serializer):
    ORDER_BY_CHOICES = (
        ('desc', 'desc'),
        ('asc', 'asc'),
    )
    order = FilterOrderRequestParamSerializer(required=False)
    order_by = serializers.ChoiceField(choices=ORDER_BY_CHOICES, default='asc')


class FilterAnnualOrderReportRequestSerializer(BasePagingSerializer):
    filter = FilterAnnualOrderReportParamRequestSerializer()


class FilterAnnualOrderReportResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=AnnualOrderReportSerializer())


class BadDebtReportSerializer(serializers.Serializer):
    pic = serializers.CharField()
    total_order = serializers.IntegerField()
    total_debt = serializers.FloatField()
    paid_amount = serializers.FloatField()
    remaining_debt = serializers.FloatField()
    waiting_approved_remaining_debt = serializers.FloatField()
    top = serializers.IntegerField


class FilterBadDebtReportParamRequestSerializer(serializers.Serializer):
    ORDER_BY_CHOICES = (
        ('desc', 'desc'),
        ('asc', 'asc'),
    )
    months = serializers.IntegerField()
    order_by = serializers.ChoiceField(choices=ORDER_BY_CHOICES, default='asc')


class FilterBadDebtReportRequestSerializer(BasePagingSerializer):
    filter = FilterBadDebtReportParamRequestSerializer()


class FilterBadDebtReportResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=BadDebtReportSerializer())

