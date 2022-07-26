from api.models.base import BaseModel
from django.db import models
from api.models.organization import Company
from django.contrib.auth import get_user_model

from api.models.product import Product
from api.models.system_configuration import DataStatus, DataSubStatus, DataSource, DataChannel

User = get_user_model()


class FBUser(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    uid = models.CharField(max_length=255, db_index=True, unique=True)
    name = models.CharField(max_length=1024)
    access_token = models.CharField(max_length=4096, default='')
    expire_time = models.IntegerField(default=0)
    need_crawl = models.BooleanField(default=False)
    picture_url = models.TextField(default='')

    class Meta:
        db_table = 'fb_users'


class FBPage(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(FBUser, on_delete=models.CASCADE, null=True)
    page_id = models.CharField(max_length=64, unique=True, db_index=True)
    page_name = models.CharField(max_length=1024)
    access_token = models.CharField(max_length=1024)
    expire_time = models.IntegerField(default=0)
    last_check_time = models.IntegerField(default=0)
    is_subscribed = models.BooleanField(default=True)

    class Meta:
        db_table = 'fb_pages'


class FBPost(BaseModel):
    page = models.ForeignKey(FBPage, on_delete=models.CASCADE)
    post_id = models.CharField(max_length=64, db_index=True)
    post_created_time = models.DateTimeField(db_index=True)
    permalink_url = models.CharField(max_length=1024)
    message = models.TextField()
    likes = models.IntegerField(default=0)
    last_check_time = models.IntegerField(default=True)

    class Meta:
        db_table = 'fb_posts'
        unique_together = ('page_id', 'post_id',)


class FBComment(BaseModel):
    post = models.ForeignKey(FBPost, on_delete=models.CASCADE)
    comment_id = models.CharField(max_length=64, db_index=True)
    comment_created_time = models.DateTimeField()
    username = models.CharField(max_length=1024)
    user_id = models.CharField(max_length=64)
    message = models.TextField()
    phone = models.CharField(max_length=64, default='', null=True) 
    last_check_time = models.IntegerField(default=True)

    class Meta:
        db_table = 'fb_comments'


class FBMessage(BaseModel):
    page = models.ForeignKey(FBPage, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=64, db_index=True)
    username = models.CharField(max_length=1024)
    user_id = models.CharField(max_length=64)
    message = models.TextField()
    phone = models.CharField(max_length=64, default='', null=True) 

    class Meta:
        db_table = 'fb_messages'


class ZaloOA(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    access_token = models.CharField(max_length=4096, default='')
    oa_id = models.CharField(max_length=64, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    need_crawl = models.BooleanField(default=False)
    last_check_time = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        db_table = 'zalo_oas'
     

class ZaloMessage(BaseModel):
    oa = models.ForeignKey(ZaloOA, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=64, db_index=True)
    user_id = models.CharField(max_length=64)
    message = models.TextField()
    phone = models.CharField(max_length=64, default='', null=True) 

    class Meta:
        db_table = 'zalo_messages'


class CrawlData(BaseModel):
    SOURCE_CHOICES = (
        ('fb', 'fb'),
        ('zalo', 'zalo'),
    )
    STATUS_CHOICES = (
        ('init', 'init'),
    )

    TYPE_POST = 'post'
    TYPE_MSG = 'msg'
    
    TYPE_CHOICES = (
        (TYPE_POST, TYPE_POST),
        (TYPE_MSG, TYPE_MSG),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    source = models.CharField(db_index=True, max_length=64, choices=SOURCE_CHOICES, default='fb')
    type = models.CharField(db_index=True, max_length=64, choices=TYPE_CHOICES, default=TYPE_POST)
    object_id = models.CharField(db_index=True, max_length=64)
    ref_link = models.CharField(max_length=2048, default='')
    uid = models.CharField(db_index=True, max_length=64, default='')
    username = models.CharField(max_length=1024, default='')
    phone = models.CharField(max_length=64, default='')
    content = models.TextField()
    status = models.CharField(db_index=True, max_length=64, choices=STATUS_CHOICES, default='init')
    last_check_time_int = models.IntegerField(default=0)
    post_message = models.TextField(default='')
    post_picture = models.TextField(default='')

    class Meta:
        db_table = 'crawl_data'


class CrawlObject(BaseModel):
    SOURCE_CHOICES = (
        ('fb', 'fb'),
        ('zalo', 'zalo'),
    )
    TYPE_POST = 'post'
    TYPE_MSG = 'msg'

    TYPE_CHOICES = (
        (TYPE_POST, TYPE_POST),
        (TYPE_MSG, TYPE_MSG),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    object_id = models.CharField(db_index=True, max_length=64)
    source = models.CharField(db_index=True, max_length=64, choices=SOURCE_CHOICES, default='fb')
    type = models.CharField(db_index=True, max_length=64, choices=TYPE_CHOICES, default=TYPE_POST)
    last_check_time_int = models.IntegerField(default=0)

    class Meta:
        db_table = 'crawl_objects'


class Customer(models.Model):
    name = models.CharField(db_index=True, max_length=255)
    phone = models.CharField(db_index=True, max_length=64)
    address = models.CharField(max_length=2048, null=True)
   
    class Meta:
        db_table = 'customers'


class Order(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_date = models.DateField(db_index=True, null=True)
    price = models.IntegerField(default=0)
    debt = models.IntegerField(default=0)
    due_date = models.DateField(db_index=True, null=True)
    annual_debt = models.IntegerField(default=0)
    annual_due_date = models.DateField(db_index=True, null=True)
    pic = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_column='pic_id')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_code = models.CharField(max_length=1024, default='', null=True)
    shipping_fee = models.BigIntegerField(default=0)
    data_status = models.ForeignKey(DataStatus, null=True, on_delete=models.SET_NULL)
    data_sub_status = models.ForeignKey(DataSubStatus, null=True, on_delete=models.SET_NULL)
    debt_status = models.CharField(max_length=128, null=True)
    data_source = models.ForeignKey(DataSource, null=True, on_delete=models.SET_NULL)
    data_channel = models.ForeignKey(DataChannel, null=True, on_delete=models.SET_NULL)
    crawl_data = models.ForeignKey(CrawlData, null=True, on_delete=models.SET_NULL)
    discount_value = models.BigIntegerField(default=0)
    discount_type = models.CharField(max_length=64, default='')
    amount = models.IntegerField(default=0)
    annual_amount = models.IntegerField(default=0)


    class Meta:
        db_table = 'orders'


class OrderDetail(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    type = models.CharField(max_length=64)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(null=True)
    price = models.BigIntegerField(null=True)
    remaining_payment_amount = models.BigIntegerField(null=True)
    paid_payment_amount = models.BigIntegerField(null=True)
    debt = models.BigIntegerField(null=True)
    due_date = models.DateField(null=True)
    file_attach = models.FileField(null=True)
    invoice = models.TextField(null=True)
    discount_value = models.BigIntegerField(default=0)
    discount_type = models.CharField(max_length=64, default='')


    class Meta:
        db_table = 'order_details'
        index_together = ('order', 'type')


class OrderHistory(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_index=True)
    created_date = models.DateField(null=True)
    price = models.IntegerField(default=0)
    debt = models.IntegerField(default=0)
    due_date = models.DateField(null=True)
    annual_debt = models.IntegerField(default=0)
    annual_due_date = models.DateField(null=True)
    pic = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_code = models.CharField(max_length=1024, default='', null=True)
    shipping_fee = models.BigIntegerField(default=0)
    data_status = models.ForeignKey(DataStatus, null=True, on_delete=models.SET_NULL)
    data_sub_status = models.ForeignKey(DataSubStatus, null=True, on_delete=models.SET_NULL)
    debt_status = models.CharField(max_length=128, null=True)
    data_source = models.ForeignKey(DataSource, null=True, on_delete=models.SET_NULL)
    data_channel = models.ForeignKey(DataChannel, null=True, on_delete=models.SET_NULL)
    crawl_data = models.ForeignKey(CrawlData, null=True, on_delete=models.SET_NULL)
    discount_value = models.BigIntegerField(default=0)
    discount_type = models.CharField(max_length=64, default='')
    amount = models.IntegerField(default=0)
    annual_amount = models.IntegerField(default=0)

    class Meta:
        db_table = 'order_histories'


class OrderDetailHistory(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_index=True)
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, db_index=True)
    type = models.CharField(max_length=64)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(null=True)
    price = models.BigIntegerField(null=True)
    remaining_payment_amount = models.BigIntegerField(null=True)
    paid_payment_amount = models.BigIntegerField(null=True)
    debt = models.BigIntegerField(null=True)
    due_date = models.DateField(null=True)
    file_attach = models.FileField(null=True)
    invoice = models.TextField(null=True)
    discount_value = models.BigIntegerField(default=0)
    discount_type = models.CharField(max_length=64, default='')

    class Meta:
        db_table = 'order_detail_histories'


class AnnualOrder(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'annual_orders'


class Payment(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_payments', db_index=True)
    type = models.CharField(max_length=64, db_index=True)
    value = models.BigIntegerField()
    status = models.CharField(max_length=64, db_index=True)

    class Meta:
        db_table = 'payments'
        index_together = [
            ['company', 'order', 'deleted_at'],
            ['company', 'type', 'deleted_at'],
            ['company', 'status', 'deleted_at'],
        ]
