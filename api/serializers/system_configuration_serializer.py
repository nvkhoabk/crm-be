import json

from api.models.system_configuration import CompanyEmail, DataStatus
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
    password = serializers.CharField(max_length=1024, required=False, allow_null=True)


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


class DataStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataStatus
        fields = ['name', 'company']


class CreateDataStatusRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=True)
    company_id = serializers.IntegerField(required=True)


class CreateDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class GetDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class UpdateDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataStatus id', required=True)
    name = serializers.CharField(max_length=1024, required=False)


class UpdateDataStatusResponseSerializer(BaseResponseSerializer):
    data = DataStatusSerializer()


class FilterDataStatusRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=1024, required=False)


class FilterDataStatusRequestSerializer(BasePagingSerializer):
    filter = FilterDataStatusRequestParamSerializer()


class FilterDataStatusResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DataStatusSerializer())


class DeleteDataStatusRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='DataStatus id')


class DeleteDataStatusResponseSerializer(BaseResponseSerializer):
    pass