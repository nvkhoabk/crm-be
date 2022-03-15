from rest_framework.views import exception_handler
from rest_framework.views import set_rollback, Http404, PermissionDenied, exceptions, Response
from rest_framework import serializers


def crm_exception_handler(exc, context):
    if isinstance(exc, Http404):
        return exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        return exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc, serializers.ValidationError):
            if isinstance(exc.detail, (list, dict)):
                data = exc.detail
            else:
                data = {'detail': exc.detail}
        else:
            data = {
                'code': exc.code,
                'msg': exc.msg,
            }

        set_rollback()
        return Response(data, headers=headers)

    return None
