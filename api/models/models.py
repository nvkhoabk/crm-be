from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from api.models.manager import CRMUserManager


class CRMUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), max_length=50, unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CRMUserManager()
    
    def __str__(self):
        return self.email
