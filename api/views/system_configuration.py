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


class CreateDataSubStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateDataSubStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataSubStatus'],
        operation_id='Create data sub status',
        operation_description='Create data sub status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateDataSubStatusResponseSerializer,
            exceptions.DataSubStatusDuplicated.code: exceptions.DataSubStatusDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateDataSubStatusService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateDataSubStatusResponseSerializer)


class GetDataSubStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetDataSubStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataSubStatus'],
        operation_id='Get data sub status',
        operation_description='Get data sub status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetDataSubStatusResponseSerializer,
            exceptions.DataSubStatusNotFound.code: exceptions.DataSubStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetDataSubStatusService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetDataSubStatusResponseSerializer)


class UpdateDataSubStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateDataSubStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataSubStatus'],
        operation_id='Update data sub status',
        operation_description='Update data sub status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateDataSubStatusResponseSerializer,
            exceptions.DataSubStatusNotFound.code: exceptions.DataSubStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateDataSubStatusService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateDataSubStatusResponseSerializer)


class FilterDataSubStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterDataSubStatusRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['DataSubStatus'],
        operation_id='Filter data sub status',
        operation_description='Filter data sub status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterDataSubStatusResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterDataSubStatusService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterDataSubStatusResponseSerializer)


class DeleteDataSubStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteDataSubStatusRequestSerializer

    @swagger_auto_schema(
        tags=['DataSubStatus'],
        operation_id='Delete data sub status',
        operation_description='Delete data sub status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteDataSubStatusResponseSerializer,
            exceptions.DataSubStatusNotFound.code: exceptions.DataSubStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteDataSubStatusService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteDataSubStatusResponseSerializer)



class CreateDataSourceView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateDataSourceRequestSerializer

    @swagger_auto_schema(
        tags=['DataSource'],
        operation_id='Create data source',
        operation_description='Create data source api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateDataSourceResponseSerializer,
            exceptions.DataSourceDuplicated.code: exceptions.DataSourceDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateDataSourceService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateDataSourceResponseSerializer)


class GetDataSourceView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetDataSourceRequestSerializer

    @swagger_auto_schema(
        tags=['DataSource'],
        operation_id='Get data source',
        operation_description='Get data source api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetDataSourceResponseSerializer,
            exceptions.DataSourceNotFound.code: exceptions.DataSourceNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetDataSourceService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetDataSourceResponseSerializer)


class UpdateDataSourceView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateDataSourceRequestSerializer

    @swagger_auto_schema(
        tags=['DataSource'],
        operation_id='Update data source',
        operation_description='Update data source api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateDataSourceResponseSerializer,
            exceptions.DataSourceNotFound.code: exceptions.DataSourceNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateDataSourceService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateDataSourceResponseSerializer)


class FilterDataSourceView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterDataSourceRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['DataSource'],
        operation_id='Filter data source',
        operation_description='Filter data source api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterDataSourceResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterDataSourceService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterDataSourceResponseSerializer)


class DeleteDataSourceView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteDataSourceRequestSerializer

    @swagger_auto_schema(
        tags=['DataSource'],
        operation_id='Delete data source',
        operation_description='Delete data source api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteDataSourceResponseSerializer,
            exceptions.DataSourceNotFound.code: exceptions.DataSourceNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteDataSourceService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteDataSourceResponseSerializer)


class CreateDataChannelView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateDataChannelRequestSerializer

    @swagger_auto_schema(
        tags=['DataChannel'],
        operation_id='Create data channel',
        operation_description='Create data channel api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateDataChannelResponseSerializer,
            exceptions.DataChannelDuplicated.code: exceptions.DataChannelDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateDataChannelService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateDataChannelResponseSerializer)


class GetDataChannelView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetDataChannelRequestSerializer

    @swagger_auto_schema(
        tags=['DataChannel'],
        operation_id='Get data channel',
        operation_description='Get data channel api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetDataChannelResponseSerializer,
            exceptions.DataChannelNotFound.code: exceptions.DataChannelNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetDataChannelService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetDataChannelResponseSerializer)


class UpdateDataChannelView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateDataChannelRequestSerializer

    @swagger_auto_schema(
        tags=['DataChannel'],
        operation_id='Update data channel',
        operation_description='Update data channel api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateDataChannelResponseSerializer,
            exceptions.DataChannelNotFound.code: exceptions.DataChannelNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateDataChannelService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateDataChannelResponseSerializer)


class FilterDataChannelView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterDataChannelRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['DataChannel'],
        operation_id='Filter data channel',
        operation_description='Filter data channel api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterDataChannelResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterDataChannelService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterDataChannelResponseSerializer)


