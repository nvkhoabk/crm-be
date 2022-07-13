import json

from api.const import ORDER_DETAIL_TYPE, DEBT_STATUS
from api.models.data import CrawlData, Order, OrderDetail, Customer
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
        fields = ['id', 'source', 'ref_link', 'uid', 'username', 'phone', 'content', 'status', ]


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
    product = ProductSerializer()
    pic_name = serializers.SerializerMethodField(source='get_pic')

    class Meta:
        model = Order
        fields = ['id', 'created_date', 'price', 'debt', 'due_date', 'annual_debt', 'annual_due_date', 'pic',
                  'customer', 'shipping_code', 'shipping_fee', 'data_status', 'data_sub_status', 'debt_status',
                  'data_source', 'data_channel', 'pic_name']


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
    pic = serializers.IntegerField(required=False, allow_null=True)
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
    shipping_code = serializers.CharField(max_length=1024, required=False, allow_null=True)
    shipping_fee = serializers.IntegerField(required=False, allow_null=True)
    data_status_id = serializers.IntegerField(required=False, allow_null=True)
    data_sub_status_id = serializers.IntegerField(required=False, allow_null=True)
    data_source_id = serializers.IntegerField(required=False, allow_null=True)
    data_channel_id = serializers.IntegerField(required=False, allow_null=True)
    debt_status = serializers.ChoiceField(choices=DEBT_STATUS_CHOICES, required=False, allow_null=True)


class UpdateOrderResponseSerializer(BaseResponseSerializer):
    data = OrderSerializer()


class DataStatusFilterParamSerializer(serializers.Serializer):
    data_status_id = serializers.IntegerField()
    data_sub_status_id = serializers.IntegerField()


class DataSourceFilterParamSerializer(serializers.Serializer):
    data_source_id = serializers.IntegerField()
    data_channel_id = serializers.IntegerField()


class FilterOrderRequestParamSerializer(serializers.Serializer):
    DEBT_STATUS_CHOICES = (
        (DEBT_STATUS.UNPAID, DEBT_STATUS.UNPAID),
        (DEBT_STATUS.UNAPPROVED, DEBT_STATUS.UNAPPROVED),
        (DEBT_STATUS.APPROVED, DEBT_STATUS.APPROVED)
    )

    from_date = serializers.DateField(required=False, allow_null=True)
    to_date = serializers.DateField(required=False, allow_null=True)
    pics = serializers.ListField(child=serializers.IntegerField(), required=False, allow_null=True)
    data_status = serializers.ListField(child=DataStatusFilterParamSerializer(), required=False, allow_null=True)
    data_source = serializers.ListField(child=DataSourceFilterParamSerializer(), required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)
    customer_name = serializers.CharField(required=False, allow_null=True)
    debt_status = serializers.ChoiceField(choices=DEBT_STATUS_CHOICES, required=False)


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
    order = OrderSerializer()
    class Meta:
        model = OrderDetail
        fields = ['id', 'order', 'type', 'product', 'quantity', 'price', 'discount', 'remaining_payment_amount',
                  'paid_payment_amount', 'debt', 'due_date', 'file_attach', 'invoice']


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
    discount = serializers.IntegerField(required=False, allow_null=True)
    remaining_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    paid_payment_amount = serializers.IntegerField(required=False, allow_null=True)
    debt = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    file_attach = serializers.FileField(required=False, allow_null=True)
    invoice = serializers.CharField(required=False, allow_null=True)


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
    discount = serializers.IntegerField(required=False, allow_null=True)
    remaining_payment_amount = serializers.IntegerField(required=False, allow_null=True)
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