from api.models.base import BaseModel
from django.db import models


class FBUser(BaseModel):
    uid = models.IntegerField(db_index=True, unique=True)
    name = models.CharField(max_length=1024)

    class Meta:
        db_table = 'fb_users'


class FBPage(BaseModel):
    uid = models.ForeignKey(FBUser, on_delete=models.CASCADE, null=True)
    page_id = models.CharField(max_length=64, unique=True, db_index=True)
    page_name = models.CharField(max_length=1024)
    access_token = models.CharField(max_length=1024)

    class Meta:
        db_table = 'fb_pages'


class FBPost(BaseModel):
    page = models.ForeignKey(FBPage, on_delete=models.CASCADE)
    post_id = models.CharField(max_length=64, db_index=True)
    post_created_time = models.DateTimeField(db_index=True)
    permalink_url = models.CharField(max_length=1024)
    message = models.TextField()
    likes = models.IntegerField(default=0)

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
