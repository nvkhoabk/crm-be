import json

from api.models.data import Customer
from api.models.call_center import CallCenter
from api.models.organization import Company, Department, Permission, Role, UserRole
from api.models.package import Package
from api.models.param import Param
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.serializers.call_center_serializer import CallCenterSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class ParamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Param
        fields = ['id', 'key', 'value', 'description', 'group']


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

class FilterParamRequestParamSerializer(serializers.Serializer):
    key = serializers.CharField(required=False, allow_blank=True)
    value = serializers.CharField(required=False, allow_blank=True)
    group = serializers.CharField(required=False, allow_blank=True)

class FilterParamRequestSerializer(BasePagingSerializer):
    filter = FilterParamRequestParamSerializer()


class FilterParamResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=ParamSerializer())


class CreatePackageRequestSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(help_text='Company id', default=0)
    viettel = serializers.CharField()
    vinaphone = serializers.CharField()
    mobifone = serializers.CharField()
    other = serializers.CharField()


class PackageSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    def get_company_name(self, package):
        if package.company_id is None or package.company_id == 0:
            return ''

        return package.company.name

    class Meta:
        model = Package
        fields = ['id', 'company_name', 'viettel', 'vinaphone', 'mobifone', 'other']


class CreatePackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class GetPackageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Package id', allow_null=True)


class GetPackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class UpdatePackageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Package id', allow_null=True)
    company_id = serializers.IntegerField(help_text='Company id', allow_null=True, required=False)
    viettel = serializers.CharField(required=False)
    vinaphone = serializers.CharField(required=False)
    mobifone = serializers.CharField(required=False)
    other = serializers.CharField(required=False)


class UpdatePackageResponseSerializer(BaseResponseSerializer):
    data = PackageSerializer()


class FilterPackageRequestParamSerializer(serializers.Serializer):
    company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


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


class CompanySerializer(serializers.ModelSerializer):
    call_center = serializers.SerializerMethodField()
    use_package = serializers.SerializerMethodField()

    def get_call_center(self, company):
        call_center = CallCenter.objects.filter(company_id=company.id)
        if call_center:
            return CallCenterSerializer(call_center.first()).data

        return None

    def get_use_package(self, company):
        if Package.objects.filter(deleted_at__isnull=True, company_id=company.id):
            return True
        return False

    class Meta:
        model = Company
        fields = ['id', 'name', 'type', 'owner', 'phone', 'use_package', 'call_center']


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
        ('DATA_MANAGEMENT_FOR_SALE', 'DATA_MANAGEMENT_FOR_SALE'),
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
        ('MARKETING', 'MARKETING'),
        ('DATA_MANAGEMENT', 'DATA_MANAGEMENT'),
        ('DATA_MANAGEMENT_FOR_SALE', 'DATA_MANAGEMENT_FOR_SALE'),
        ('USER_MANAGEMENT', 'USER_MANAGEMENT'),
        ('PRODUCT_AND_WAREHOUSE', 'PRODUCT_AND_WAREHOUSE'),
        ('ACCOUNTING', 'ACCOUNTING'),
        ('SYSTEM_CONFIGURATION', 'SYSTEM_CONFIGURATION'),
        ('REPORT', 'REPORT'),
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


class UserRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRole
        fields = ('id', 'company', 'department', 'role')
        depth = 1


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField(source='get_company_name', read_only=True)
    status = serializers.BooleanField(source='is_active', read_only=True)
    user_roles = UserRoleSerializer(many=True, required=False)

    def get_company_name(self, user):
        company_id = UserRole.objects.filter(user_id=user.id).first().company_id
        return Company.objects.filter(pk=company_id).first().name

    class Meta:
        model = User
        fields = ('id', 'username', 'company_name', 'status', 'user_roles')


class CreateUserResponseSerializer(BaseResponseSerializer):
    data = UserSerializer()


class GetUserRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetUserResponseSerializer(BaseResponseSerializer):
    pass  # Customized response in service


class FilterUserRequestParamSerializer(serializers.Serializer):
    company_id = serializers.IntegerField(allow_null=True, required=False)
    department_id = serializers.IntegerField(allow_null=True, required=False)
    role_id = serializers.IntegerField(allow_null=True, required=False)
    username = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        permission_field = 'company_id'
        permission_class = 'company'


class FilterUserRequestSerializer(BasePagingSerializer):
    filter = FilterUserRequestParamSerializer()


class FilterUserResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=UserSerializer())


class FilterSaleUserRequestSerializer(BasePagingSerializer):
    None


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


class GetUserRoleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetUserRoleResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=UserRoleSerializer())


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'address', 'email', 'company_id']


class CreateCustomerRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField()
    address = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    company_id = serializers.IntegerField()


class CreateCustomerResponseSerializer(BaseResponseSerializer):
    data = CustomerSerializer()


class GetCustomerRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetCustomerResponseSerializer(BaseResponseSerializer):
    data = CustomerSerializer()


class UpdateCustomerRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)


class UpdateCustomerResponseSerializer(BaseResponseSerializer):
    data = CustomerSerializer()


class FilterCustomerRequestCustomerSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)


class FilterCustomerRequestSerializer(BasePagingSerializer):
    filter = FilterCustomerRequestCustomerSerializer()


class FilterCustomerResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CustomerSerializer())


