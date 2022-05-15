from rest_framework import serializers
from api.serializers.base import BaseResponseSerializer


class ZaloLoginRequestSerializer(serializers.Serializer):
    pass


class ZaloLoginResponseSerializer(BaseResponseSerializer):
    data = serializers.CharField(allow_blank=True, default='')


class ZaloLoginCallBackRequestSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


class ZaloLoginCallBackResponseSerializer(serializers.Serializer):
    pass
