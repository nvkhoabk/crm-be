from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission, CompanyAdminPermission
from api.serializers import fb_serializer
from api.services import exceptions
from api.services import fb as fb_service
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class FBLoginView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = None

    @swagger_auto_schema(
        tags=['Facebook'],
        operation_id='Facebook login',
        operation_description='Facebook login api',
        responses={
            status.HTTP_201_CREATED: None,
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        fb_login_service = fb_service.FBLoginService()
        return fb_login_service.serve(request, cookies)


class FBLoginCallBackView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = fb_serializer.FBLoginCallBackRequestSerializer

    @swagger_auto_schema(
        tags=['Facebook'],
        operation_id='Facebook login callback',
        operation_description='Facebook login callback api',
        responses={
            status.HTTP_201_CREATED: None,
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        fb_login_call_back_service = fb_service.FBLoginCallBackService()
        result = fb_login_call_back_service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=result, request=request, serializer=fb_serializer.FBLoginCallBackResponseSerializer)
