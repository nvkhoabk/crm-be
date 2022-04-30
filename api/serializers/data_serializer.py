import json
from api.models.data import CrawlData
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.utils import validate
from rest_framework import serializers


class CrawlDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlData
        fields = ['id', 'source', 'ref_link', 'uid', 'username', 'phone', 'content', 'status', ]


class FilterCrawlDataParamRequestSerializer(BasePagingSerializer):
    SOURCE_CHOICES = (
        ('fb', 'fb'),
        ('zalo', 'zalo'),
    )
    STATUS_CHOICES = (
        ('init', 'init'),
    )
    
    source = serializers.ChoiceField(choices=SOURCE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    phone = serializers.CharField(required=False) 


class FilterCrawlDataRequestSerializer(BasePagingSerializer):
    filter = FilterCrawlDataParamRequestSerializer()


class FilterCrawlDataResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CrawlDataSerializer())
