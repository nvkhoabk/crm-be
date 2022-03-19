from rest_framework.exceptions import APIException


class AuthLoginInvalid(APIException):
    code = 1001
    msg = 'Not found username or password'


class AuthLogoutNotLoggedIn(APIException):
    code = 1002
    msg = 'User not loggedin'


class ManageCreateParamDuplicated(APIException):
    code = 2001
    msg = 'Duplicate param name'


class ManageCreatePackageDuplicated(APIException):
    code = 2010
    msg = 'Duplicate param name'


class ManageDeletePackageNotFound(APIException):
    code = 2011
    msg = 'Not found package'


class ManageCreateCompanyDuplicated(APIException):
    code = 2020
    msg = 'Duplicate company name'
 

class ManageCompanyNotFound(APIException):
    code = 2021
    msg = 'Not found company'


class ManageDepartmentNotFound(APIException):
    code = 2031
    msg = 'Not found department'
