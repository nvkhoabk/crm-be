"""
Definition of response common.
"""
from django.http import JsonResponse


class Response:
    data = None
    mess = None
    status = None
    
    class STATUS_CODE:
        SUCCESS = 0
        SERVER_ERROR = 1
        BAD_REQUEST = 2

    class STATUS_MSG:
        pass
        
    def __init__(self, **kwargs):
        self.data = kwargs.get("data")
        self.msg = kwargs.get("msg")
        self.status = kwargs.get("status")

    @classmethod
    def success(cls, data):
        return JsonResponse({
            'code': cls.STATUS_CODE.SUCCESS,
            'msg': 'success',
            'data': data,
        })

    @classmethod
    def bad_request(cls, msg, data):
        return JsonResponse({
            'code': cls.STATUS_CODE.BAD_REQUEST,
            'msg': msg,
            'data': data,
        })

    @classmethod
    def server_error(cls, msg, data):
        return JsonResponse({
            'code': cls.STATUS_CODE.SERVER_ERROR,
            'msg': msg,
            'data': data,
        })
