from api.models.organization import Company
from api.models.package import Package
from api.models.param import Param
from api.models.organization import Department, Role
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.utils import validate
from rest_framework import serializers


class CreateParamRequestSerializer(serializers.Serializer):
    KEY_CHOICES = (
        ('INTRODUCTION', 'INTRODUCTION'),
    )

    key = serializers.ChoiceField(choices=KEY_CHOICES, default='INTRODUCTION')
    value = serializers.CharField(min_length=5)


class CreateParamResponseSerializer(BaseResponseSerializer):
    pass


class UpdateParamRequestSerializer(serializers.Serializer):
    KEY_CHOICES = (
        ('INTRODUCTION', 'INTRODUCTION'),
    )

    key = serializers.ChoiceField(choices=KEY_CHOICES, default='INTRODUCTION')
    value = serializers.CharField(min_length=5)


class UpdateParamResponseSerializer(BaseResponseSerializer):
    pass


class FilterParamRequestSerializer(serializers.Serializer):
    pass


class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = ['id', 'key', 'value']


class FilterParamResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ParamSerializer())


class CreatePackageRequestSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=5)
    price = serializers.IntegerField(min_value=1)


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'price']


class CreatePackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class UpdatePackageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(min_length=5)
    price = serializers.IntegerField(min_value=1)


class UpdatePackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class FilterPackageRequestParamSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)


class FilterPackageRequestSerializer(BasePagingSerializer):
    filter = FilterPackageRequestParamSerializer()


class FilterPackageResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PackageSerializer())


class DeletePackageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeletePackageResponseSerializer(BaseResponseSerializer):
    pass


class CreateCompanyRequestSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=5)
    type = serializers.CharField(min_length=5)
    owner = serializers.CharField(min_length=5)
    phone = serializers.CharField(min_length=5)

    def validate_phone(self, value):
        value = validate.check_phone_number(value)
        if not value:
            raise serializers.ValidationError('Phone is not valid')
        return value


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


class CreateDepartmentRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_name = serializers.CharField(min_length=5)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'company_id', 'department_name', ]


class CreateDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class UpdateDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    department_name = serializers.CharField(min_length=5)


class UpdateDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class FilterDepartmentRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(allow_null=True)
    id = serializers.IntegerField(allow_null=True)
    department_name = serializers.CharField(required=False, allow_blank=True)


class FilterDepartmentRequestSerializer(BasePagingSerializer):
    filter = FilterDepartmentRequestParamSerializer()


class FilterDepartmentResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DepartmentSerializer())


class DeleteDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteDepartmentResponseSerializer(BaseResponseSerializer):
    pass


class CreateRoleRequestSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    role_name = serializers.CharField(min_length=5)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'department_id', 'role_name', ]


class CreateRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class UpdateRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    role_name = serializers.CharField(min_length=5)


class UpdateRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class FilterRoleRequestParamSerializer(serializers.Serializer):
    department_id = serializers.IntegerField(allow_null=True)
    id = serializers.IntegerField(allow_null=True)
    role_name = serializers.CharField(required=False, allow_blank=True)


class FilterRoleRequestSerializer(BasePagingSerializer):
    filter = FilterRoleRequestParamSerializer()


class FilterRoleResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=RoleSerializer())


class DeleteRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteRoleResponseSerializer(BaseResponseSerializer):
    pass
