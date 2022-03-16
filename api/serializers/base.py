from rest_framework import serializers


class BaseResponseSerializer(serializers.Serializer):        
    code = serializers.IntegerField(default=0)
    msg = serializers.CharField(allow_blank=True, default='success')


class BasePagingSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=0)
    page_size = serializers.IntegerField(default=10)
