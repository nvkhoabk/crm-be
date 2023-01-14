from api.models.base import BaseModel
from django.db import models
from django.contrib.auth import get_user_model

from api.models.organization import Company

User = get_user_model()

class Notification(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=256)
    content = models.CharField(max_length=1024)
    unread = models.BooleanField(default=True)

    class Meta:
        db_table = 'notifications'
        index_together = ('company', 'user', 'deleted_at')
