from rest_framework import serializers
from api.serializers.base import BaseResponseSerializer


class FBLoginRequestSerializer(serializers.Serializer):
    pass


class FBLoginResponseSerializer(BaseResponseSerializer):
    data = serializers.CharField(allow_blank=True, default='')


class FBLoginCallBackRequestSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


class FBLoginCallBackResponseSerializer(serializers.Serializer):
    pass
