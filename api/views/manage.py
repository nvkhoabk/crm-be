from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission
from api.serializers import manage_serializer
from api.services import exceptions
from api.services import manage as manage_service


class CreateParamView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.CreateParamRequestSerializer

    @swagger_auto_schema(
        tags=['Param'],
        operation_id='Create param',
        operation_description='Create param api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateParamResponseSerializer,
            exceptions.ManageParamDuplicated.code: exceptions.ManageParamDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_param_service = manage_service.CreateParamService()
        param = create_param_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.CreateParamResponseSerializer)


class GetParamView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.GetParamRequestSerializer

    @swagger_auto_schema(
        tags=['Param'],
        operation_id='Get param',
        operation_description='Get param api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetParamResponseSerializer,
            exceptions.ManageParamNotFound.code: exceptions.ManageParamNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_param_service = manage_service.GetParamService()
        param = get_param_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.GetParamResponseSerializer)


class UpdateParamView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission]
    serializer_class = manage_serializer.UpdateParamRequestSerializer

    @swagger_auto_schema(
        tags=['Param'],
        operation_id='Update param',
        operation_description='Update param api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateParamResponseSerializer,
            exceptions.ManageParamNotFound.code: exceptions.ManageParamNotFound.msg,
            exceptions.ManageParamDuplicated.code: exceptions.ManageParamDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_param_service = manage_service.UpdateParamService()
        param = update_param_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.UpdateParamResponseSerializer)


class FilterParamView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ]
    serializer_class = manage_serializer.FilterParamRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Param'],
        operation_id='Filter param',
        operation_description='Filter param api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.FilterParamResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_param_service = manage_service.FilterParamService()
        params = filter_param_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=params, request=serializer.validated_data, serializer=manage_serializer.FilterParamResponseSerializer)

class CreatePackageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.CreatePackageRequestSerializer

    @swagger_auto_schema(
        tags=['Package'],
        operation_id='Create package',
        operation_description='Create package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreatePackageResponseSerializer,
            exceptions.ManagePackageDuplicated.code: exceptions.ManagePackageDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_package_service = manage_service.CreatePackageService()
        param = create_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.CreatePackageResponseSerializer)


class GetPackageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.GetPackageRequestSerializer

    @swagger_auto_schema(
        tags=['Package'],
        operation_id='Get package',
        operation_description='Get package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetPackageResponseSerializer,
            exceptions.ManagePackageNotFound.code: exceptions.ManagePackageNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_package_service = manage_service.GetPackageService()
        param = get_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.GetPackageResponseSerializer)


class UpdatePackageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.UpdatePackageRequestSerializer

    @swagger_auto_schema(
        tags=['Package'],
        operation_id='Update package',
        operation_description='Update package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdatePackageResponseSerializer,
            exceptions.ManagePackageDuplicated.code: exceptions.ManagePackageDuplicated.msg,
            exceptions.ManagePackageNotFound.code: exceptions.ManagePackageNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_package_service = manage_service.UpdatePackageService()
        param = update_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.UpdatePackageResponseSerializer)


class FilterPackageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.FilterPackageRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Package'],
        operation_id='Filter package',
        operation_description='Filter package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterPackageResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_package_service = manage_service.FilterPackageService()
        packages = filter_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=packages, request=serializer.validated_data, serializer=manage_serializer.FilterPackageResponseSerializer)


class DeletePackageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.DeletePackageRequestSerializer

    @swagger_auto_schema(
        tags=['Package'],
        operation_id='Delete package',
        operation_description='Delete package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeletePackageResponseSerializer,
            exceptions.ManagePackageNotFound.code: exceptions.ManagePackageNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_package_service = manage_service.DeletePackageService()
        package = delete_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=package, request=request, serializer=manage_serializer.DeletePackageResponseSerializer)


class CreateCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.CreateCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Create company',
        operation_description='Create company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateCompanyResponseSerializer,
            exceptions.ManageCompanyDuplicated.code: exceptions.ManageCompanyDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_company_service = manage_service.CreateCompanyService()
        company = create_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=company, request=request, serializer=manage_serializer.CreateCompanyResponseSerializer)


class GetCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.GetCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Get company',
        operation_description='Get company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetCompanyResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_company_service = manage_service.GetCompanyService()
        company = get_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=company, request=request, serializer=manage_serializer.GetCompanyResponseSerializer)


class UpdateCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.UpdateCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Update company',
        operation_description='Update company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateCompanyResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.ManageCompanyDuplicated.code: exceptions.ManageCompanyDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_company_service = manage_service.UpdateCompanyService()
        company = update_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=company, request=request, serializer=manage_serializer.UpdateCompanyResponseSerializer)


class FilterCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.FilterCompanyRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Filter company',
        operation_description='Filter company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterCompanyResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_company_service = manage_service.FilterCompanyService()
        companies = filter_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=companies, request=serializer.validated_data,
                                 serializer=manage_serializer.FilterCompanyResponseSerializer,
                                 )


class DeleteCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.DeleteCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Delete company',
        operation_description='Delete company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeleteCompanyRequestSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_company_service = manage_service.DeleteCompanyService()
        delete_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results={}, request=request, serializer=manage_serializer.DeleteCompanyResponseSerializer)


class CreateDepartmentView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.CreateDepartmentRequestSerializer

    @swagger_auto_schema(
        tags=['Department'],
        operation_id='Create department',
        operation_description='Create department api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateDepartmentResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.ManageDepartmentDuplicated.code: exceptions.ManageDepartmentDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_department_service = manage_service.CreateDepartmentService()
        department = create_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=request, serializer=manage_serializer.CreateDepartmentResponseSerializer)


class GetDepartmentView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.GetDepartmentRequestSerializer

    @swagger_auto_schema(
        tags=['Department'],
        operation_id='Get department',
        operation_description='Get department api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetDepartmentResponseSerializer,
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_department_service = manage_service.GetDepartmentService()
        department = get_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=request, serializer=manage_serializer.GetDepartmentResponseSerializer)


class UpdateDepartmentView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.UpdateDepartmentRequestSerializer

    @swagger_auto_schema(
        tags=['Department'],
        operation_id='Update department',
        operation_description='Update department api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateDepartmentResponseSerializer,
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_department_service = manage_service.UpdateDepartmentService()
        department = update_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=request, serializer=manage_serializer.UpdateDepartmentResponseSerializer)


class FilterDepartmentView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.FilterDepartmentRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Department'],
        operation_id='Filter department',
        operation_description='Filter department api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterDepartmentResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_department_service = manage_service.FilterDepartmentService()
        department = filter_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=serializer.validated_data, serializer=manage_serializer.FilterDepartmentResponseSerializer)


class DeleteDepartmentView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.DeleteDepartmentRequestSerializer

    @swagger_auto_schema(
        tags=['Department'],
        operation_id='Delete department',
        operation_description='Delete department api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateDepartmentResponseSerializer,
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_department_service = manage_service.DeleteDepartmentService()
        department = filter_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=request, serializer=manage_serializer.DeleteDepartmentResponseSerializer)


class CreateRoleView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.CreateRoleRequestSerializer

    @swagger_auto_schema(
        tags=['Role'],
        operation_id='Create role',
        operation_description='Create role api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateRoleResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg,
            exceptions.ManageRoleDuplicated.code: exceptions.ManageRoleDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_role_service = manage_service.CreateRoleService()
        role = create_role_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=role, request=request, serializer=manage_serializer.CreateRoleResponseSerializer)


class GetRoleView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.GetRoleRequestSerializer

    @swagger_auto_schema(
        tags=['Role'],
        operation_id='Get role',
        operation_description='Get role api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetRoleResponseSerializer,
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_role_service = manage_service.GetRoleService()
        role = get_role_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=role, request=request, serializer=manage_serializer.GetRoleResponseSerializer)


class UpdateRoleView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.UpdateRoleRequestSerializer

    @swagger_auto_schema(
        tags=['Role'],
        operation_id='Update role',
        operation_description='Update role api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateRoleResponseSerializer,
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_role_service = manage_service.UpdateRoleService()
        role = update_role_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=role, request=request, serializer=manage_serializer.UpdateRoleResponseSerializer)


class FilterRoleView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.FilterRoleRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Role'],
        operation_id='Filter role',
        operation_description='Filter role api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterRoleResponseSerializer, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_role_service = manage_service.FilterRoleService()
        roles = filter_role_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=roles, request=serializer.validated_data, serializer=manage_serializer.FilterRoleResponseSerializer)


