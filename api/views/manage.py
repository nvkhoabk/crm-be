from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission
from api.serializers import manage_serializer
from api.services import exceptions
from api.services import manage as manage_service
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


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
        create_param_service = manage_service.CreateOrUpdateParamService()
        param = create_param_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.CreateParamResponseSerializer)


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
            exceptions.ManageParamDuplicated.code: exceptions.ManageParamDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_param_service = manage_service.CreateOrUpdateParamService()
        param = update_param_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.UpdateParamResponseSerializer)


class FilterParamView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ]
    serializer_class = manage_serializer.FilterParamRequestSerializer

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
        return self.get_response(results=params, request=request, serializer=manage_serializer.FilterParamResponseSerializer)


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
        create_package_service = manage_service.CreateOrUpdatePackageService()
        param = create_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.CreatePackageResponseSerializer)


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
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_package_service = manage_service.CreateOrUpdatePackageService()
        param = update_package_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=param, request=request, serializer=manage_serializer.UpdatePackageResponseSerializer)


class FilterPackageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [SuperAdminPermission, ]
    serializer_class = manage_serializer.FilterPackageRequestSerializer

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
        return self.get_response(results=packages, request=request, serializer=manage_serializer.FilterPackageResponseSerializer)


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
    permission_classes = []
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


class UpdateCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
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
    permission_classes = []
    serializer_class = manage_serializer.FilterCompanyRequestSerializer

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
        return self.get_response(results=companies, request=request,
                                 serializer=manage_serializer.FilterCompanyResponseSerializer,
                                 )


class DeleteCompanyView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
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
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_department_service = manage_service.CreateDepartmentService()
        department = create_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=request, serializer=manage_serializer.CreateDepartmentResponseSerializer)


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
        return self.get_response(results=department, request=request, serializer=manage_serializer.FilterDepartmentResponseSerializer)


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
            exceptions.ManageDepartmentNotFound.code: exceptions.ManageDepartmentNotFound.msg,
            exceptions.ManageRoleDuplicated.code: exceptions.ManageRoleDuplicated.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_role_service = manage_service.CreateRoleService()
        role = create_role_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=role, request=request, serializer=manage_serializer.CreateRoleResponseSerializer)


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
        return self.get_response(results=roles, request=request, serializer=manage_serializer.FilterRoleResponseSerializer)


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
        return self.get_response(results=permissions, request=request, serializer=manage_serializer.FilterPermissionResponseSerializer)


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
