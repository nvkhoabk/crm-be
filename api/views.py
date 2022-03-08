from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from api.serializers import request_serializer
from api.serializers import response_serializer


class ArticleCreateView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = request_serializer.ArticleCreateSerializer
    
    @swagger_auto_schema(
        operation_id='Create article',
        operation_description='Description',
        request_body=serializer_class,
        response={
            status.HTTP_200_OK: response_serializer.ArticleSerializer(),
        }
    )
    def post(self, request, serializer=None, *args, **kwargs):
        pass
