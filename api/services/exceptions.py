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


class ManageCustomerDuplicated(APIException):
    code = 3008
    msg = 'Duplicate param name'


class ManageCustomerNotFound(APIException):
    code = 3009
    msg = 'Not found param'


class CallCenterPaymentNotDue(APIException):
    code = 3010
    msg = 'Call center payment is not due'


class CallLogNotFound(APIException):
    code = 3011
    msg = 'Call log not found'


class ReportNotFound(APIException):
    code = 3012
    msg = 'Report does not exists'


class NumberAgentRegisterNotMatch(APIException):
    code = 3013
    msg = 'Number agent register not match'


class CompanyEmailDuplicated(APIException):
    code = 4001
    msg = 'Duplicated email'


class CompanyEmailNotFound(APIException):
    code = 4002
    msg = 'Email not found'


class DataStatusDuplicated(APIException):
    code = 4003
    msg = 'Duplicated data status'


class DataStatusNotFound(APIException):
    code = 4004
    msg = 'Data status not found'


class DataSubStatusDuplicated(APIException):
    code = 4005
    msg = 'Duplicated data sub status'


class DataSubStatusNotFound(APIException):
    code = 4006
    msg = 'Data sub status not found'


class DataSourceDuplicated(APIException):
    code = 4007
    msg = 'Duplicated data source'


class DataSourceNotFound(APIException):
    code = 4008
    msg = 'Data source not found'


class DataChannelDuplicated(APIException):
    code = 4009
    msg = 'Duplicated data channel'


class DataChannelNotFound(APIException):
    code = 4010
    msg = 'Data channel not found'


class EmailSyntaxDuplicated(APIException):
    code = 4011
    msg = 'Duplicated email syntax'


class EmailSyntaxNotFound(APIException):
    code = 4012
    msg = 'Email syntax not found'


class EmailTemplateDuplicated(APIException):
    code = 4013
    msg = 'Duplicated email template'


class EmailTemplateNotFound(APIException):
    code = 4014
    msg = 'Email template not found'


class CompanyLogoDuplicated(APIException):
    code = 4013
    msg = 'Logo is already set'


class CompanyLogoNotFound(APIException):
    code = 4014
    msg = 'Logo is not found'


class OrderDuplicated(APIException):
    code = 5001
    msg = 'Order is duplicated'


class OrderNotFound(APIException):
    code = 5002
    msg = 'Order is not found'


class OrderDetailDuplicated(APIException):
    code = 5003
    msg = 'Order detail is duplicated'


class OrderDetailNotFound(APIException):
    code = 5004
    msg = 'Order detail is not found'


class FBPageNotFound(APIException):
    code = 5005
    msg = 'FBPage is not found'


class FBUserNotExisted(APIException):
    code = 5006
    msg = 'FBUser is not existed'


class PaymentNotFound(APIException):
    code = 5007
    msg = 'Payment is not found'


class CrawlDataNotFound(APIException):
    code = 5008
    msg = 'CrawlData is not found'


class ImportRecordNotFound(APIException):
    code = 5009
    msg = 'ImportRecord not found'


class PaymentForNoProductOrder(APIException):
    code = 5007
    msg = 'Payment for not product order'


class PaymentMoreThanAmount(APIException):
    code = 5008
    msg = 'Payment more than amount'


class DeleteApprovedOrderDetail(APIException):
    code = 5009
    msg = 'Cannot delete order detail when payment has been approved'


class ZaloOAAPIHasNoPermission(APIException):
    code = 6001
    msg = 'Zalo OA need buy another package, see details: https://developers.zalo.me/docs/api/official-account-api/phu-luc/official-account-access-token-post-4307'


class NotificationNotFound(APIException):
    code = 7001
    msg = 'Notification not found'


class TrialExpired(APIException):
    code = 8001
    msg = 'Trial expired'


class MainPhoneNumberDuplicated(APIException):
    code = 9001
    msg = 'main phone number is duplicated'


class MainPhoneNumberNotFound(APIException):
    code = 9002
    msg = 'main phone number is not found'


class ProviderDuplicated(APIException):
    code = 9003
    msg = 'provider is duplicated'


class ProviderNotFound(APIException):
    code = 9004
    msg = 'provider is not found'


class LegalDuplicated(APIException):
    code = 9005
    msg = 'legal is duplicated'


class LegalNotFound(APIException):
    code = 9006
    msg = 'legal is not found'


class PhoneNumberClientDuplicated(APIException):
    code = 9007
    msg = 'PhoneNumberClient is duplicated'


class PhoneNumberClientNotFound(APIException):
    code = 9008
    msg = 'PhoneNumberClient is not found'


class PhoneNumberStatusDuplicated(APIException):
    code = 9009
    msg = 'PhoneNumberStatus is duplicated'


class PhoneNumberStatusNotFound(APIException):
    code = 9010
    msg = 'PhoneNumberStatus is not found'


class PhoneNumberDuplicated(APIException):
    code = 9011
    msg = 'PhoneNumber is duplicated'


class PhoneNumberNotFound(APIException):
    code = 9012
    msg = 'PhoneNumber is not found'


class PhoneNumberMonthlyFeeDuplicated(APIException):
    code = 9013
    msg = 'PhoneNumberMonthlyFee is duplicated'


class PhoneNumberMonthlyFeeNotFound(APIException):
    code = 9014
    msg = 'PhoneNumberMonthlyFee is not found'


class PhoneNumberActivityDuplicated(APIException):
    code = 9015
    msg = 'PhoneNumberActivity is duplicated'


class PhoneNumberActivityNotFound(APIException):
    code = 9016
    msg = 'PhoneNumberActivity is not found'


class InvalidInpputDate(APIException):
    code = 9017
    msg = 'InvalidInpputDate'


class InvalidPhoneNumberStatus(APIException):
    code = 10001
    msg = 'InvalidPhoneNumberStatus'
