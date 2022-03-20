from rest_framework import serializers
from api.serializers.base import BaseResponseSerializer


class AuthLoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class AuthLoginResponseSerializer(BaseResponseSerializer):
    data = serializers.CharField(allow_blank=True, default='')


class AuthLogoutRequestSerializer(serializers.Serializer):
    pass


class AuthLogoutResponseSerializer(BaseResponseSerializer):
    data = serializers.CharField(allow_blank=True, default='')
