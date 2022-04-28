from api.common.base_view import BaseAPIView
from api.serializers import call_center_serializer
from api.services import exceptions
from api.services import call_center as call_center_service
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from api.permissions import SuperAdminPermission


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
        disable_call_center_service = call_center_service.DisableCallCenterService()
        call_center = disable_call_center_service.serve(
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


class GetAgentsView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetAgentsRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        user = get_agent_list_service.serve(request, cookies)
        return self.get_response(results=user, request=request,
                                 serializer=call_center_serializer.GetAgentsResponseSerializer)


class UpdateAgentsView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.UpdateAgentsRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        user = update_agent_list_service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=user, request=request,
                                 serializer=call_center_serializer.UpdateAgentsResponseSerializer)


class StartCallInView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        tags=['Manage Call Center'],
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
        tags=['Manage Call Center'],
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
        tags=['Manage Call Center'],
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
    forward_pagination = True

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        user = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=user, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetCompanyCallHistoryResponseSerializer)


class GetUserCallHistoryView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetUserCallHistoryRequestSerializer
    pagination_class = True
    forward_pagination = True

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        user = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=user, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetUserCallHistoryResponseSerializer)


class GetCallReportView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.GetCallReportRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        user = service.serve(request, cookies, **serializer.validated_data)
        return self.get_response(results=user, request=serializer.validated_data,
                                 serializer=call_center_serializer.GetCallReportResponseSerializer)


class CreateAgentRegisterCenterView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated]
    serializer_class = call_center_serializer.CreateAgentResiterRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center'],
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
        tags=['Manage Call Center'],
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
        tags=['Manage Call Center'],
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
