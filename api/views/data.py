from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.common.base_view import BaseAPIView
from api.permissions import DataReadPermission, DataEditPermission, AccountEditPermission
from api.serializers import data_serializer
from api.services import data as data_service
from api.services import exceptions


class FilterCrawlDataView(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = data_serializer.FilterCrawlDataRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['CrawlData'],
        operation_id='Filter crawl data',
        operation_description='Filter crawl data api',
        request_body=serializer_class,
        responses={
            status.HTTP_200_OK: data_serializer.FilterCrawlDataResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_crawl_data_service = data_service.FilterCrawlDataService()
        data = filter_crawl_data_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=data, request=serializer.validated_data, serializer=data_serializer.FilterCrawlDataResponseSerializer)


class GetCrawlDataView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.GetCrawlDataRequestSerializer

    @swagger_auto_schema(
        tags=['CrawlData'],
        operation_id='Get CrawlData',
        operation_description='Get CrawlData api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.GetCrawlDataResponseSerializer,
            exceptions.CrawlDataNotFound.code: exceptions.CrawlDataNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = data_service.GetCrawlDataService()
        crawl_data = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=crawl_data, request=request,
                                 serializer=data_serializer.GetCrawlDataResponseSerializer)


class CreateOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.CreateOrderRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Create order',
        operation_description='Create order api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.CreateOrderResponseSerializer,
            exceptions.OrderDuplicated.code: exceptions.OrderDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = data_service.CreateOrderService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.CreateOrderResponseSerializer)


class GetOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.GetOrderRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Get order',
        operation_description='Get order api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.GetOrderResponseSerializer,
            exceptions.OrderNotFound.code: exceptions.OrderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = data_service.GetOrderService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.GetOrderResponseSerializer)


class UpdateOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.UpdateOrderRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Update order',
        operation_description='Update order api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.UpdateOrderResponseSerializer,
            exceptions.OrderNotFound.code: exceptions.OrderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = data_service.UpdateOrderService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.UpdateOrderResponseSerializer)


class FilterOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.FilterOrderRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Filter order',
        operation_description='Filter order api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.FilterOrderResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = data_service.FilterOrderService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=data_serializer.FilterOrderResponseSerializer)


class DeleteOrderView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.DeleteOrderRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Delete order',
        operation_description='Delete order api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.DeleteOrderResponseSerializer,
            exceptions.OrderNotFound.code: exceptions.OrderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = data_service.DeleteOrderService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.DeleteOrderResponseSerializer)


class CreateOrderDetailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.CreateOrderDetailRequestSerializer

    @swagger_auto_schema(
        tags=['OrderDetail'],
        operation_id='Create order detail',
        operation_description='Create order detail api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.CreateOrderDetailResponseSerializer,
            exceptions.OrderDetailDuplicated.code: exceptions.OrderDetailDuplicated.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = data_service.CreateOrderDetailService()
        product = service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.CreateOrderDetailResponseSerializer)


class GetOrderDetailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.GetOrderDetailRequestSerializer

    @swagger_auto_schema(
        tags=['OrderDetail'],
        operation_id='Get order detail',
        operation_description='Get order detail api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.GetOrderDetailResponseSerializer,
            exceptions.OrderDetailNotFound.code: exceptions.OrderDetailNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = data_service.GetOrderDetailService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.GetOrderDetailResponseSerializer)


class UpdateOrderDetailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.UpdateOrderDetailRequestSerializer

    @swagger_auto_schema(
        tags=['OrderDetail'],
        operation_id='Update order detail',
        operation_description='Update order detail api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.UpdateOrderDetailResponseSerializer,
            exceptions.OrderDetailNotFound.code: exceptions.OrderDetailNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = data_service.UpdateOrderDetailService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.UpdateOrderDetailResponseSerializer)


class FilterOrderDetailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.FilterOrderDetailRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['OrderDetail'],
        operation_id='Filter order detail',
        operation_description='Filter order detail api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.FilterOrderDetailResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = data_service.FilterOrderDetailService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=data_serializer.FilterOrderDetailResponseSerializer)


