from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from api.serializers import manage_serializer 
from api.common.base_view import BaseAPIView
from api.services.manage import CreateCompanyService, DeleteCompanyService, UpdateCompanyService, FilterCompanyService


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
        create_company_service = CreateCompanyService()
        company = create_company_service.serve(request, cookies, *args, **serializer.validated_data)
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
        update_company_service = UpdateCompanyService()
        company = update_company_service.serve(request, cookies, *args, **serializer.validated_data)
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
        filter_company_service = FilterCompanyService()
        companies = filter_company_service.serve(request, cookies, *args, **serializer.validated_data)
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
        delete_company_service = DeleteCompanyService()
        delete_company_service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(results={}, request=request, serializer=manage_serializer.DeleteCompanyResponseSerializer)