class DeleteRoleView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.DeleteRoleRequestSerializer

    @swagger_auto_schema(
        tags=['Role'],
        operation_id='Delete role',
        operation_description='Delete role api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeleteRoleResponseSerializer,
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_role_service = manage_service.DeleteRoleService()
        role = delete_role_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=role, request=request, serializer=manage_serializer.DeleteRoleResponseSerializer)


class CreatePermissionView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.CreatePermissionRequestSerializer

    @swagger_auto_schema(
        tags=['Permission'],
        operation_id='Create permission',
        operation_description='Create permission api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreatePermisionResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg, 
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg, 
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_permission_service = manage_service.CreatePermissionService()
        permission = create_permission_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=permission, request=request, serializer=manage_serializer.CreatePermisionResponseSerializer)


class GetPermissionView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.GetPermissionRequestSerializer

    @swagger_auto_schema(
        tags=['Permission'],
        operation_id='Get permission',
        operation_description='Get permission api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetPermisionResponseSerializer,
            exceptions.ManagePermissionNotFound.code: exceptions.ManagePermissionNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_permission_service = manage_service.GetPermissionService()
        permission = get_permission_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=permission, request=request, serializer=manage_serializer.GetPermisionResponseSerializer)


class UpdatePermissionView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.UpdatePermissionRequestSerializer

    @swagger_auto_schema(
        tags=['Permission'],
        operation_id='Update permission',
        operation_description='Update permission api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdatePermisionResponseSerializer,
            exceptions.ManagePermissionNotFound.code: exceptions.ManagePermissionNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_permission_service = manage_service.UpdatePermissionService()
        permission = update_permission_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=permission, request=request, serializer=manage_serializer.UpdatePermisionResponseSerializer)


class FilterPermissionView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.FilterPermissionRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Permission'],
        operation_id='Filter permission',
        operation_description='Filter permission api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterPermissionResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_permission_service = manage_service.FilterPermissionService()
        permissions = filter_permission_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=permissions, request=serializer.validated_data, serializer=manage_serializer.FilterPermissionResponseSerializer)


class DeletePermissionView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.DeletePermissionRequestSerializer

    @swagger_auto_schema(
        tags=['Permission'],
        operation_id='Delete permission',
        operation_description='Delete permission api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeletePermissionResponseSerializer,
            exceptions.ManagePermissionNotFound.code: exceptions.ManagePermissionNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_permission_service = manage_service.DeletePermissionService()
        permission = delete_permission_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=permission, request=request, serializer=manage_serializer.DeletePermissionResponseSerializer)


class CreateUserView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.CreateUserRequestSerializer

    @swagger_auto_schema(
        tags=['Manage User'],
        operation_id='Create user',
        operation_description='Create user',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateUserResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg, 
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg, 
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_user_service = manage_service.CreateUserService()
        user = create_user_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=user, request=request, serializer=manage_serializer.CreateUserResponseSerializer)


class GetUserView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.GetUserRequestSerializer

    @swagger_auto_schema(
        tags=['Manage User'],
        operation_id='Get user',
        operation_description='Get user',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: "{'code': 0, 'msg': 'success', 'data': \"{'is_superuser': False, 'roles': [{'company': {'id': 7, 'name': 'Company A'}, 'department': {'id': 1, 'department_name': 'name'}, 'role': None, 'edit_permissions': [], 'read_permissions': []}]}\"}",
            exceptions.ManageUserNotFound.code: exceptions.ManageUserNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_user_service = manage_service.GetUserService()
        user = get_user_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=user, request=request)


class FilterUserView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.FilterUserRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage User'],
        operation_id='Filter user',
        operation_description='Filter user',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterUserResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg, 
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg, 
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg, 
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_user_service = manage_service.FilterUserService()
        users = filter_user_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=users, request=serializer.validated_data, serializer=manage_serializer.FilterUserResponseSerializer)


class UpdateUserView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.UpdateUserRequestSerializer

    @swagger_auto_schema(
        tags=['Manage User'],
        operation_id='Update user',
        operation_description='Update user',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateUserResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg, 
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg, 
            exceptions.ManageRoleNotFound.code: exceptions.ManageRoleNotFound.msg, 
            exceptions.ManageUserNotFound.code: exceptions.ManageUserNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_user_service = manage_service.UpdateUserService()
        user = update_user_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=user, request=request, serializer=manage_serializer.UpdateUserResponseSerializer)


