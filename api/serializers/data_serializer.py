import json

from api.const import ORDER_DETAIL_TYPE, DEBT_STATUS, ORDER_PAYMENT_STATUS, PAYMENT_METHOD
from api.models.data import CrawlData, Order, OrderDetail, Customer, FBPage, FBUser, Payment
from api.models.system_configuration import DataChannel
from api.serializers.base import BasePagingSerializer, BaseResponseSerializer
from api.serializers.manage_serializer import CustomerSerializer
from api.serializers.product_serializer import ProductSerializer
from api.serializers.system_configuration_serializer import DataStatusSerializer, DataSubStatusSerializer, \
    DataSourceSerializer, DataChannelSerializer
from api.utils import validate
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class CrawlDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrawlData
        fields = ['id', 'source', 'ref_link', 'uid', 'username', 'phone', 'content', 'status', 'type']


class FilterCrawlDataParamRequestSerializer(BasePagingSerializer):
    SOURCE_CHOICES = (
        ('fb', 'fb'),
        ('zalo', 'zalo'),
    )
    STATUS_CHOICES = (
        ('init', 'init'),
    )
    
    source = serializers.ChoiceField(choices=SOURCE_CHOICES, required=False)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)
    phone = serializers.CharField(required=False) 


class FilterCrawlDataRequestSerializer(BasePagingSerializer):
    filter = FilterCrawlDataParamRequestSerializer()


class FilterCrawlDataResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=CrawlDataSerializer())


class GetCrawlDataRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetCrawlDataResponseSerializer(BaseResponseSerializer):
    data = CrawlDataSerializer()


class OrderSerializer(serializers.ModelSerializer):
    def get_pic_name(self, order):
        if order.pic is None:
            return None
        return User.objects.get(pk=order.pic_id).username

    customer = CustomerSerializer()
    data_status = DataStatusSerializer()
    data_sub_status = DataSubStatusSerializer()
    data_source = DataSourceSerializer()
    data_channel = DataChannelSerializer()
    pic_name = serializers.SerializerMethodField(source='get_pic')

    class Meta:
        model = Order
        fields = ['id', 'created_date', 'price', 'debt', 'due_date', 'annual_debt', 'annual_due_date', 'pic',
                  'customer', 'shipping_code', 'shipping_fee', 'data_status', 'data_sub_status', 'debt_status',
                  'data_source', 'data_channel', 'pic_name', 'discount_value', 'discount_type', 'amount',
                  'annual_amount', 'care_notes', 'duplicated_with', 'crawl_data']


