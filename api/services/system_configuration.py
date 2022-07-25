import json

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import UserRole
from api.models.product import Product
from api.models.system_configuration import CompanyEmail, DataStatus, DataSubStatus, DataSource, DataChannel, \
    EmailSyntax, EmailTemplate, CompanyLogo
from api.services import utils
from rest_framework.exceptions import PermissionDenied
from api.services.exceptions import (CompanyEmailDuplicated, CompanyEmailNotFound,
                                     DataStatusDuplicated, DataStatusNotFound, DataSubStatusDuplicated,
                                     DataSubStatusNotFound, DataSourceDuplicated, DataSourceNotFound,
                                     DataChannelNotFound, DataChannelDuplicated, EmailSyntaxNotFound,
                                     EmailSyntaxDuplicated, EmailTemplateDuplicated, EmailTemplateNotFound,
                                     CompanyLogoDuplicated, CompanyLogoNotFound, )
from django.db import IntegrityError


class CreateCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return CompanyEmail.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise CompanyEmailDuplicated()


class GetCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return CompanyEmail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except CompanyEmail.DoesNotExist as e:
            raise CompanyEmailNotFound()


class UpdateCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                email = CompanyEmail.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                email = CompanyEmail.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('email'):
                email.email = kwargs['email']

            if kwargs.get('password'):
                email.password = kwargs['password']

            email.save()

            return email
        except CompanyEmail.DoesNotExist:
            raise CompanyEmailNotFound()
    

class FilterCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = CompanyEmail.objects.filter(company_id=user_roles.first().company_id)

        filters = ['email']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'email' and key is not None:
                query_set = query_set.filter(
                    email__icontains=value,
                )

        return query_set


class DeleteCompanyEmailService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return CompanyEmail.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except CompanyEmail.DoesNotExist as e:
            raise CompanyEmailNotFound()


class CreateDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return DataStatus.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise DataStatusDuplicated()


class GetDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return DataStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except DataStatus.DoesNotExist as e:
            raise DataStatusNotFound()


class UpdateDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                result = DataStatus.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                result = DataStatus.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                result.name = kwargs['name']

            if kwargs.get('color'):
                result.color = kwargs['color']

            if kwargs.get('index'):
                result.index = kwargs['index']

            if 'choose_by_default' in kwargs:
                result.choose_by_default = kwargs['choose_by_default']

            result.save()

            return result
        except DataStatus.DoesNotExist:
            raise DataStatusNotFound()


class FilterDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = DataStatus.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

        filters = ['name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name' and value != '' and value is not None:
                query_set = query_set.filter(
                    name__icontains=value,
                )

        return query_set.order_by('index')


class DeleteDataStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return DataStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except DataStatus.DoesNotExist as e:
            raise DataStatusNotFound()


class CreateDataSubStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            DataStatus.objects.get(pk=kwargs['data_status_id'])

            return DataSubStatus.objects.create(
                **kwargs
            )
        except DataStatus.DoesNotExist:
            raise DataStatusNotFound()
        except IntegrityError as e:
            raise DataSubStatusDuplicated()


class GetDataSubStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return DataSubStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except DataSubStatus.DoesNotExist as e:
            raise DataSubStatusNotFound()


class UpdateDataSubStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                result = DataSubStatus.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                result = DataSubStatus.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                result.name = kwargs['name']

            if kwargs.get('color'):
                result.color = kwargs['color']

            if kwargs.get('index'):
                result.index = kwargs['index']

            if 'choose_by_default' in kwargs:
                result.choose_by_default = kwargs['choose_by_default']

            result.save()

            return result
        except DataSubStatus.DoesNotExist:
            raise DataSubStatusNotFound()


class FilterDataSubStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = DataSubStatus.objects.filter(company_id=user_roles.first().company_id, deleted_at__isnull=True)

        filters = ['name', 'data_status_id']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name' and value != '' and value is not None:
                query_set = query_set.filter(
                    name__icontains=value,
                )

            if key == 'data_status_id':
                query_set = query_set.filter(
                    data_status_id=value,
                )

        return query_set.order_by('index')


class DeleteDataSubStatusService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return DataSubStatus.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except DataSubStatus.DoesNotExist as e:
            raise DataSubStatusNotFound()



class CreateDataSourceService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return DataSource.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise DataSourceDuplicated()


class GetDataSourceService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return DataSource.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except DataSource.DoesNotExist as e:
            raise DataSourceNotFound()


class UpdateDataSourceService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                result = DataSource.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                result = DataSource.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                result.name = kwargs['name']

            if 'choose_by_default' in kwargs:
                result.choose_by_default = kwargs['choose_by_default']

            result.save()

            return result
        except DataSource.DoesNotExist:
            raise DataSourceNotFound()


class FilterDataSourceService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = DataSource.objects.filter(company_id=user_roles.first().company_id)

        filters = ['name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name' and value != '' and value is not None:
                query_set = query_set.filter(
                    name__icontains=value,
                )

        return query_set


class DeleteDataSourceService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return DataSource.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except DataSource.DoesNotExist as e:
            raise DataSourceNotFound()


class CreateDataChannelService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            DataSource.objects.get(pk=kwargs['data_source_id'])

            return DataChannel.objects.create(
                **kwargs
            )
        except DataSource.DoesNotExist:
            raise DataStatusNotFound()
        except IntegrityError as e:
            raise DataChannelDuplicated()


class GetDataChannelService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return DataChannel.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except DataChannel.DoesNotExist as e:
            raise DataChannelNotFound()


class UpdateDataChannelService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                result = DataChannel.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                result = DataChannel.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('name'):
                result.name = kwargs['name']

            result.save()

            return result
        except DataChannel.DoesNotExist:
            raise DataChannelNotFound()


class FilterDataChannelService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = DataChannel.objects.filter(company_id=user_roles.first().company_id)

        filters = ['name', 'data_source_id']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'name' and value != '' and value is not None:
                query_set = query_set.filter(
                    name__icontains=value,
                )

            if key == 'data_source_id':
                query_set = query_set.filter(
                    data_source_id=value,
                )

        return query_set


class DeleteDataChannelService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return DataChannel.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except DataChannel.DoesNotExist as e:
            raise DataChannelNotFound()


class CreateEmailSyntaxService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return EmailSyntax.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise EmailSyntaxDuplicated()


class GetEmailSyntaxService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return EmailSyntax.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except EmailSyntax.DoesNotExist as e:
            raise EmailSyntaxNotFound()


class UpdateEmailSyntaxService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                syntax = EmailSyntax.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                syntax = EmailSyntax.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('code'):
                syntax.code = kwargs['code']

            if kwargs.get('column_name'):
                syntax.column_name = kwargs['column_name']

            syntax.save()

            return syntax
        except EmailSyntax.DoesNotExist:
            raise EmailSyntaxNotFound()


class FilterEmailSyntaxService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = EmailSyntax.objects.filter(company_id=user_roles.first().company_id)

        filters = ['code', 'column_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'code':
                query_set = query_set.filter(
                    code__icontains=value,
                )

            if key == 'column_name':
                query_set = query_set.filter(
                    column_name__icontains=value,
                )

        return query_set


class DeleteEmailSyntaxService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return EmailSyntax.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except EmailSyntax.DoesNotExist as e:
            raise EmailSyntaxNotFound()


class CreateEmailTemplateService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return EmailTemplate.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise EmailTemplateDuplicated()


class GetEmailTemplateService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return EmailTemplate.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            )
        except EmailTemplate.DoesNotExist as e:
            raise EmailTemplateNotFound()


class UpdateEmailTemplateService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                template = EmailTemplate.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                template = EmailTemplate.objects.get(
                    pk=kwargs.get('id'),
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('code'):
                template.code = kwargs['code']

            if kwargs.get('email_name'):
                template.email_name = kwargs['email_name']

            if kwargs.get('content'):
                template.content = kwargs['content']

            template.save()

            return template
        except EmailTemplate.DoesNotExist:
            raise EmailTemplateNotFound()


class FilterEmailTemplateService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = EmailTemplate.objects.filter(company_id=user_roles.first().company_id)

        filters = ['code', 'email_name']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'code':
                query_set = query_set.filter(
                    code__icontains=value,
                )

            if key == 'email_name':
                query_set = query_set.filter(
                    email_name__icontains=value,
                )

        return query_set


class DeleteEmailTemplateService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return EmailTemplate.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id
            ).delete()
        except EmailTemplate.DoesNotExist as e:
            raise EmailTemplateNotFound()


class CreateCompanyLogoService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if not request.user.is_superuser:
                user_roles = UserRole.objects.filter(user_id=request.user)

                if 'company_id' in kwargs and kwargs['company_id'] != user_roles.first().company_id:
                    raise PermissionDenied()

            return CompanyLogo.objects.create(
                **kwargs
            )
        except IntegrityError as e:
            raise CompanyLogoDuplicated()


class GetCompanyLogoService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }

            user_roles = UserRole.objects.filter(**filter)

            return CompanyLogo.objects.get(
                company_id=user_roles.first().company_id
            )
        except CompanyLogo.DoesNotExist as e:
            raise CompanyLogoNotFound()


class UpdateCompanyLogoService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            if request.user.is_superuser:
                logo = CompanyLogo.objects.get(
                    pk=kwargs.get('id')
                )
            else:
                filter = {
                    'user': request.user,
                    'deleted_at__isnull': True
                }
                user_roles = UserRole.objects.filter(**filter)

                logo = CompanyLogo.objects.get(
                    company_id=user_roles.first().company_id
                )

            if kwargs.get('logo'):
                logo.logo = kwargs['logo']

            logo.save()

            return logo
        except CompanyLogo.DoesNotExist:
            raise CompanyLogoNotFound()


class DeleteCompanyLogoService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            return CompanyLogo.objects.get(
                company_id=user_roles.first().company_id
            ).delete()
        except CompanyLogo.DoesNotExist as e:
            raise CompanyLogoNotFound()
