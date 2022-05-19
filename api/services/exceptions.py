from rest_framework.exceptions import APIException


class AuthLoginInvalid(APIException):
    code = 1001
    msg = 'Not found username or password'


class AuthLogoutNotLoggedIn(APIException):
    code = 1002
    msg = 'User not loggedin'


class ManageParamDuplicated(APIException):
    code = 2000
    msg = 'Duplicate param name'


class ManageParamNotFound(APIException):
    code = 2001
    msg = 'Not found param'


class ManagePackageDuplicated(APIException):
    code = 2010
    msg = 'Duplicate param name'


class ManagePackageNotFound(APIException):
    code = 2011
    msg = 'Not found package'


class ManageCompanyDuplicated(APIException):
    code = 2020
    msg = 'Duplicate company name'
 

class ManageCompanyNotFound(APIException):
    code = 2021
    msg = 'Not found company'


class ManageDepartmentDuplicated(APIException):
    code = 2030
    msg = 'Duplicated department'


class ManageDepartmentNotFound(APIException):
    code = 2031
    msg = 'Not found department'


class ManageDepartmentNotEmpty(APIException):
    code = 2032
    msg = 'Department is not empty'


class ManageRoleDuplicated(APIException):
    code = 2040
    msg = 'Duplicate role'


class ManageRoleNotFound(APIException):
    code = 2041
    msg = 'Not found role'


class ManagePermissionDuplicated(APIException):
    code = 2050
    msg = 'Duplicate permission'


class ManagePermissionNotFound(APIException):
    code = 2051
    msg = 'Permission not found'


class ManageUserDuplicated(APIException):
    code = 2060
    msg = 'User duplicated'


class ManageUserNotFound(APIException):
    code = 2061
    msg = 'User not found'


class ProductNotFound(APIException):
    code = 3001
    msg = 'Product not found'


class ProductDuplicated(APIException):
    code = 3002
    msg = 'Duplicate product'


class CallCenterDuplicated(APIException):
    code = 3003
    msg = 'Duplicate call center'


class CallCenterNotFound(APIException):
    code = 3003
    msg = 'Call center not found'


class SipCredentialError(APIException):
    code = 3004
    msg = 'Sip username or password is wrong'


class SipAPIError(APIException):
    code = 3005
    msg = 'Sip api error'


class CallAgentNotFound(APIException):
    code = 3006
    msg = 'Call agent not found'


class AgentRegisterNotFound(APIException):
    code = 3007
    msg = 'Agent Register not found'


class CallLogNotFound(APIException):
    code = 3007
    msg = 'Call log not found'


class ManageCustomerDuplicated(APIException):
    code = 3008
    msg = 'Duplicate param name'


class ManageCustomerNotFound(APIException):
    code = 3009
    msg = 'Not found param'