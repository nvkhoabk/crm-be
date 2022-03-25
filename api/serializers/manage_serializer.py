import json

from api.models.organization import Company, Department, Permission, Role, UserRole
from api.models.package import Package
from api.models.param import Param
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = ['id', 'key', 'value']


class CreateParamRequestSerializer(serializers.Serializer):
    KEY_CHOICES = (
        ('INTRODUCTION', 'INTRODUCTION'),
    )

    key = serializers.ChoiceField(choices=KEY_CHOICES, default='INTRODUCTION')
    value = serializers.CharField()


class CreateParamResponseSerializer(BaseResponseSerializer):
   data = ParamSerializer() 


class GetParamRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetParamResponseSerializer(BaseResponseSerializer):
    data = ParamSerializer() 
 
class UpdateParamRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class UpdateParamResponseSerializer(BaseResponseSerializer):
    data = ParamSerializer() 


class FilterParamRequestSerializer(BasePagingSerializer):
    pass


class FilterParamResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ParamSerializer())


class CreatePackageRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField(min_value=1)


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ['id', 'name', 'price']


class CreatePackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class GetPackageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Package id')


class GetPackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class UpdatePackageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Package id')
    name = serializers.CharField()
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
    id = serializers.IntegerField(help_text='Package id')


class DeletePackageResponseSerializer(BaseResponseSerializer):
    pass


class CreateCompanyRequestSerializer(serializers.Serializer):
    name = serializers.CharField(help_text='Company name')
    type = serializers.CharField(
        allow_blank=True, required=False, help_text='Company type')
    owner = serializers.CharField(
        allow_blank=True, required=False, help_text='Owner name')
    phone = serializers.CharField(
        allow_blank=True, required=False, help_text='Company phone')

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


class GetCompanyRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Company id')


class GetCompanyResponseSerializer(BaseResponseSerializer):
    data = CompanySerializer()


class DeleteCompanyRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Company id')


class DeleteCompanyResponseSerializer(BaseResponseSerializer):
    pass


class UpdateCompanyRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Company id')
    name = serializers.CharField(required=False)
    type = serializers.CharField(required=False)
    owner = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)


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
    department_name = serializers.CharField()

    class Meta:
        permission_field = 'company_id'
        permission_class = 'company'


class DepartmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    class Meta:
        model = Department
        fields = ['id', 'company_id', 'company_name', 'department_name', ]


class CreateDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class GetDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class UpdateDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Department id')
    department_name = serializers.CharField()

    class Meta:
        permission_field = 'id'
        permission_class = 'department'


class UpdateDepartmentResponseSerializer(BaseResponseSerializer):
    data = DepartmentSerializer()


class FilterDepartmentRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField(required=False)
    department_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        permission_field = 'company_id'
        permission_class = 'company'


class FilterDepartmentRequestSerializer(BasePagingSerializer):
    filter = FilterDepartmentRequestParamSerializer()


class FilterDepartmentResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=DepartmentSerializer())


class DeleteDepartmentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Department id')

    class Meta:
        permission_field = 'id'
        permission_class = 'department'


class DeleteDepartmentResponseSerializer(BaseResponseSerializer):
    pass


class CreateRoleRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField()
    role_name = serializers.CharField()

    class Meta:
        permission_field = 'department_id'
        permission_class = 'department'


class RoleSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    class Meta:
        model = Role
        fields = ['id', 'company_id', 'company_name', 'department_id', 'department_name', 'role_name', ]


class CreateRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class GetRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class UpdateRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Role id')
    role_name = serializers.CharField()

    class Meta:
        permission_field = 'id'
        permission_class = 'role'


class UpdateRoleResponseSerializer(BaseResponseSerializer):
    data = RoleSerializer()


class FilterRoleRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField(allow_null=True)
    role_id = serializers.IntegerField(allow_null=True)
    role_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        permission_field = 'id'
        permission_class = 'role'


class FilterRoleRequestSerializer(BasePagingSerializer):
    filter = FilterRoleRequestParamSerializer()


class FilterRoleResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=RoleSerializer())


class DeleteRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    class Meta:
        permission_field = 'id'
        permission_class = 'role'


