from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from api.models.manager import CRMUserManager


class CRMUser(AbstractUser):
    pass
