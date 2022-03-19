from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission
from api.serializers import manage_serializer
from api.services.exceptions import ManageCreatePackageDuplicated, ManageDeletePackageNotFound
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
        operation_id='Create param',
        operation_description='Create param api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.CreateParamResponseSerializer,
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
        operation_id='Update param',
        operation_description='Update param api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.UpdateParamResponseSerializer,
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
        operation_id='Create package',
        operation_description='Create package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.CreatePackageResponseSerializer,
            ManageCreatePackageDuplicated.code: ManageCreatePackageDuplicated.msg,
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
        operation_id='Update package',
        operation_description='Update package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.UpdatePackageResponseSerializer,
            ManageCreatePackageDuplicated.code: ManageCreatePackageDuplicated.msg,
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
    serializer_class = manage_serializer.FilterPackageRequestParamSerializer

    @swagger_auto_schema(
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
        operation_id='Delete package',
        operation_description='Delete package api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: manage_serializer.DeletePackageResponseSerializer,
            ManageDeletePackageNotFound.code: ManageDeletePackageNotFound.msg,
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
        operation_id='Create company',
        operation_description='Create company api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.CreateCompanyResponseSerializer,
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
        operation_id='Update company',
        operation_description='Update company api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.UpdateCompanyResponseSerializer,
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
        operation_id='Filter company',
        operation_description='Filter company api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.FilterCompanyResponseSerializer,
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
        operation_id='Delete company',
        operation_description='Delete company api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.DeleteCompanyRequestSerializer(),
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
        operation_id='Create department',
        operation_description='Create department api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.CreateDepartmentResponseSerializer,
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
        operation_id='Update department',
        operation_description='Update department api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.UpdateDepartmentResponseSerializer,
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
        operation_id='Filter department',
        operation_description='Filter department api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.FilterDepartmentResponseSerializer,
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
        operation_id='Delete department',
        operation_description='Delete department api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: manage_serializer.DeleteDepartmentResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_department_service = manage_service.DeleteDepartmentService()
        department = filter_department_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=department, request=request, serializer=manage_serializer.DeleteDepartmentResponseSerializer)

