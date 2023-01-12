import json

from api.models.notification import Notification
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'content', 'unread', 'created_at', 'user', 'company']


class FilterNotificationRequestParamSerializer(serializers.Serializer):
    from_time = serializers.DateTimeField(required=False, allow_null=True)
    unread = serializers.BooleanField(required=False, allow_null=True)


class FilterNotificationRequestSerializer(BasePagingSerializer):
    filter = FilterNotificationRequestParamSerializer()


class FilterNotificationResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=NotificationSerializer())


class UpdateUnreadNotificationRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Notification id')


class UpdateUnreadNotificationResponseSerializer(BaseResponseSerializer):
    pass