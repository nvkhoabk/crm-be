from api.common.base_view import BaseAPIView
from api.serializers import call_center_serializer
from api.services import exceptions
from api.services import call_center as call_center_service
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from api.permissions import SuperAdminPermission, CallCenterAuthenticated


class CreateCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]
    serializer_class = call_center_serializer.CreateCallCenterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Create Call Center',
        operation_description='Create Call Center',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.CreateCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.CallCenterDuplicated.code: exceptions.CallCenterDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.CreateCallCenterService()
        call_center = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=call_center, request=request,
                                 serializer=call_center_serializer.CreateCallCenterResponseSerializer)


class GetCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]
    serializer_class = call_center_serializer.GetCallCenterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Get Call Center',
        operation_description='Get Call Center',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_call_center_service = call_center_service.GetCallCenterService()
        call_center = get_call_center_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=call_center, request=request,
                                 serializer=call_center_serializer.GetCallCenterResponseSerializer)


class UpdateCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]
    serializer_class = call_center_serializer.UpdateCallCenterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Update Call Center',
        operation_description='Update Call Center',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.UpdateCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_call_center_service = call_center_service.UpdateCallCenterService()
        call_center = update_call_center_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=call_center, request=request,
                                 serializer=call_center_serializer.UpdateCallCenterResponseSerializer)


class FilterCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]
    serializer_class = call_center_serializer.FilterCallCenterRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Filter Call Center',
        operation_description='Filter Call Center',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.FilterCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.FilterCallCenterService()
        results = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=serializer.validated_data,
                                 serializer=call_center_serializer.FilterCallCenterResponseSerializer)


class EnableCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]
    serializer_class = call_center_serializer.EnableCallCenterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Enable Call Center',
        operation_description='Enable Call Center',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.EnableCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        enable_call_center_service = call_center_service.EnableCallCenterService()
        call_center = enable_call_center_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=call_center, request=request,
                                 serializer=call_center_serializer.EnableCallCenterResponseSerializer)


class DisableCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]
    serializer_class = call_center_serializer.DisableCallCenterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Disable Call Center',
        operation_description='Disable Call Center',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.DisableCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        disable_call_center_service = call_center_service.DisableCallCenterService()
        call_center = disable_call_center_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=call_center, request=request,
                                 serializer=call_center_serializer.DisableCallCenterResponseSerializer)

class CalculatePayemntCallCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, SuperAdminPermission]

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Calculate payment call center',
        operation_description='Calculate payment call center',
        responses={
            0: call_center_serializer.CalculatePayemntCallCenterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.CalculatePaymentCallCenterService()
        results = service.serve(
            request, cookies, *args, **kwargs)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.CalculatePayemntCallCenterResponseSerializer)


class GetAgentsView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetAgentsRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Agents'],
        operation_id='Get Agents',
        operation_description='Get Agents',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetAgentsResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.CallCenterDuplicated.code: exceptions.CallCenterDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_agent_list_service = call_center_service.GetAgentsService()
        results = get_agent_list_service.serve(request, cookies)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.GetAgentsResponseSerializer)


class UpdateAgentsView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.UpdateAgentsRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Agents'],
        operation_id='Update Agents',
        operation_description='Update Agents',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.UpdateAgentsResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg,
            exceptions.CallCenterDuplicated.code: exceptions.CallCenterDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_agent_list_service = call_center_service.UpdateAgentService()
        results = update_agent_list_service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.UpdateAgentsResponseSerializer)


class StartCallInView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Manage Call Events'],
        operation_id='Start Call In',
        operation_description='Start Call In',
        responses={}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        return self.get_response()


class EndCallInView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Manage Call Events'],
        operation_id='End Call In',
        operation_description='End Call In',
        responses={}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        return self.get_response()


class StartCallOutView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Manage Call Events'],
        operation_id='Start Call Out',
        operation_description='End Call Out',
        responses={}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        return self.get_response()


class EndCallOutView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Manage Call Events'],
        operation_id='End Call Out',
        operation_description='End Call Out',
        responses={}
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        return self.get_response()


class GetCompanyCallHistoryView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetCompanyCallHistoryRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call History'],
        operation_id='Get company call history',
        operation_description='Get company call history',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetCompanyCallHistoryResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.GetCompanyCallHistoryService()
        results = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=results, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetCompanyCallHistoryResponseSerializer)


class GetUserCallHistoryView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetUserCallHistoryRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call History'],
        operation_id='Get call history',
        operation_description='Get user call history',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetUserCallHistoryResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.GetUserCallHistoryService()
        results = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=results, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetUserCallHistoryResponseSerializer)


class GetCallReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetCallReportRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Get call report',
        operation_description='Get call report',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetCallReportResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.GetCallReportService()
        results = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=results, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetCallReportResponseSerializer)


class CreateAgentRegisterCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.CreateAgentResiterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Agents'],
        operation_id='Create Agent Register',
        operation_description='Create Agent Register',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.CreateAgentRegisterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.CreateAgentRegisterService()
        results = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.CreateAgentRegisterResponseSerializer)


class DeleteAgentRegisterCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.DeleteAgentRegisterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Agents'],
        operation_id='Delete Agent Register',
        operation_description='Delete Agent Register',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.DeleteAgentRegisterResponseSerializer,
            exceptions.AgentRegisterNotFound.code: exceptions.AgentRegisterNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.DeleteAgentRegisterService()
        results = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.DeleteAgentRegisterResponseSerializer)


class FilterAgentRegisterCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.FilterAgentRegisterRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call Agents'],
        operation_id='Filter Agent Register',
        operation_description='Filter Agent Register',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.CreateAgentRegisterResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.FilterAgentRegisterService()
        results = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=serializer.validated_data,
                                 serializer=call_center_serializer.FilterAgentRegisterResponseSerializer)


class GetExternalPaymentReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetExternalPaymentReportRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Get external report',
        operation_description='Get external report',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetExternalPaymentReportResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.GetExternalPaymentReportService()
        results = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=results, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetExternalPaymentReportResponseSerializer)


class GetCreditPaymentReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetCreditPaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Get credit payment report',
        operation_description='Get credit payment report',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.GetCreditPaymentResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.GetCreditPaymentReportService()
        results = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.GetCreditPaymentResponseSerializer)


class IncomingCallView(BaseAPIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Incoming call',
        operation_description='Incoming call'
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.IncomingCallService()
        service.serve(request, cookies, *args, **kwargs)
        return self.get_response()


class OutgoingCallView(BaseAPIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Outgoing call',
        operation_description='Outgoing call'
    )
    def get(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.OutgoingCallService()
        service.serve(request, cookies, *args, **kwargs)
        return self.get_response()


class CallAnsweredView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = call_center_serializer.CallLogRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
        operation_id='Call answered',
        operation_description='Call answered',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.CallLogResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.CallAnsweredService()
        service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response()


class UploadExtFile(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = call_center_serializer.UploadExtFileRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Upload extension file',
        operation_description='Upload extension file',
        request_body=serializer_class,
        responses={
            0: call_center_serializer.UploadExtFileResponseSerializer,
            exceptions.CallCenterNotFound.code: exceptions.CallCenterNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.UploadExtFileService()
        results = service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=call_center_serializer.UploadExtFileResponseSerializer)

class DownloadExtFile(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = call_center_serializer.DownloadExtFileRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Download extension file',
        operation_description='Download extension file',
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = call_center_service.DownloadExtFileService()
        response = service.serve(request, cookies, *args, **serializer.validated_data)
        return response
