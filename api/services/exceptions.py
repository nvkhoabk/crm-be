from rest_framework.exceptions import APIException


class AuthLoginInvalid(APIException):
    code = 1001
    msg = 'Not found username or password'


class AuthLogoutNotLoggedIn(APIException):
    code = 1002
    msg = 'User not loggedin'


class ManageCreateCompanyDuplicated(APIException):
    code = 2001
    msg = 'Duplicate company name'
 

class ManageDeleteCompanyNotFound(APIException):
    code = 2002
    msg = 'Not found company'
