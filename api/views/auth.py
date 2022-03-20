from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from api.serializers import auth_serializer
from api.common.base_view import BaseAPIView
from api.services.auth import AuthLoginService, AuthLogoutService, AuthGetUserInfoService
from rest_framework.permissions import IsAuthenticated


class AuthLoginView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = auth_serializer.AuthLoginRequestSerializer
    
    @swagger_auto_schema(
        operation_id='Auth login',
        operation_description='Auth login api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: auth_serializer.AuthLoginResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        auth_login_service = AuthLoginService()
        user = auth_login_service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=user, request=request, serializer=auth_serializer.AuthLoginResponseSerializer)


class AuthLogoutView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = auth_serializer.AuthLogoutRequestSerializer
    
    @swagger_auto_schema(
        operation_id='Auth logout',
        operation_description='Auth logout api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: auth_serializer.AuthLogoutResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        auth_logout_service = AuthLogoutService()
        auth_logout_service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(request=request, results={}, serializer=auth_serializer.AuthLogoutResponseSerializer)


class AuthGetUserInfoView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ]
    serializer_class = None 
    
    @swagger_auto_schema(
        operation_id='Auth get user info',
        operation_description='Auth get user info api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: auth_serializer.AuthLoginResponseSerializer,
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        auth_get_user_info = AuthGetUserInfoService()
        user_info = auth_get_user_info.serve(request, cookies, *args)
        return self.get_response(results=user_info, request=request, serializer=auth_serializer.AuthLoginResponseSerializer)
