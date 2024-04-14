from api.common.base_view import BaseAPIView
from api.serializers import phone_number_serializer
from api.services import exceptions
from api.services import phone_number as phone_number_service
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.permissions import PhoneNumberReadPermission, PhoneNumberEditPermission, CallCenterAuthenticated


class CreateMainPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreateMainPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['MainPhoneNumber'],
        operation_id='Create main_phone_number',
        operation_description='Create main_phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreateMainPhoneNumberResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreateMainPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreateMainPhoneNumberResponseSerializer)


class GetMainPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetMainPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['MainPhoneNumber'],
        operation_id='Get main_phone_number',
        operation_description='Get main_phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetMainPhoneNumberResponseSerializer,
            exceptions.MainPhoneNumberNotFound.code: exceptions.MainPhoneNumberNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetMainPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetMainPhoneNumberResponseSerializer)


class UpdateMainPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdateMainPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['MainPhoneNumber'],
        operation_id='Update main_phone_number',
        operation_description='Update main_phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdateMainPhoneNumberResponseSerializer,
            exceptions.MainPhoneNumberNotFound.code: exceptions.MainPhoneNumberNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdateMainPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdateMainPhoneNumberResponseSerializer)


class FilterMainPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterMainPhoneNumberRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['MainPhoneNumber'],
        operation_id='Filter main_phone_number',
        operation_description='Filter main_phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterMainPhoneNumberResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterMainPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterMainPhoneNumberResponseSerializer)


class DeleteMainPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeleteMainPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['MainPhoneNumber'],
        operation_id='Delete main_phone_number',
        operation_description='Delete main_phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeleteMainPhoneNumberResponseSerializer,
            exceptions.MainPhoneNumberNotFound.code: exceptions.MainPhoneNumberNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeleteMainPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeleteMainPhoneNumberResponseSerializer)


class CreateProviderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreateProviderRequestSerializer

    @swagger_auto_schema(
        tags=['Provider'],
        operation_id='Create provider',
        operation_description='Create provider api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreateProviderResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreateProviderService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreateProviderResponseSerializer)


class GetProviderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetProviderRequestSerializer

    @swagger_auto_schema(
        tags=['Provider'],
        operation_id='Get provider',
        operation_description='Get provider api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetProviderResponseSerializer,
            exceptions.ProviderNotFound.code: exceptions.ProviderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetProviderService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetProviderResponseSerializer)


class UpdateProviderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdateProviderRequestSerializer

    @swagger_auto_schema(
        tags=['Provider'],
        operation_id='Update provider',
        operation_description='Update provider api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdateProviderResponseSerializer,
            exceptions.ProviderNotFound.code: exceptions.ProviderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdateProviderService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdateProviderResponseSerializer)


class FilterProviderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterProviderRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Provider'],
        operation_id='Filter provider',
        operation_description='Filter provider api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterProviderResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterProviderService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterProviderResponseSerializer)


class DeleteProviderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeleteProviderRequestSerializer

    @swagger_auto_schema(
        tags=['Provider'],
        operation_id='Delete provider',
        operation_description='Delete provider api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeleteProviderResponseSerializer,
            exceptions.ProviderNotFound.code: exceptions.ProviderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeleteProviderService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeleteProviderResponseSerializer)


class CreateLegalView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreateLegalRequestSerializer

    @swagger_auto_schema(
        tags=['Legal'],
        operation_id='Create legal',
        operation_description='Create legal api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreateLegalResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreateLegalService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreateLegalResponseSerializer)


class GetLegalView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetLegalRequestSerializer

    @swagger_auto_schema(
        tags=['Legal'],
        operation_id='Get legal',
        operation_description='Get legal api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetLegalResponseSerializer,
            exceptions.LegalNotFound.code: exceptions.LegalNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetLegalService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetLegalResponseSerializer)


class UpdateLegalView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdateLegalRequestSerializer

    @swagger_auto_schema(
        tags=['Legal'],
        operation_id='Update legal',
        operation_description='Update legal api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdateLegalResponseSerializer,
            exceptions.LegalNotFound.code: exceptions.LegalNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdateLegalService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdateLegalResponseSerializer)


class FilterLegalView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterLegalRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Legal'],
        operation_id='Filter legal',
        operation_description='Filter legal api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterLegalResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterLegalService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterLegalResponseSerializer)


class DeleteLegalView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeleteLegalRequestSerializer

    @swagger_auto_schema(
        tags=['Legal'],
        operation_id='Delete legal',
        operation_description='Delete legal api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeleteLegalResponseSerializer,
            exceptions.LegalNotFound.code: exceptions.LegalNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeleteLegalService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeleteLegalResponseSerializer)


class CreatePhoneNumberClientView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreatePhoneNumberClientRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberClient'],
        operation_id='Create phone_number_client',
        operation_description='Create phone_number_client api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreatePhoneNumberClientResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreatePhoneNumberClientService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreatePhoneNumberClientResponseSerializer)


class GetPhoneNumberClientView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetPhoneNumberClientRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberClient'],
        operation_id='Get phone_number_client',
        operation_description='Get phone_number_client api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetPhoneNumberClientResponseSerializer,
            exceptions.PhoneNumberClientNotFound.code: exceptions.PhoneNumberClientNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetPhoneNumberClientService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetPhoneNumberClientResponseSerializer)


class UpdatePhoneNumberClientView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdatePhoneNumberClientRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberClient'],
        operation_id='Update phone_number_client',
        operation_description='Update phone_number_client api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdatePhoneNumberClientResponseSerializer,
            exceptions.PhoneNumberClientNotFound.code: exceptions.PhoneNumberClientNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdatePhoneNumberClientService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdatePhoneNumberClientResponseSerializer)


