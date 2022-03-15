from rest_framework import serializers
from api.models.organization import Company
from api.serializers.base import BaseResponseSerializer


class CreateCompanyRequestSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=5)
    type = serializers.CharField(min_length=5)
    owner = serializers.CharField(min_length=5)
    phone = serializers.CharField(min_length=5)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'type', 'owner', 'phone']


class CreateCompanyResponseSerializer(BaseResponseSerializer):
    data = CompanySerializer() 


class DeleteCompanyRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteCompanyResponseSerializer(BaseResponseSerializer):
    data = CompanySerializer()
