from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission, DataReadPermission, DataEditPermission, AccountReadPermission, \
    AccountEditPermission
from api.serializers import report_serializer
from api.services import exceptions
from api.services import report as report_service
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class FilterReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = report_serializer.FilterReportRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Report'],
        operation_id='Filter report',
        operation_description='Filter report',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: report_serializer.FilterReportResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_report_service = report_service.FilterReportService()
        report = filter_report_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=report, request=serializer.validated_data, serializer=report_serializer.FilterReportResponseSerializer)


class FilterAnnualOrderReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = report_serializer.FilterAnnualOrderReportRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Report'],
        operation_id='Filter annual report',
        operation_description='Filter annual report',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: report_serializer.FilterAnnualOrderReportResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_report_service = report_service.FilterAnnualOrderReportService()
        report = filter_report_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=report, request=serializer.validated_data, serializer=report_serializer.FilterAnnualOrderReportResponseSerializer)


class FilterBadDebtReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = report_serializer.FilterBadDebtReportRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Report'],
        operation_id='Filter bad debt report',
        operation_description='Filter bad debt report',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: report_serializer.FilterBadDebtReportResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_report_service = report_service.FilterBadDebtReportService()
        report = filter_report_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=report, request=serializer.validated_data, serializer=report_serializer.FilterBadDebtReportResponseSerializer)


class FilterOrderStatusReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = report_serializer.FilterOrderStatusReportRequestSerializer

    @swagger_auto_schema(
        tags=['Report'],
        operation_id='Filter order status report',
        operation_description='Filter order status report',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: report_serializer.FilterOrderStatusReportRequestSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_report_service = report_service.FilterOrderStatusReportService()
        report = filter_report_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=report, request=serializer.validated_data, serializer=report_serializer.FilterOrderStatusReportResponseSerializer)