class FilterPhoneNumberClientView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterPhoneNumberClientRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumberClient'],
        operation_id='Filter phone_number_client',
        operation_description='Filter phone_number_client api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterPhoneNumberClientResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterPhoneNumberClientService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterPhoneNumberClientResponseSerializer)


class DeletePhoneNumberClientView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeletePhoneNumberClientRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberClient'],
        operation_id='Delete phone_number_client',
        operation_description='Delete phone_number_client api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeletePhoneNumberClientResponseSerializer,
            exceptions.PhoneNumberClientNotFound.code: exceptions.PhoneNumberClientNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeletePhoneNumberClientService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeletePhoneNumberClientResponseSerializer)


class CreatePhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreatePhoneNumberStatusRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberStatus'],
        operation_id='Create phone_number_status',
        operation_description='Create phone_number_status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreatePhoneNumberStatusResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreatePhoneNumberStatusService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreatePhoneNumberStatusResponseSerializer)


class GetPhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetPhoneNumberStatusRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberStatus'],
        operation_id='Get phone_number_status',
        operation_description='Get phone_number_status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetPhoneNumberStatusResponseSerializer,
            exceptions.PhoneNumberStatusNotFound.code: exceptions.PhoneNumberStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetPhoneNumberStatusService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetPhoneNumberStatusResponseSerializer)


class UpdatePhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdatePhoneNumberStatusRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberStatus'],
        operation_id='Update phone_number_status',
        operation_description='Update phone_number_status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdatePhoneNumberStatusResponseSerializer,
            exceptions.PhoneNumberStatusNotFound.code: exceptions.PhoneNumberStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdatePhoneNumberStatusService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdatePhoneNumberStatusResponseSerializer)


class FilterPhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterPhoneNumberStatusRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumberStatus'],
        operation_id='Filter phone_number_status',
        operation_description='Filter phone_number_status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterPhoneNumberStatusResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterPhoneNumberStatusService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterPhoneNumberStatusResponseSerializer)


class DeletePhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeletePhoneNumberStatusRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberStatus'],
        operation_id='Delete phone_number_status',
        operation_description='Delete phone_number_status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeletePhoneNumberStatusResponseSerializer,
            exceptions.PhoneNumberStatusNotFound.code: exceptions.PhoneNumberStatusNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeletePhoneNumberStatusService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeletePhoneNumberStatusResponseSerializer)


class CreatePhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreatePhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Create phone_number',
        operation_description='Create phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreatePhoneNumberResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreatePhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreatePhoneNumberResponseSerializer)


class GetPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Get phone_number',
        operation_description='Get phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetPhoneNumberResponseSerializer,
            exceptions.PhoneNumberNotFound.code: exceptions.PhoneNumberNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetPhoneNumberResponseSerializer)


class UpdatePhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdatePhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Update phone_number',
        operation_description='Update phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdatePhoneNumberResponseSerializer,
            exceptions.PhoneNumberNotFound.code: exceptions.PhoneNumberNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdatePhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdatePhoneNumberResponseSerializer)


class FilterPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterPhoneNumberRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Filter phone_number',
        operation_description='Filter phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterPhoneNumberResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterPhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterPhoneNumberResponseSerializer)


class BulkUpdatePhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.BulkUpdatePhoneNumberStatusRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='bulk update phone_number status',
        operation_description='bulk update phone_number status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.BulkUpdatePhoneNumberStatusResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.BulkUpdateStatusService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response()


class GetStatisticPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterPhoneNumberRequestSerializer
    pagination_class = False

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='GetStatisticPhoneNumber',
        operation_description='GetStatisticPhoneNumber',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetStatisticPhoneNumberResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetStatisticPhoneNumberService()
        results = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=phone_number_serializer.GetStatisticPhoneNumberResponseSerializer)


class UpdateListPhoneNumberStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.UpdateListPhoneNumberStatusRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='UpdateListPhoneNumberStatus',
        operation_description='UpdateListPhoneNumberStatus',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdateListPhoneNumberStatusResponseSerializer,
            exceptions.OrderNotFound.code: exceptions.OrderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdateListPhoneNumberStatusService()
        results = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=phone_number_serializer.UpdateListPhoneNumberStatusResponseSerializer)


class DeletePhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeletePhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Delete phone_number',
        operation_description='Delete phone_number api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeletePhoneNumberResponseSerializer,
            exceptions.PhoneNumberNotFound.code: exceptions.PhoneNumberNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeletePhoneNumberService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeletePhoneNumberResponseSerializer)


class CreatePhoneNumberMonthlyFeeView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.CreatePhoneNumberMonthlyFeeRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberMonthlyFee'],
        operation_id='Create phone_number_monthly_fee',
        operation_description='Create phone_number_monthly_fee api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.CreatePhoneNumberMonthlyFeeResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.CreatePhoneNumberMonthlyFeeService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.CreatePhoneNumberMonthlyFeeResponseSerializer)


class GetPhoneNumberMonthlyFeeView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.GetPhoneNumberMonthlyFeeRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberMonthlyFee'],
        operation_id='Get phone_number_monthly_fee',
        operation_description='Get phone_number_monthly_fee api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.GetPhoneNumberMonthlyFeeResponseSerializer,
            exceptions.PhoneNumberMonthlyFeeNotFound.code: exceptions.PhoneNumberMonthlyFeeNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.GetPhoneNumberMonthlyFeeService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.GetPhoneNumberMonthlyFeeResponseSerializer)


class UpdatePhoneNumberMonthlyFeeView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.UpdatePhoneNumberMonthlyFeeRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberMonthlyFee'],
        operation_id='Update phone_number_monthly_fee',
        operation_description='Update phone_number_monthly_fee api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.UpdatePhoneNumberMonthlyFeeResponseSerializer,
            exceptions.PhoneNumberMonthlyFeeNotFound.code: exceptions.PhoneNumberMonthlyFeeNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.UpdatePhoneNumberMonthlyFeeService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.UpdatePhoneNumberMonthlyFeeResponseSerializer)


class FilterPhoneNumberMonthlyFeeView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.FilterPhoneNumberMonthlyFeeRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumberMonthlyFee'],
        operation_id='Filter phone_number_monthly_fee',
        operation_description='Filter phone_number_monthly_fee api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterPhoneNumberMonthlyFeeResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterPhoneNumberMonthlyFeeService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterPhoneNumberMonthlyFeeResponseSerializer)


class DeletePhoneNumberMonthlyFeeView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.DeletePhoneNumberMonthlyFeeRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumberMonthlyFee'],
        operation_id='Delete phone_number_monthly_fee',
        operation_description='Delete phone_number_monthly_fee api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.DeletePhoneNumberMonthlyFeeResponseSerializer,
            exceptions.PhoneNumberMonthlyFeeNotFound.code: exceptions.PhoneNumberMonthlyFeeNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.DeletePhoneNumberMonthlyFeeService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=request,
                                 serializer=phone_number_serializer.DeletePhoneNumberMonthlyFeeResponseSerializer)


class FilterPhoneNumberActivityView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberReadPermission]
    serializer_class = phone_number_serializer.FilterPhoneNumberActivityRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumberActivity'],
        operation_id='Filter phone number activity',
        operation_description='Filter phone number activity api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterPhoneNumberActivityResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterPhoneNumberActivityService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterPhoneNumberActivityResponseSerializer)


class FilterPhoneNumberLockHistoryView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberReadPermission]
    serializer_class = phone_number_serializer.FilterPhoneNumberActivityRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['PhoneNumberActivity'],
        operation_id='Filter phone number lock history',
        operation_description='Filter phone number lock history api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: phone_number_serializer.FilterPhoneNumberLockHistoryResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.FilterPhoneNumberLockHistoryService()
        result = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=result, request=serializer.validated_data,
                                 serializer=phone_number_serializer.FilterPhoneNumberLockHistoryResponseSerializer)


class PushToQueueView(BaseAPIView):
    authentication_classes = []
    permission_classes = [CallCenterAuthenticated]

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='Push phone number to queue',
        operation_description='Push phone number to queue'
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.PushToQueueService()
        service.serve(request, cookies, *args, **kwargs)
        return self.get_response()


class ImportPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = phone_number_serializer.ImportPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['PhoneNumber'],
        operation_id='import phone number',
        operation_description='Import phone number from excel file',
        request_body=serializer_class,
        responses={
            0: phone_number_serializer.ImportPhoneNumberResponseSerializer
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.ImportPhoneNumberService()
        results = service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=phone_number_serializer.ImportPhoneNumberResponseSerializer)


class ConfirmImportPhoneNumberView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, PhoneNumberEditPermission]
    serializer_class = phone_number_serializer.ConfirmImportPhoneNumberRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='confirm phone number',
        operation_description='confirm import phone number from excel file',
        request_body=serializer_class,
        responses={
            0: phone_number_serializer.ConfirmImportPhoneNumberRequestSerializer
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = phone_number_service.ConfirmImportPhoneNumberService()
        results = service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=phone_number_serializer.ImportPhoneNumberResponseSerializer)
