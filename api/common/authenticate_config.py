"""
Definition of authenticate config.
"""
from api.common.common import Common
from api.common.response import Response
from django.http import JsonResponse
from rest_framework import status
# from api.user.user_query import UserQuery
from api.const import Const
from django.db import connection


def authentication_staff(api_name):
    """
    Custom authentication method with argument
    :param api_name:
    :return:
    """
    def real_authentication_required(function):
        """
        Custom authenticate
        :param function:
        :return:
        """
        def wrapper(request, *args, **kw):
            """
            Custom authenticate
            :param request:
            :param args:
            :param kw:
            :return:
            """
            try:
                # Inject require object
                common = Common()
                user_query = UserQuery()
                cursor = connection.cursor()

                if 'token' in request.headers:
                    token = request.headers['token']

                    user = common.get_user_from_token(token, Const.SECRET_KEY)
                    if user is not None:
                        # Check user from staff
                        if 'phone_number' in user:
                            phone_number = user['phone_number']

                            cursor.execute(user_query.get_user_id_by_phone_number(), [phone_number])
                            user_dbs = common.dictfetchall(cursor)

                            if user_dbs is None or len(user_dbs) == 0:
                                response = Response(status=status.HTTP_403_FORBIDDEN)
                                return JsonResponse(response.__dict__, status=response.status)
                            else:
                                user_db = user_dbs[0]
                                request.COOKIES['id'] = user_db['id']
                                request.COOKIES['role_code'] = user_db['role_code']
                                request.COOKIES['group_user_code'] = user_db['group_user_code']
                                request.COOKIES['screen'] = user_db['screen']
                                return function(request, *args, **kw)
                        else:
                            response = Response(status=status.HTTP_403_FORBIDDEN)
                            return JsonResponse(response.__dict__, status=response.status)
                    else:
                        response = Response(status=status.HTTP_403_FORBIDDEN)
                        return JsonResponse(response.__dict__, status=response.status)
                else:
                    response = Response(status=status.HTTP_401_UNAUTHORIZED)
                    return JsonResponse(response.__dict__, status=response.status)
            except Exception as e:
                response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return JsonResponse(response.__dict__, status=response.status)

        return wrapper

    return real_authentication_required

def authentication_class(api_name):
    """
    Custom authentication method with argument
    :param api_name:
    :return:
    """
    def real_authentication_required(function):
        """
        Custom authenticate
        :param function:
        :return:
        """
        def wrapper(cls, request, *args, **kw):
            """
            Custom authenticate
            :param request:
            :param args:
            :param kw:
            :return:
            """
            try:
                # Inject require object
                common = Common()
                user_query = UserQuery()
                cursor = connection.cursor()

                if 'token' in request.headers:
                    token = request.headers['token']

                    user = common.get_user_from_token(token, Const.SECRET_KEY)
                    if user is not None:
                        # Check user from staff
                        if 'phone_number' in user:
                            phone_number = user['phone_number']

                            cursor.execute(user_query.get_user_id_by_phone_number(), [phone_number])
                            user_dbs = common.dictfetchall(cursor)

                            if user_dbs is None or len(user_dbs) == 0:
                                response = Response(status=status.HTTP_403_FORBIDDEN)
                                return JsonResponse(response.__dict__, status=response.status)
                            else:
                                user_db = user_dbs[0]
                                request.COOKIES['id'] = user_db['id']
                                return function(cls, request, *args, **kw)
                        else:
                            response = Response(status=status.HTTP_403_FORBIDDEN)
                            return JsonResponse(response.__dict__, status=response.status)
                    else:
                        response = Response(status=status.HTTP_403_FORBIDDEN)
                        return JsonResponse(response.__dict__, status=response.status)
                else:
                    response = Response(status=status.HTTP_401_UNAUTHORIZED)
                    return JsonResponse(response.__dict__, status=response.status)
            except Exception as e:
                response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return JsonResponse(response.__dict__, status=response.status)

        return wrapper

    return real_authentication_required