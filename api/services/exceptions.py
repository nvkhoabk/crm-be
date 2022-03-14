from rest_framework.exceptions import APIException


class AuthLoginInvalid(APIException):
    code = 1001
    msg = 'Not found username or password'


class AuthLogoutNotLoggedIn(APIException):
    code = 1002
    msg = 'Not found username or password'
