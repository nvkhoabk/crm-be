from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from aim.apps.common.base_view import BaseAPIView
from aim.apps.common.cookies import Cookies
from aim.apps.common.authenticate_config import authentication_class

from .services import AssetCreateService, AssetGetService, AssetFilterService, \
    AssetUpdateService, AssetDeleteService, ServiceException, AssetTypeGetService, AssetTypeGetAllService, \
    AssetStatusGetAllService, AssetStatusGetService, AssetGetNewService, AssetGetBuyingService, AssetGetOwningService, \
    AssetGetTransferringService
from .serializers import request_serializer
from .serializers import response_serializer
from .models import AssetType, AssetStatus, Asset


# Asset api
class AssetCreateView(BaseAPIView):
    serializer_class = request_serializer.AssetCreateSerializer

    @csrf_exempt
    @authentication_class('create_asset')
    def authenticate(self, request):
        None

    @swagger_auto_schema(
        operation_id='create_asset',
        operation_description='Create Asset',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: response_serializer.AssetSerializer(),
            status.HTTP_400_BAD_REQUEST: "Invalid request",
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_create_service = AssetCreateService()
        asset = asset_create_service.serve(cookies, *args, **serializer.validated_data)
        return self.get_response(results=asset, request=request, serializer=response_serializer.AssetSerializer)


class AssetFilterView(BaseAPIView):
    serializer_class = request_serializer.AssetFilterSerializer
    pagination_class = LimitOffsetPagination()

    @csrf_exempt
    @authentication_class('get_all_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_all_asset',
        operation_description='Get All Asset',
        request_body=serializer_class,
        manual_parameters=[openapi.Parameter(
            name='offset', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="offset"), openapi.Parameter(
            name='limit', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="limit")],
        responses={status.HTTP_200_OK: response_serializer.FilterAssetPagationSerializer()}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_filter_service = AssetFilterService()
        assets = asset_filter_service.serve(cookies, *args, **serializer.validated_data)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetSerializer, many=True)


class AssetGetView(BaseAPIView):

    @csrf_exempt
    @authentication_class('get_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_asset',
        operation_description='Get Asset',
        responses={
            status.HTTP_200_OK: response_serializer.AssetSerializer(),
            status.HTTP_404_NOT_FOUND: "Not found"
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_get_service = AssetGetService()
        try:
            asset = asset_get_service.serve(cookies, *args, **kwargs)
            return self.get_response(results=asset, request=request, serializer=response_serializer.AssetSerializer)
        except ServiceException:
            return Response(str(asset_get_service.exception), status=asset_get_service.status)


class AssetUpdateView(BaseAPIView):
    serializer_class = request_serializer.AssetUpdateSerializer

    @csrf_exempt
    @authentication_class('update_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='update_asset',
        operation_description='Update Asset',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: response_serializer.AssetSerializer(),
            status.HTTP_404_NOT_FOUND: "Not found"
        }
    )
    def put(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_update_service = AssetUpdateService()
        try:
            asset_update_service.serve(cookies, **serializer.validated_data)
            return self.get_response()
        except ServiceException:
            return Response(str(asset_update_service.exception), status=asset_update_service.status)


class AssetDeleteView(BaseAPIView):

    @csrf_exempt
    @authentication_class('delete_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='delete_asset',
        operation_description='Delete Asset',
        responses={
            status.HTTP_200_OK: response_serializer.AssetSerializer(),
            status.HTTP_404_NOT_FOUND: "Not found"
        }
    )
    def delete(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_delete_service = AssetDeleteService()
        try:
            asset_delete_service.serve(cookies, *args, **kwargs)
            return self.get_response()
        except ServiceException:
            return Response(str(asset_delete_service.exception), status=asset_delete_service.status)


# Asset type api
class AssetTypeGetAllView(BaseAPIView):

    @csrf_exempt
    @authentication_class('get_all_asset_type')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_all_asset_type',
        operation_description='Get All Asset Type',
        responses={status.HTTP_200_OK: response_serializer.AssetTypeSerializer(many=True)}
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_type_get_all_service = AssetTypeGetAllService()
        assets = asset_type_get_all_service.serve(cookies, *args, **kwargs)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetTypeSerializer, many=True)


class AssetTypeGetView(BaseAPIView):

    @csrf_exempt
    @authentication_class('get_asset_type')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_asset_type',
        operation_description='Get Asset Type',
        responses={
            status.HTTP_200_OK: response_serializer.AssetTypeSerializer(),
            status.HTTP_404_NOT_FOUND: "Not found"
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_type_get_service = AssetTypeGetService()
        try:
            asset = asset_type_get_service.serve(cookies, *args, **kwargs)
            return self.get_response(results=asset, request=request, serializer=response_serializer.AssetTypeSerializer)
        except ServiceException:
            return Response(str(asset_type_get_service.exception), status=asset_type_get_service.status)


# Asset type api
class AssetStatusGetAllView(BaseAPIView):

    @csrf_exempt
    @authentication_class('get_all_asset_status')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_all_asset_status',
        operation_description='Get All Asset Status',
        responses={status.HTTP_200_OK: response_serializer.AssetStatusSerializer(many=True)}
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_status_get_all_service = AssetStatusGetAllService()
        assets = asset_status_get_all_service.serve(cookies, *args, **kwargs)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetStatusSerializer, many=True)


class AssetStatusGetView(BaseAPIView):

    @csrf_exempt
    @authentication_class('get_asset_status')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_asset_status',
        operation_description='Get Asset Status',
        responses={
            status.HTTP_200_OK: response_serializer.AssetStatusSerializer(),
            status.HTTP_404_NOT_FOUND: "Not found"
        }
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_status_get_service = AssetStatusGetService()
        try:
            asset = asset_status_get_service.serve(cookies, *args, **kwargs)
            return self.get_response(results=asset, request=request,
                                     serializer=response_serializer.AssetStatusSerializer)
        except ServiceException:
            return Response(str(asset_status_get_service.exception), status=asset_status_get_service.status)


class AssetGetNewView(BaseAPIView):
    pagination_class = LimitOffsetPagination()

    @csrf_exempt
    @authentication_class('get_new_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_new_asset',
        operation_description='Get New Asset',
        manual_parameters=[openapi.Parameter(
            name='offset', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="offset"), openapi.Parameter(
            name='limit', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="limit")],
        responses={status.HTTP_200_OK: response_serializer.FilterAssetPagationSerializer()}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_get_new_service = AssetGetNewService()
        assets = asset_get_new_service.serve(cookies)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetSerializer, many=True)


class AssetGetBuyingView(BaseAPIView):
    pagination_class = LimitOffsetPagination()

    @csrf_exempt
    @authentication_class('get_buying_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_buying_asset',
        operation_description='Get Buying Asset',
        manual_parameters=[openapi.Parameter(
            name='offset', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="offset"), openapi.Parameter(
            name='limit', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="limit")],
        responses={status.HTTP_200_OK: response_serializer.FilterAssetPagationSerializer()}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_get_buying_service = AssetGetBuyingService()
        assets = asset_get_buying_service.serve(cookies)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetSerializer, many=True)


class AssetGetOwningView(BaseAPIView):
    pagination_class = LimitOffsetPagination()

    @csrf_exempt
    @authentication_class('get_owning_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_owning_asset',
        operation_description='Get Owning Asset',
        manual_parameters=[openapi.Parameter(
            name='offset', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="offset"), openapi.Parameter(
            name='limit', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="limit")],
        responses={status.HTTP_200_OK: response_serializer.FilterAssetPagationSerializer()}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_get_owning_service = AssetGetOwningService()
        assets = asset_get_owning_service.serve(cookies)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetSerializer, many=True)


class AssetGetTransferringView(BaseAPIView):
    pagination_class = LimitOffsetPagination()

    @csrf_exempt
    @authentication_class('get_transferring_asset')
    def authenticate(self, request):
        return None

    @swagger_auto_schema(
        operation_id='get_transferring_asset',
        operation_description='Get Transferring Asset',
        manual_parameters=[openapi.Parameter(
            name='offset', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="offset"), openapi.Parameter(
            name='limit', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER, required=True,
            description="limit")],
        responses={status.HTTP_200_OK: response_serializer.FilterAssetPagationSerializer()}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        asset_get_transferring_service = AssetGetTransferringService()
        assets = asset_get_transferring_service.serve(cookies)
        return self.get_response(results=assets, request=request,
                                 serializer=response_serializer.AssetSerializer, many=True)