class DeleteRoleResponseSerializer(BaseResponseSerializer):
    pass


class CreatePermissionRequestSerializer(serializers.Serializer):
    CATEGORY_CHOICES = (
        ('MARKETING', 'MARKETING'),
        ('DATA_MANAGEMENT', 'DATA_MANAGEMENT'),
        ('USER_MANAGEMENT', 'USER_MANAGEMENT'),
        ('PRODUCT_AND_WAREHOUSE', 'PRODUCT_AND_WAREHOUSE'),
        ('ACCOUNTING', 'ACCOUNTING'),
        ('SYSTEM_CONFIGURATION', 'SYSTEM_CONFIGURATION'),
        ('REPORT', 'REPORT'),
    )
    company_id = serializers.IntegerField()
    department_id = serializers.IntegerField()
    role_id = serializers.IntegerField()
    edit_permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))
    read_permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))

    class Meta:
        permission_field = 'company_id'
        permission_class = 'company'


class PermissionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    edit_permissions = serializers.SerializerMethodField()
    read_permissions = serializers.SerializerMethodField()

    def get_edit_permissions(self, obj):
        return json.loads(obj.edit_permissions)

    def get_read_permissions(self, obj):
        return json.loads(obj.read_permissions)

    class Meta:
        model = Permission
        fields = ['id', 'company_id', 'company_name', 'department_id', 'department_name',
                  'role_id', 'role_name', 'edit_permissions', 'read_permissions']


class CreatePermisionResponseSerializer(BaseResponseSerializer):
    data = PermissionSerializer()


class GetPermissionRequestSerializer(serializers.Serializer): 
    id = serializers.IntegerField()


class GetPermisionResponseSerializer(BaseResponseSerializer):
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
    edit_permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))
    read_permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=CATEGORY_CHOICES, allow_blank=True))

    class Meta:
        permission_field = 'id'
        permission_class = 'permission'


class UpdatePermisionResponseSerializer(BaseResponseSerializer):
    data = PermissionSerializer()


class FilterPermissionRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    role_id = serializers.IntegerField(required=False, allow_null=True)
    permission_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        permission_field = 'company_id'
        permission_class = 'company'


class FilterPermissionRequestSerializer(BasePagingSerializer):
    filter = FilterPermissionRequestParamSerializer()


class FilterPermissionResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PermissionSerializer())


class DeletePermissionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Permission id')

    class Meta:
        permission_field = 'id'
        permission_class = 'permission'


class DeletePermissionResponseSerializer(BaseResponseSerializer):
    pass


class UserPositionSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    role_id = serializers.IntegerField()


class CreateUserRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    roles = serializers.ListField(child=UserPositionSerializer(), required=False)    
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', )


class CreateUserResponseSerializer(BaseResponseSerializer):
    data = UserSerializer()


class GetUserRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetUserResponseSerializer(BaseResponseSerializer):
    pass


class FilterUserRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(required=False)
    department_id = serializers.IntegerField(required=False)
    role_id = serializers.IntegerField(required=False)
    username = serializers.CharField(allow_null=True, required=False)

    class Meta:
        permission_field = 'company_id'
        permission_class = 'company'


class FilterUserRequestSerializer(BasePagingSerializer):
    filter = FilterUserRequestParamSerializer()


class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserRole
        fields = '__all__'
        depth = 1


class FilterUserResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=UserSerializer())


class UpdateUserRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='User id')
    company_id = serializers.IntegerField(required=True)
    roles = serializers.ListField(child=UserPositionSerializer(), required=False)  
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    status = serializers.BooleanField(required=False, default=True)
    # phone = serializers.CharField(required=False)

    # def validate_phone(self, value):
    #     value = validate.check_phone_number(value)
    #     if not value:
    #         raise serializers.ValidationError('Phone is not valid')
    #     return value


class UpdateUserResponseSerializer(BaseResponseSerializer):
    data = UserSerializer()


class DeleteUserRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='User id')

    class Meta:
        permission_field = 'id'
        permission_class = 'permission'


class DeleteUserResponseSerializer(BaseResponseSerializer):
    pass
