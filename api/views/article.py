from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from api.serializers import request_serializer
from api.serializers import response_serializer
from api.common.base_view import BaseAPIView
from api.services.article import ArticleCreateService


class ArticleCreateView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = request_serializer.ArticleCreateSerializer
    
    @swagger_auto_schema(
        operation_id='Create article',
        operation_description='Description',
        request_body=serializer_class,
        response={
            status.HTTP_200_OK: response_serializer.ArticleResponseSerializer(),
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        article_create_service = ArticleCreateService()
        article = article_create_service.serve(cookies, *args, **serializer.validated_data)
        return self.get_response(results=article, request=request, serializer=response_serializer.ArticleResponseSerializer)