class DeleteOrderDetailView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.DeleteOrderDetailRequestSerializer

    @swagger_auto_schema(
        tags=['OrderDetail'],
        operation_id='Delete order detail',
        operation_description='Delete order detail api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.DeleteOrderDetailResponseSerializer,
            exceptions.OrderDetailNotFound.code: exceptions.OrderDetailNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = data_service.DeleteOrderDetailService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.DeleteOrderDetailResponseSerializer)


class FilterOrderHistoryView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.FilterOrderHistoryRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['OrderHistory'],
        operation_id='Filter order history',
        operation_description='Filter order detail api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.FilterOrderHistoryResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = data_service.FilterOrderHistoryService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=data_serializer.FilterOrderHistoryResponseSerializer)


class FilterOrderDetailHistoryView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.FilterOrderDetailHistoryRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['OrderDetailHistory'],
        operation_id='Filter order detail history',
        operation_description='Filter order detail history api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.FilterOrderDetailHistoryResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = data_service.FilterOrderDetailHistoryService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=data_serializer.FilterOrderDetailHistoryResponseSerializer)


class BulkUpdateOrderStatusView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.BulkUpdateOrderStatusRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Bulk update order status',
        operation_description='Bulk update order status api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.BulkUpdateOrderStatusResponseSerializer,
            exceptions.OrderNotFound.code: exceptions.OrderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = data_service.BulkUpdateOrderStatusService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.BulkUpdateOrderStatusResponseSerializer)


class BulkUpdateOrderPicView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.BulkUpdateOrderPicRequestSerializer

    @swagger_auto_schema(
        tags=['Order'],
        operation_id='Bulk update order pic',
        operation_description='Bulk update order pic api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.BulkUpdateOrderPicResponseSerializer,
            exceptions.OrderNotFound.code: exceptions.OrderNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = data_service.BulkUpdateOrderPicService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.BulkUpdateOrderPicResponseSerializer)


class FilterFBPageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.FilterFBPageRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['FBPage'],
        operation_id='Filter FBPage',
        operation_description='Filter FBPage api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.FilterFBPageResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_service = data_service.FilterFBPageService()
        products = filter_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=products, request=serializer.validated_data,
                                 serializer=data_serializer.FilterFBPageResponseSerializer)


class DeleteFBPageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.DeleteFBPageRequestSerializer

    @swagger_auto_schema(
        tags=['FBPage'],
        operation_id='Delete FBPage',
        operation_description='Delete FBPage api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.DeleteFBPageResponseSerializer,
            exceptions.FBPageNotFound.code: exceptions.FBPageNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_service = data_service.DeleteFBPageService()
        product = delete_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.DeleteFBPageResponseSerializer)


class UpdateFBPageView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.UpdateFBPageRequestSerializer

    @swagger_auto_schema(
        tags=['FBPage'],
        operation_id='Update FBPage',
        operation_description='Update FBPage api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.UpdateFBPageResponseSerializer,
            exceptions.FBPageNotFound.code: exceptions.FBPageNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_service = data_service.UpdateFBPageService()
        product = update_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.UpdateFBPageResponseSerializer)


class GetSynchronizedFBAccountView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.GetSynchronizedFBAccountRequestSerializer

    @swagger_auto_schema(
        tags=['FBPage'],
        operation_id='Get SynchronizedFBAccount',
        operation_description='Get SynchronizedFBAccount api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.GetSynchronizedFBAccountResponseSerializer
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = data_service.GetSynchronizedFBAccountService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.GetSynchronizedFBAccountResponseSerializer)


class DeleteSynchronizedFBAccountView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.DeleteSynchronizedFBAccountRequestSerializer

    @swagger_auto_schema(
        tags=['FBPage'],
        operation_id='Get SynchronizedFBAccount',
        operation_description='Get SynchronizedFBAccount api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.DeleteSynchronizedFBAccountResponseSerializer
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_service = data_service.DeleteSynchronizedFBAccountService()
        product = get_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=product, request=request,
                                 serializer=data_serializer.DeleteSynchronizedFBAccountResponseSerializer)


class CreatePaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.CreatePaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Create Payment',
        operation_description='Create Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.CreatePaymentResponseSerializer,
            exceptions.ManageCompanyNotFound.code: exceptions.ManageCompanyNotFound.msg
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        create_payment_service = data_service.CreatePaymentService()
        payment = create_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payment, request=request,
                                 serializer=data_serializer.CreatePaymentResponseSerializer)


class GetPaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.GetPaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Get Payment',
        operation_description='Get Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.GetPaymentResponseSerializer,
            exceptions.PaymentNotFound.code: exceptions.PaymentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        get_payment_service = data_service.GetPaymentService()
        payment = get_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payment, request=request,
                                 serializer=data_serializer.GetPaymentResponseSerializer)


class UpdatePaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.UpdatePaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Update Payment',
        operation_description='Update Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.UpdatePaymentResponseSerializer,
            exceptions.PaymentNotFound.code: exceptions.PaymentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        update_payment_service = data_service.UpdatePaymentService()
        payment = update_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payment, request=request,
                                 serializer=data_serializer.UpdatePaymentResponseSerializer)


class ApprovePaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, AccountEditPermission]
    serializer_class = data_serializer.ApprovePaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Approve Payment',
        operation_description='Approve Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.ApprovePaymentResponseSerializer,
            exceptions.PaymentNotFound.code: exceptions.PaymentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        approve_payment_service = data_service.ApprovePaymentService()
        payment = approve_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payment, request=request,
                                 serializer=data_serializer.ApprovePaymentResponseSerializer)


class DisapprovePaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, AccountEditPermission]
    serializer_class = data_serializer.DisapprovePaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Disapprove Payment',
        operation_description='Disapprove Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.DisapprovePaymentResponseSerializer,
            exceptions.PaymentNotFound.code: exceptions.PaymentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        approve_payment_service = data_service.DisapprovePaymentService()
        payment = approve_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payment, request=request,
                                 serializer=data_serializer.DisapprovePaymentResponseSerializer)


class FilterPaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataReadPermission]
    serializer_class = data_serializer.FilterPaymentRequestSerializer
    pagination_class = True

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Filter Payment',
        operation_description='Filter Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.FilterPaymentResponseSerializer,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        filter_payment_service = data_service.FilterPaymentService()
        payments = filter_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payments, request=serializer.validated_data,
                                 serializer=data_serializer.FilterPaymentResponseSerializer)


class DeletePaymentView(BaseAPIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, DataEditPermission]
    serializer_class = data_serializer.DeletePaymentRequestSerializer

    @swagger_auto_schema(
        tags=['Payment'],
        operation_id='Delete Payment',
        operation_description='Delete Payment api',
        request_body=serializer_class,
        responses={
            status.HTTP_201_CREATED: None,
            0: data_serializer.DeletePaymentResponseSerializer,
            exceptions.PaymentNotFound.code: exceptions.PaymentNotFound.msg,
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        delete_payment_service = data_service.DeletePaymentService()
        payment = delete_payment_service.serve(
            request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=payment, request=request,
                                 serializer=data_serializer.DeletePaymentResponseSerializer)


class ImportOrder(BaseAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = data_serializer.ImportOrderRequestSerializer

    @swagger_auto_schema(
        tags=['Manage Call Center Report'],
        operation_id='Upload extension file',
        operation_description='Upload extension file',
        request_body=serializer_class,
        responses={
            0: data_serializer.ImportOrderResponseSerializer
        }
    )
    def post(self, request, serializer=None, cookies=None, *args, **kwargs):
        service = data_service.ImportOrderService()
        results = service.serve(request, cookies, *args, **serializer.validated_data)
        return self.get_response(results=results, request=request,
                                 serializer=data_serializer.ImportOrderResponseSerializer)
