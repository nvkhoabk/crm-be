from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User


class CRMBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        pass