class DeleteDataChannelView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteDataChannelRequestSerializer

    @swagger_auto_schema(
        tags=['DataChannel'],
        operation_id='Delete data channel',
        operation_description='Delete data channel api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteDataChannelResponseSerializer,
            exceptions.DataChannelNotFound.code: exceptions.DataChannelNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteDataChannelService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteDataChannelResponseSerializer)



class CreateEmailSyntaxView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateEmailSyntaxRequestSerializer

    @swagger_auto_schema(
        tags=['EmailSyntax'],
        operation_id='Create email syntax',
        operation_description='Create email syntax api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateEmailSyntaxResponseSerializer,
            exceptions.EmailSyntaxDuplicated.code: exceptions.EmailSyntaxDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateEmailSyntaxService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateEmailSyntaxResponseSerializer)


class GetEmailSyntaxView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetEmailSyntaxRequestSerializer

    @swagger_auto_schema(
        tags=['EmailSyntax'],
        operation_id='Get email syntax',
        operation_description='Get email syntax api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetEmailSyntaxResponseSerializer,
            exceptions.EmailSyntaxNotFound.code: exceptions.EmailSyntaxNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetEmailSyntaxService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetEmailSyntaxResponseSerializer)


class UpdateEmailSyntaxView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateEmailSyntaxRequestSerializer

    @swagger_auto_schema(
        tags=['EmailSyntax'],
        operation_id='Update email syntax',
        operation_description='Update email syntax api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateEmailSyntaxResponseSerializer,
            exceptions.EmailSyntaxNotFound.code: exceptions.EmailSyntaxNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateEmailSyntaxService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateEmailSyntaxResponseSerializer)


class FilterEmailSyntaxView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterEmailSyntaxRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['EmailSyntax'],
        operation_id='Filter email syntax',
        operation_description='Filter email syntax api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterEmailSyntaxResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterEmailSyntaxService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterEmailSyntaxResponseSerializer)


class DeleteEmailSyntaxView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteEmailSyntaxRequestSerializer

    @swagger_auto_schema(
        tags=['EmailSyntax'],
        operation_id='Delete email syntax',
        operation_description='Delete email syntax api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteEmailSyntaxResponseSerializer,
            exceptions.EmailSyntaxNotFound.code: exceptions.EmailSyntaxNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteEmailSyntaxService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteEmailSyntaxResponseSerializer)



class CreateEmailTemplateView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.CreateEmailTemplateRequestSerializer

    @swagger_auto_schema(
        tags=['EmailTemplate'],
        operation_id='Create email template',
        operation_description='Create email template api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.CreateEmailTemplateResponseSerializer,
            exceptions.EmailTemplateDuplicated.code: exceptions.EmailTemplateDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = system_configuration_service.CreateEmailTemplateService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.CreateEmailTemplateResponseSerializer)


class GetEmailTemplateView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.GetEmailTemplateRequestSerializer

    @swagger_auto_schema(
        tags=['EmailTemplate'],
        operation_id='Get email template',
        operation_description='Get email template api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.GetEmailTemplateResponseSerializer,
            exceptions.EmailTemplateNotFound.code: exceptions.EmailTemplateNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = system_configuration_service.GetEmailTemplateService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.GetEmailTemplateResponseSerializer)


class UpdateEmailTemplateView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.UpdateEmailTemplateRequestSerializer

    @swagger_auto_schema(
        tags=['EmailTemplate'],
        operation_id='Update email template',
        operation_description='Update email template api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.UpdateEmailTemplateResponseSerializer,
            exceptions.EmailTemplateNotFound.code: exceptions.EmailTemplateNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = system_configuration_service.UpdateEmailTemplateService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.UpdateEmailTemplateResponseSerializer)


class FilterEmailTemplateView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationReadPermission]
    serializer_class = system_configuration_serializer.FilterEmailTemplateRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['EmailTemplate'],
        operation_id='Filter email template',
        operation_description='Filter email template api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.FilterEmailTemplateResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = system_configuration_service.FilterEmailTemplateService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=system_configuration_serializer.FilterEmailTemplateResponseSerializer)


class DeleteEmailTemplateView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SystemConfigurationEditPermission]
    serializer_class = system_configuration_serializer.DeleteEmailTemplateRequestSerializer

    @swagger_auto_schema(
        tags=['EmailTemplate'],
        operation_id='Delete email template',
        operation_description='Delete email template api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: system_configuration_serializer.DeleteEmailTemplateResponseSerializer,
            exceptions.EmailTemplateNotFound.code: exceptions.EmailTemplateNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = system_configuration_service.DeleteEmailTemplateService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=system_configuration_serializer.DeleteEmailTemplateResponseSerializer)