class CreateOrderRequestSerializer(serializers.Serializer):
    DEBT_STATUS_CHOICES = (
        (DEBT_STATUS.UNPAID, DEBT_STATUS.UNPAID),
        (DEBT_STATUS.UNAPPROVED, DEBT_STATUS.UNAPPROVED),
        (DEBT_STATUS.APPROVED, DEBT_STATUS.APPROVED)
    )

    company_id = serializers.IntegerField()
    created_date = serializers.DateField(required=False, allow_null=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    debt = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    annual_debt = serializers.IntegerField(required=False, allow_null=True)
    annual_due_date = serializers.DateField(required=False, allow_null=True)
    pic_id = serializers.IntegerField(required=False, allow_null=True)
    customer_id = serializers.IntegerField()
    shipping_code = serializers.CharField(max_length=1024, required=False, allow_null=True)
    shipping_fee = serializers.IntegerField(required=False, allow_null=True)
    data_status_id = serializers.IntegerField(required=False, allow_null=True)
    data_sub_status_id = serializers.IntegerField(required=False, allow_null=True)
    data_source_id = serializers.IntegerField(required=False, allow_null=True)
    data_channel_id = serializers.IntegerField(required=False, allow_null=True)
    debt_status = serializers.ChoiceField(choices=DEBT_STATUS_CHOICES, required=False, allow_null=True)


class CreateOrderResponseSerializer(BaseResponseSerializer):
    data = OrderSerializer()


class GetOrderRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetOrderResponseSerializer(BaseResponseSerializer):
    data = OrderSerializer()


class UpdateOrderRequestSerializer(serializers.Serializer):
    DEBT_STATUS_CHOICES = (
        (DEBT_STATUS.UNPAID, DEBT_STATUS.UNPAID),
        (DEBT_STATUS.UNAPPROVED, DEBT_STATUS.UNAPPROVED),
        (DEBT_STATUS.APPROVED, DEBT_STATUS.APPROVED)
    )

    id = serializers.IntegerField(help_text='Order id', required=True)
    created_date = serializers.DateField(required=False, allow_null=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    debt = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    annual_debt = serializers.IntegerField(required=False, allow_null=True)
    annual_due_date = serializers.DateField(required=False, allow_null=True)
    pic = serializers.IntegerField(required=False, allow_null=True)
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    shipping_code = serializers.CharField(max_length=1024, required=False, allow_null=True, allow_blank=True)
    shipping_fee = serializers.IntegerField(required=False, allow_null=True)
    data_status_id = serializers.IntegerField(required=False, allow_null=True)
    data_sub_status_id = serializers.IntegerField(required=False, allow_null=True)
    data_source_id = serializers.IntegerField(required=False, allow_null=True)
    data_channel_id = serializers.IntegerField(required=False, allow_null=True)
    debt_status = serializers.ChoiceField(choices=DEBT_STATUS_CHOICES, required=False, allow_null=True)
    care_notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class UpdateOrderResponseSerializer(BaseResponseSerializer):
    data = OrderSerializer()


class DataStatusFilterParamSerializer(serializers.Serializer):
    data_status_id = serializers.IntegerField()
    data_sub_status_id = serializers.IntegerField(required=False, allow_null=True)


class DataSourceFilterParamSerializer(serializers.Serializer):
    data_source_id = serializers.IntegerField()
    data_channel_id = serializers.IntegerField(required=False, allow_null=True)


class FilterOrderRequestParamSerializer(serializers.Serializer):
    DEBT_STATUS_CHOICES = (
        (DEBT_STATUS.UNPAID, DEBT_STATUS.UNPAID),
        (DEBT_STATUS.UNAPPROVED, DEBT_STATUS.UNAPPROVED),
        (DEBT_STATUS.APPROVED, DEBT_STATUS.APPROVED)
    )

    id = serializers.IntegerField(required=False, allow_null=True)
    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)
    pics = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    data_status = serializers.ListField(child=DataStatusFilterParamSerializer(), required=False, allow_null=True)
    data_source = serializers.ListField(child=DataSourceFilterParamSerializer(), required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    customer_name = serializers.CharField(required=False, allow_null=True)
    debt_status = serializers.ChoiceField(choices=DEBT_STATUS_CHOICES, required=False)
    confirmed_from_date = serializers.DateField(required=False, allow_null=True)
    confirmed_to_date = serializers.DateField(required=False, allow_null=True)
    annual_due_date_from_date = serializers.DateField(required=False, allow_null=True)
    annual_due_date_to_date = serializers.DateField(required=False, allow_null=True)


class FilterOrderRequestSerializer(BasePagingSerializer):
    filter = FilterOrderRequestParamSerializer()


class FilterOrderResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=OrderSerializer())


class DeleteOrderRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Order id')


class DeleteOrderResponseSerializer(BaseResponseSerializer):
    pass


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderDetail
        fields = ['id', 'type', 'product', 'quantity', 'price', 'annual_price', 'discount_value', 'remaining_payment_amount',
                  'total_payment_amount',
                  'paid_payment_amount', 'debt', 'due_date', 'file_attach', 'invoice', 'discount_type', 'created_at']


class CreateOrderDetailRequestSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        (ORDER_DETAIL_TYPE.NEW_BUY, ORDER_DETAIL_TYPE.NEW_BUY),
        (ORDER_DETAIL_TYPE.ANNUAL_BUY, ORDER_DETAIL_TYPE.ANNUAL_BUY),
    )

    order_id = serializers.IntegerField()
    company_id = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    product_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, allow_null=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    annual_price = serializers.IntegerField(required=False, allow_null=True)
    discount = serializers.IntegerField(required=False, allow_null=True)
    remaining_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    total_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    paid_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    debt = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    file_attach = serializers.FileField(required=False, allow_null=True)
    invoice = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class CreateOrderDetailResponseSerializer(BaseResponseSerializer):
    data = OrderDetailSerializer()


class GetOrderDetailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetOrderDetailResponseSerializer(BaseResponseSerializer):
    data = OrderDetailSerializer()


class UpdateOrderDetailRequestSerializer(serializers.Serializer):
    order_detail_id = serializers.IntegerField()
    product_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(required=False, allow_null=True)
    price = serializers.IntegerField(required=False, allow_null=True)
    annual_price = serializers.IntegerField(required=False, allow_null=True)
    discount_value = serializers.IntegerField(required=False, allow_null=True)
    discount_type = serializers.CharField(required=False, allow_null=True)
    remaining_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    total_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    paid_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    debt = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    file_attach = serializers.FileField(required=False, allow_null=True)
    invoice = serializers.CharField(required=False, allow_null=True)


class UpdateOrderDetailResponseSerializer(BaseResponseSerializer):
    data = OrderDetailSerializer()


class FilterOrderDetailRequestParamSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        (ORDER_DETAIL_TYPE.NEW_BUY, ORDER_DETAIL_TYPE.NEW_BUY),
        (ORDER_DETAIL_TYPE.ANNUAL_BUY, ORDER_DETAIL_TYPE.ANNUAL_BUY),
    )

    order_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=TYPE_CHOICES)


class FilterOrderDetailRequestSerializer(BasePagingSerializer):
    filter = FilterOrderDetailRequestParamSerializer()


class FilterOrderDetailResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=OrderDetailSerializer())


class DeleteOrderDetailRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='OrderDetail id')


class DeleteOrderDetailResponseSerializer(BaseResponseSerializer):
    pass


class FilterOrderHistoryRequestParamSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()


class FilterOrderHistoryRequestSerializer(BasePagingSerializer):
    filter = FilterOrderHistoryRequestParamSerializer()


class FilterOrderHistoryResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=OrderSerializer())


class FilterOrderDetailHistoryRequestParamSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        (ORDER_DETAIL_TYPE.NEW_BUY, ORDER_DETAIL_TYPE.NEW_BUY),
        (ORDER_DETAIL_TYPE.ANNUAL_BUY, ORDER_DETAIL_TYPE.ANNUAL_BUY),
    )

    order_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    order_detail_id = serializers.IntegerField(required=False)


class FilterOrderDetailHistoryRequestSerializer(BasePagingSerializer):
    filter = FilterOrderDetailHistoryRequestParamSerializer()


class FilterOrderDetailHistoryResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=OrderDetailSerializer())


class BulkUpdateOrderStatusRequestSerializer(serializers.Serializer):
    order_id_list = serializers.ListField(child=serializers.IntegerField())
    data_status_id = serializers.IntegerField()
    data_sub_status_id = serializers.IntegerField(allow_null=True, required=False)


class BulkUpdateOrderStatusResponseSerializer(BaseResponseSerializer):
    pass


class BulkUpdateOrderPicRequestSerializer(serializers.Serializer):
    order_id_list = serializers.ListField(child=serializers.IntegerField())
    pic_list = serializers.ListField(child=serializers.IntegerField())


class BulkUpdateOrderPicResponseSerializer(BaseResponseSerializer):
    pass


class FBPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FBPage
        fields = ['id', 'page_id', 'page_name', 'created_at', 'is_subscribed']


class FilterFBPageRequestParamSerializer(serializers.Serializer):
    page_id_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class FilterFBPageRequestSerializer(BasePagingSerializer):
    filter = FilterFBPageRequestParamSerializer()


class FilterFBPageResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=FBPageSerializer())


class DeleteFBPageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='FBPage id')


class DeleteFBPageResponseSerializer(BaseResponseSerializer):
    pass


class UpdateFBPageRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    is_subscribed = serializers.BooleanField(required=False, allow_null=True)


class UpdateFBPageResponseSerializer(BaseResponseSerializer):
    data = FBPageSerializer()


class SynchronizedFBAccount(serializers.ModelSerializer):
    class Meta:
        model = FBUser
        fields = ['id', 'name', 'picture_url']


class GetSynchronizedFBAccountRequestSerializer(serializers.Serializer):
    pass


class GetSynchronizedFBAccountResponseSerializer(BaseResponseSerializer):
    data = SynchronizedFBAccount()


class DeleteSynchronizedFBAccountRequestSerializer(serializers.Serializer):
    pass


class DeleteSynchronizedFBAccountResponseSerializer(BaseResponseSerializer):
    pass


class PaymentSerializer(serializers.ModelSerializer):

    order = OrderSerializer()

    class Meta:
        model = Payment
        fields = ['id', 'company', 'order', 'type', 'value', 'status', 'sale_note',
                  'invoice_no', 'accountant_note', 'approved_at', 'approver_id',
                  'payment_method', 'order_detail_id', 'created_at']


class CreatePaymentRequestSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        (ORDER_DETAIL_TYPE.NEW_BUY, ORDER_DETAIL_TYPE.NEW_BUY),
        (ORDER_DETAIL_TYPE.ANNUAL_BUY, ORDER_DETAIL_TYPE.ANNUAL_BUY)
    )

    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_METHOD.CASH, PAYMENT_METHOD.CASH),
        (PAYMENT_METHOD.CARD, PAYMENT_METHOD.CARD),
        (PAYMENT_METHOD.TRANSFER, PAYMENT_METHOD.TRANSFER)
    )

    company_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    order_detail_id = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)
    value = serializers.IntegerField()
    sale_note = serializers.CharField(max_length=512, allow_null=True, allow_blank=True, required=False)
    accountant_note = serializers.CharField(max_length=512, allow_null=True, allow_blank=True, required=False)
    approver_id = serializers.IntegerField(allow_null=True, required=False)
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, allow_blank=True, required=False)
    invoice_no = serializers.CharField(max_length=128, allow_null=True, allow_blank=True, required=False)


class CreatePaymentResponseSerializer(BaseResponseSerializer):
    data = PaymentSerializer()


class GetPaymentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetPaymentResponseSerializer(BaseResponseSerializer):
    data = PaymentSerializer()


class UpdatePaymentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Payment id', required=True)
    value = serializers.IntegerField()


class UpdatePaymentResponseSerializer(BaseResponseSerializer):
    data = PaymentSerializer()


class ApprovePaymentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Payment id', required=True)
    accountant_note = serializers.CharField(max_length=128, allow_null=True, allow_blank=True)

class DisapprovePaymentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Payment id', required=True)
    accountant_note = serializers.CharField(max_length=128, allow_null=True)


class ApprovePaymentResponseSerializer(BaseResponseSerializer):
    data = PaymentSerializer()

class DisapprovePaymentResponseSerializer(BaseResponseSerializer):
    data = PaymentSerializer()


class FilterPaymentRequestParamSerializer(serializers.Serializer):
    TYPE_CHOICES = (
        (ORDER_DETAIL_TYPE.NEW_BUY, ORDER_DETAIL_TYPE.NEW_BUY),
        (ORDER_DETAIL_TYPE.ANNUAL_BUY, ORDER_DETAIL_TYPE.ANNUAL_BUY)
    )
    order_id = serializers.IntegerField(required=False)
    type = serializers.ChoiceField(choices=TYPE_CHOICES, required=False)
    order = FilterOrderRequestParamSerializer(required=False)


class FilterPaymentRequestSerializer(BasePagingSerializer):
    filter = FilterPaymentRequestParamSerializer()


class FilterPaymentResponseSerializer(BaseResponseSerializer):
    data = serializers.ListField(child=PaymentSerializer())


class DeletePaymentRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text='Payment id')


class DeletePaymentResponseSerializer(BaseResponseSerializer):
    pass