from api.common.base_view import BaseAPIView
from api.serializers import notification_serializer
from api.services import exceptions
from api.services import notification as notification_service
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import ProductReadPermission, ProductEditPermission


class FilterNotificationView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = notification_serializer.FilterNotificationRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Notification'],
        operation_id='Filter notification',
        operation_description='Filter notification api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: notification_serializer.FilterNotificationResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = notification_service.FilterNotificationService()
        notifications = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=notifications, request=serializer.validated_data,
                                 serializer=notification_serializer.FilterNotificationResponseSerializer)


class UpdateUnreadNotificationView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ProductEditPermission]
    serializer_class = notification_serializer.UpdateUnreadNotificationRequestSerializer

    @swagger_auto_schema(
        tags=['Notification'],
        operation_id='Delete product',
        operation_description='Update unread notification api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: notification_serializer.UpdateUnreadNotificationRequestSerializer,
            exceptions.ProductNotFound.code: exceptions.ProductNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = notification_service.UpdateUnreadNotificationService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=notification_serializer.UpdateUnreadNotificationResponseSerializer)
