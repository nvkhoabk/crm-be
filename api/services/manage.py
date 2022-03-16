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


class UpdateCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            Company.objects.get(pk=kwargs['id'])
        except Company.DoesNotExist:
            raise ManageDeleteCompanyNotFound()
        
        try:
            Company.objects.filter(pk=kwargs['id']).update(**kwargs)            
        except IntegrityError as e:
            raise ManageCreateCompanyDuplicated()
 
        return Company.objects.get(pk=kwargs['id'])


class DeleteCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        id = kwargs['id']

        try:
            return Company.objects.get(
                id=id,
            ).delete()
        except Company.DoesNotExist as e:
            raise ManageDeleteCompanyNotFound()


class FilterCompanyService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = Company.objects.all()
        
        filters = ['name', 'type', 'owner', 'phone']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue
            
            if key == 'name':
                query_set = query_set.filter(
                    name__icontains=value,
                )
            if key == 'type':
                query_set = query_set.filter(
                    type__icontains=value,
                )
            if key == 'owner':
                query_set = query_set.filter(
                    owner__icontains=value,
                )
            if key == 'phone':
                query_set = query_set.filter(
                    phone__icontains=value,
                )
            
        return query_set
