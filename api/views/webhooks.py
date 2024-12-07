from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.common.base_view import BaseAPIView
from api.permissions import SuperAdminPermission
from api.serializers import manage_serializer
from api.services import exceptions
from api.services import manage as manage_service


class VerifyWebhooksView(BaseAPIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Push phone number to queue',
        operation_description='Push phone number to queue'
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        challenge = int(request.GET.get('hub.challenge', None))
        request.GET.get('hub.verify_token')
        print(challenge)
        return Response(data=challenge, status=status.HTTP_200_OK)
