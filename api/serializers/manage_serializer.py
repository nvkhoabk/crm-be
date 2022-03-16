from rest_framework import serializers
from api.models.organization import Company
from api.serializers.base import BaseResponseSerializer, BasePagingSerializer


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
    pass


class UpdateCompanyRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(min_length=5)
    type = serializers.CharField(min_length=5)
    owner = serializers.CharField(min_length=5)
    phone = serializers.CharField(min_length=5)


class UpdateCompanyResponseSerializer(BaseResponseSerializer):
    data = CompanySerializer()
 

class FilterCompanyRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
    owner = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True) 


class FilterCompanyRequestSerializer(BasePagingSerializer):
    filter = FilterCompanyRequestParamSerializer()
 
 
class FilterCompanyResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CompanySerializer()) 