class DeleteUserView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.DeleteUserRequestSerializer

    @swagger_auto_schema(
        tags=['Manage User'],
        operation_id='Delete user',
        operation_description='Delete user',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeleteUserResponseSerializer,
            exceptions.ManageUserNotFound.code: exceptions.ManageUserNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_user_service = manage_service.DeleteUserService()
        user = delete_user_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=user, request=request, serializer=manage_serializer.DeleteUserResponseSerializer)


class CreateCustomerView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = manage_serializer.CreateCustomerRequestSerializer

    @swagger_auto_schema(
        tags=['Customer'],
        operation_id='Create Customer',
        operation_description='Create Customer api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateCustomerResponseSerializer,
            exceptions.ManageCustomerDuplicated.code: exceptions.ManageCustomerDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_customer_service = manage_service.CreateCustomerService()
        Customer = create_customer_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=Customer, request=request, serializer=manage_serializer.CreateCustomerResponseSerializer)


class GetCustomerView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.GetCustomerRequestSerializer

    @swagger_auto_schema(
        tags=['Customer'],
        operation_id='Get Customer',
        operation_description='Get Customer api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetCustomerResponseSerializer,
            exceptions.ManageCustomerNotFound.code: exceptions.ManageCustomerNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_Customer_service = manage_service.GetCustomerService()
        Customer = get_Customer_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=Customer, request=request, serializer=manage_serializer.GetCustomerResponseSerializer)


class UpdateCustomerView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission]
    serializer_class = manage_serializer.UpdateCustomerRequestSerializer

    @swagger_auto_schema(
        tags=['Customer'],
        operation_id='Update Customer',
        operation_description='Update Customer api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateCustomerResponseSerializer,
            exceptions.ManageCustomerNotFound.code: exceptions.ManageCustomerNotFound.msg,
            exceptions.ManageCustomerDuplicated.code: exceptions.ManageCustomerDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_Customer_service = manage_service.UpdateCustomerService()
        Customer = update_Customer_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=Customer, request=request, serializer=manage_serializer.UpdateCustomerResponseSerializer)


class FilterCustomerView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ]
    serializer_class = manage_serializer.FilterCustomerRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Customer'],
        operation_id='Filter Customer',
        operation_description='Filter Customer api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.FilterCustomerResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_Customer_service = manage_service.FilterCustomerService()
        Customers = filter_Customer_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=Customers, request=serializer.validated_data, serializer=manage_serializer.FilterCustomerResponseSerializer)


class CreateOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.CreateCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Create company',
        operation_description='Create company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreateCompanyResponseSerializer,
            exceptions.ManageCompanyDuplicated.code: exceptions.ManageCompanyDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_company_service = manage_service.CreateCompanyService()
        company = create_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=company, request=request, serializer=manage_serializer.CreateCompanyResponseSerializer)


class GetOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.GetCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Get company',
        operation_description='Get company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.GetCompanyResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_company_service = manage_service.GetCompanyService()
        company = get_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=company, request=request, serializer=manage_serializer.GetCompanyResponseSerializer)


class UpdateOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.UpdateCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Update company',
        operation_description='Update company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdateCompanyResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.ManageCompanyDuplicated.code: exceptions.ManageCompanyDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_company_service = manage_service.UpdateCompanyService()
        company = update_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=company, request=request, serializer=manage_serializer.UpdateCompanyResponseSerializer)


class FilterOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.FilterCompanyRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Filter company',
        operation_description='Filter company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.FilterCompanyResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_company_service = manage_service.FilterCompanyService()
        companies = filter_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=companies, request=serializer.validated_data,
                                 serializer=manage_serializer.FilterCompanyResponseSerializer,
                                 )


class DeleteOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.DeleteCompanyRequestSerializer

    @swagger_auto_schema(
        tags=['Company'],
        operation_id='Delete company',
        operation_description='Delete company api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeleteCompanyRequestSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_company_service = manage_service.DeleteCompanyService()
        delete_company_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results={}, request=request, serializer=manage_serializer.DeleteCompanyResponseSerializer)