from rest_framework import serializers


class BaseResponseSerializer(serializers.Serializer):        
    code = serializers.IntegerField(default=0)
    msg = serializers.CharField(allow_blank=True, default='success')


class BaseResponsePagingSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total = serializers.IntegerField()

class BasePagingSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=0)
    page_size = serializers.IntegerField(default=10)
    sum_field = serializers.CharField(max_length=256, default=None)
    order_by = serializers.CharField(max_length=128, default='-id')
