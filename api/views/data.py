from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission, CompanyAdminPermission
from api.serializers import data_serializer
from api.services import exceptions
from api.services import data as data_service
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class FilterCrawlDataView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = data_serializer.FilterCrawlDataRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['CrawlData'],
        operation_id='Filter crawl data',
        operation_description='Filter crawl data api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: data_serializer.FilterCrawlDataResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_crawl_data_service = data_service.FilterCrawlDataService()
        data = filter_crawl_data_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=data, request=serializer.validated_data, serializer=data_serializer.FilterCrawlDataResponseSerializer)
