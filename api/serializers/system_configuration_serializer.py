import json

from api.models.system_configuration import CompanyEmail
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanyEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyEmail
        fields = ['email', 'company']


class CreateCompanyEmailRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=1024, required=True)
    password = serializers.CharField(max_length=1024, required=False, allow_null=True)
    company_id = serializers.IntegerField(required=True)


class CreateCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class GetCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class UpdateCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='CompanyEmail id', required=True)
    email = serializers.CharField(max_length=1024, required=False)
    password = serializers.CharField(max_length=1024, required=False, allow_null=False)


class UpdateCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = CompanyEmailSerializer()


class FilterCompanyEmailRequestParamSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=1024, required=False)


class FilterCompanyEmailRequestSerializer(BasePagingSerializer):
    filter = FilterCompanyEmailRequestParamSerializer()


class FilterCompanyEmailResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CompanyEmailSerializer())


class DeleteCompanyEmailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='CompanyEmail id')


class DeleteCompanyEmailResponseSerializer(BaseResponseSerializer):
    pass