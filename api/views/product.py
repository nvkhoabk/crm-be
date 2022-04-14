from api.common.base_view import BaseAPIView
from api.serializers import product_serializer
from api.services import exceptions
from api.services import product as product_service
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import ProductReadPermission, ProductEditPermission


class CreateProductView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ProductEditPermission]
    serializer_class = product_serializer.CreateProductRequestSerializer

    @swagger_auto_schema(
        tags=['Product'],
        operation_id='Create product',
        operation_description='Create product api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: product_serializer.CreateProductResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_product_service = product_service.CreateProductService()
        product = create_product_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=product_serializer.CreateProductResponseSerializer)


class GetProductView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ProductReadPermission]
    serializer_class = product_serializer.GetProductRequestSerializer

    @swagger_auto_schema(
        tags=['Product'],
        operation_id='Get product',
        operation_description='Get product api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: product_serializer.GetProductResponseSerializer,
            exceptions.ProductNotFound.code: exceptions.ProductNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_product_service = product_service.GetProductService()
        product = get_product_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=product_serializer.GetProductResponseSerializer)


class UpdateProductView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ProductEditPermission]
    serializer_class = product_serializer.UpdateProductRequestSerializer

    @swagger_auto_schema(
        tags=['Product'],
        operation_id='Update product',
        operation_description='Update product api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: product_serializer.UpdateProductResponseSerializer,
            exceptions.ProductNotFound.code: exceptions.ProductNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_product_service = product_service.UpdateProductService()
        product = update_product_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=product_serializer.UpdateProductResponseSerializer)


class FilterProductView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ProductReadPermission]
    serializer_class = product_serializer.FilterProductRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Product'],
        operation_id='Filter product',
        operation_description='Filter product api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: product_serializer.FilterProductResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_product_service = product_service.FilterProductService()
        products = filter_product_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=product_serializer.FilterProductResponseSerializer)


class DeleteProductView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, ProductEditPermission]
    serializer_class = product_serializer.DeleteProductRequestSerializer

    @swagger_auto_schema(
        tags=['Product'],
        operation_id='Delete product',
        operation_description='Delete product api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: product_serializer.DeleteProductResponseSerializer,
            exceptions.ProductNotFound.code: exceptions.ProductNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_product_service = product_service.DeleteProductService()
        product = delete_product_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=product_serializer.DeleteProductResponseSerializer)
