from api.models.base import BaseModel
from django.db import models
from api.models.organization import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class FBUser(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    uid = models.CharField(max_length=255, db_index=True, unique=True)
    name = models.CharField(max_length=1024)
    access_token = models.CharField(max_length=4096, default='')
    expire_time = models.IntegerField(default=0)
    need_crawl = models.BooleanField(default=False)

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

    class Meta:
        db_table = 'crawl_data'


class Customer(models.Model):
    name = models.CharField(db_index=True, max_length=255)
    phone = models.CharField(db_index=True, max_length=64)
    address = models.CharField(max_length=2048, null=True)
   
    class Meta:
        db_table = 'customers'


class Data(models.Model):
    created_date = models.DateField(db_index=True)
    price = models.IntegerField(default=0)
    debt = models.IntegerField(default=0)
    due_date = models.DateField(db_index=True)
    annual_debt = models.IntegerField(default=0)
    pic = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        db_table = 'data'


class Order(BaseModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True, unique=True)
    type = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    class Meta:
        db_table = 'companies'
        unique_together = ('name', 'deleted_at',)