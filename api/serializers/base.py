from rest_framework import serializers


class BaseResponseSerializer(serializers.Serializer):        
    code = serializers.IntegerField(default=0)
    msg = serializers.CharField(allow_blank=True, default='success')
