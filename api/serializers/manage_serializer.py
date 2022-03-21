import json

from api.models.organization import Company, Department, Permission, Role
from api.models.package import Package
from api.models.param import Param
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


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
    type = serializers.CharField(min_length=5, allow_blank=True, required=False)
    owner = serializers.CharField(min_length=5, allow_blank=True, required=False)
    phone = serializers.CharField(min_length=5, allow_blank=True, required=False)

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

    class Meta:
        permission_field = 'company_id'
        permission_class= 'company'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'company_id', 'department_name', ]


class CreateDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class UpdateDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    department_name = serializers.CharField(min_length=5)

    class Meta:
        permission_field = 'id'
        permission_class= 'department'


class UpdateDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class FilterDepartmentRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    id = serializers.IntegerField(allow_null=True)
    department_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        permission_field = 'company_id'
        permission_class= 'company'


class FilterDepartmentRequestSerializer(BasePagingSerializer):
    filter = FilterDepartmentRequestParamSerializer()


class FilterDepartmentResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DepartmentSerializer())


class DeleteDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        permission_field = 'id'
        permission_class= 'department'


class DeleteDepartmentResponseSerializer(BaseResponseSerializer):
    pass


class CreateRoleRequestSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    role_name = serializers.CharField(min_length=5)

    class Meta:
        permission_field = 'department_id'
        permission_class= 'department'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'department_id', 'role_name', ]


class CreateRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class UpdateRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    role_name = serializers.CharField(min_length=5)

    class Meta:
        permission_field = 'id'
        permission_class= 'role'


class UpdateRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class FilterRoleRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField()
    id = serializers.IntegerField(allow_null=True)
    role_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        permission_field = 'id'
        permission_class= 'role'


class FilterRoleRequestSerializer(BasePagingSerializer):
    filter = FilterRoleRequestParamSerializer()


class FilterRoleResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=RoleSerializer())


class DeleteRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        permission_field = 'id'
        permission_class= 'role'


class DeleteRoleResponseSerializer(BaseResponseSerializer):
    pass


class CreatePermissionRequestSerializer(serializers.Serializer):
    CATEGORY_CHOICES = (
        ('Marketing', 'Marketing'),
        ('Quản lý data', 'Quản lý data'),
        ('Quản lý nhân sự', 'Quản lý nhân sự'),
        ('Sản phẩm và kho hàng', 'Sản phẩm và kho hàng'),
        ('Tài chính - kế toán', 'Tài chính - kế toán'),
        ('Tuỳ chỉnh hệ thống', 'Tuỳ chỉnh hệ thống'),
        ('Báo cáo', 'Báo cáo'),
    )
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField()
    role_id = serializers.IntegerField()
    edit_permissions = serializers.ListField(child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))
    read_permissions = serializers.ListField(child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))

    class Meta:
        permission_field = 'company_id'
        permission_class= 'company'


class PermissionSerializer(serializers.ModelSerializer):
    edit_permissions = serializers.SerializerMethodField()
    read_permissions = serializers.SerializerMethodField()

    def get_edit_permissions(self, obj):
        return json.loads(obj.edit_permissions)
    
    def get_read_permissions(self, obj):
        return json.loads(obj.read_permissions)

    class Meta:
        model = Permission
        fields = ['id', 'company_id', 'department_id', 'role_id', 'edit_permissions', 'read_permissions']


class CreatePermisionResponseSerializer(BaseResponseSerializer):
    data = PermissionSerializer()


class UpdatePermissionRequestSerializer(serializers.Serializer):
    CATEGORY_CHOICES = (
        ('Marketing', 'Marketing'),
        ('Quản lý data', 'Quản lý data'),
        ('Quản lý nhân sự', 'Quản lý nhân sự'),
        ('Sản phẩm và kho hàng', 'Sản phẩm và kho hàng'),
        ('Tài chính - kế toán', 'Tài chính - kế toán'),
        ('Tuỳ chỉnh hệ thống', 'Tuỳ chỉnh hệ thống'),
        ('Báo cáo', 'Báo cáo'),
    )
    id = serializers.IntegerField()
    edit_permissions = serializers.ListField(child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))
    read_permissions = serializers.ListField(child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))
    
    class Meta:
        permission_field = 'id'
        permission_class= 'permission'
     

class UpdatePermisionResponseSerializer(BaseResponseSerializer):
    data = PermissionSerializer()
    

class FilterPermissionRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField(allow_null=True)
    role_id = serializers.IntegerField(allow_null=True)
    id = serializers.IntegerField(allow_null=True)

    class Meta:
        permission_field = 'company_id'
        permission_class= 'company'


class FilterPermissionRequestSerializer(BasePagingSerializer):
    filter = FilterPermissionRequestParamSerializer()


class FilterPermissionResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PermissionSerializer())


class DeletePermissionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        permission_field = 'id'
        permission_class= 'permission'



class DeletePermissionResponseSerializer(BaseResponseSerializer):
    pass


class CreateUserRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField(required=False)
    role_id = serializers.IntegerField(required=False)
    username = serializers.CharField()
    password = serializers.CharField(min_length=6)
    # phone = serializers.CharField(required=False)

    # def validate_phone(self, value):
    #     value = validate.check_phone_number(value)
    #     if not value:
    #         raise serializers.ValidationError('Phone is not valid')
    #     return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', ) 


class CreateUserResponseSerializer(BaseResponseSerializer):
    data = UserSerializer()


class UpdateUserRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    company_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)
    role_id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, min_length=6)
    status = serializers.BooleanField(required=False, default=True)
    # phone = serializers.CharField(required=False)

    # def validate_phone(self, value):
    #     value = validate.check_phone_number(value)
    #     if not value:
    #         raise serializers.ValidationError('Phone is not valid')
    #     return value


class UpdateUserResponseSerializer(BaseResponseSerializer):
    data = UserSerializer()
