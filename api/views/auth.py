from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import auth_serializer
from api.common.base_view import BaseAPIView
from api.services import exceptions
from api.services.auth import AuthLoginService, AuthLogoutService, AuthGetUserInfoService
from rest_framework.permissions import IsAuthenticated


class AuthLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data.get('access')
            auth_login_service = AuthLoginService()
            auth_login_service.serve(request, None, access_token)

        return response


class AuthLogoutView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = auth_serializer.AuthLogoutRequestSerializer
    
    @swagger_auto_schema(
        tags=['Auth'],
        operation_id='Auth logout',
        operation_description='Auth logout api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: auth_serializer.AuthLogoutResponseSerializer,
            exceptions.AuthLogoutNotLoggedIn.code: exceptions.AuthLogoutNotLoggedIn.msg,
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
        tags=['Auth'],
        operation_id='Auth get user info',
        operation_description='Auth get user info api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: "{'code': 0, 'msg': 'success', 'data': \"{'is_superuser': False, 'roles': [{'company': {'id': 7, 'name': 'Company A'}, 'department': {'id': 1, 'department_name': 'name'}, 'role': None, 'edit_permissions': [], 'read_permissions': []}]}, 'menu': ['USER_MANAGEMENT'], 'call_agent': {'ext': None, 'secret': None, 'sip_server': None}, 'tenant': ''}\"}"
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        auth_get_user_info = AuthGetUserInfoService()
        user_info = auth_get_user_info.serve(request, cookies, *args)
        return self.get_response(results=user_info, request=request)
