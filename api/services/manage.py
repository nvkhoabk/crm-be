from api.common.base_service import BaseService
from api.common.cookies import Cookies
from django.contrib.auth import authenticate, login, logout
from api.models.organization import Company
from django.db import IntegrityError
from api.services.exceptions import ManageCreateCompanyDuplicated, ManageDeleteCompanyNotFound


class CreateCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            return Company.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise ManageCreateCompanyDuplicated()


class DeleteCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        id = kwargs['id']

        try:
            return Company.objects.get(
                id=id,
            ).delete()
        except Company.DoesNotExist as e:
            raise ManageDeleteCompanyNotFound()
