from api.common.base_view import BaseAPIView
from api.serializers import system_configuration_serializer
from api.services import exceptions
from api.services import system_configuration as system_configuration_service
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import SystemConfigurationReadPermission, SystemConfigurationEditPermission


class CreateCompanyEmailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateCompanyEmailRequestSerializer

    @swagger_auto_schema(
        tags=['CompanyEmail'],
        operation_id='Create company email',
        operation_description='Create company email api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateCompanyEmailResponseSerializer,
            exceptions.CompanyEmailDuplicated.code: exceptions.CompanyEmailDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateCompanyEmailService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateCompanyEmailResponseSerializer)


class GetCompanyEmailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetCompanyEmailRequestSerializer

    @swagger_auto_schema(
        tags=['CompanyEmail'],
        operation_id='Get company email',
        operation_description='Get company email api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetCompanyEmailResponseSerializer,
            exceptions.CompanyEmailNotFound.code: exceptions.CompanyEmailNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetCompanyEmailService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetCompanyEmailResponseSerializer)


class UpdateCompanyEmailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateCompanyEmailRequestSerializer

    @swagger_auto_schema(
        tags=['CompanyEmail'],
        operation_id='Update company email',
        operation_description='Update company email api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateCompanyEmailResponseSerializer,
            exceptions.CompanyEmailNotFound.code: exceptions.CompanyEmailNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateCompanyEmailService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateCompanyEmailResponseSerializer)


class FilterCompanyEmailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterCompanyEmailRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['CompanyEmail'],
        operation_id='Filter company email',
        operation_description='Filter company email api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterCompanyEmailResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterCompanyEmailService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterCompanyEmailResponseSerializer)


class DeleteCompanyEmailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteCompanyEmailRequestSerializer

    @swagger_auto_schema(
        tags=['CompanyEmail'],
        operation_id='Delete company email',
        operation_description='Delete company email api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteCompanyEmailResponseSerializer,
            exceptions.CompanyEmailNotFound.code: exceptions.CompanyEmailNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteCompanyEmailService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteCompanyEmailResponseSerializer)


class CreateDataStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateDataStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataStatus'],
        operation_id='Create data status',
        operation_description='Create data status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateDataStatusResponseSerializer,
            exceptions.DataStatusDuplicated.code: exceptions.DataStatusDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateDataStatusService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateDataStatusResponseSerializer)


class GetDataStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetDataStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataStatus'],
        operation_id='Get data status',
        operation_description='Get data status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetDataStatusResponseSerializer,
            exceptions.DataStatusNotFound.code: exceptions.DataStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetDataStatusService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetDataStatusResponseSerializer)


class UpdateDataStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateDataStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataStatus'],
        operation_id='Update data status',
        operation_description='Update data status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateDataStatusResponseSerializer,
            exceptions.DataStatusNotFound.code: exceptions.DataStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateDataStatusService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateDataStatusResponseSerializer)


class FilterDataStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterDataStatusRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['DataStatus'],
        operation_id='Filter data status',
        operation_description='Filter data status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterDataStatusResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterDataStatusService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterDataStatusResponseSerializer)


class DeleteDataStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteDataStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataStatus'],
        operation_id='Delete data status',
        operation_description='Delete data status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteDataStatusResponseSerializer,
            exceptions.DataStatusNotFound.code: exceptions.DataStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteDataStatusService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteDataStatusResponseSerializer)