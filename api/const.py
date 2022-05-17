"""
Definition of Const.
"""


class Const:
    # Secret key
    SECRET_KEY = "Y@1Z!F5Q!W6D!@K7ZS##0MR*&6N@#R4R$!P1EN3X!C8&&EB"

    # Role admin system
    ROLE_ADMIN_SYSTEM = "ADMIN"

    # Group admin system
    GROUP_ADMIN_SYSTEM = "ADMIN"

    # File path
    FILE_ROOT = "files/"

    # Sip server
    SIP_SERVER = "wss://vnsale.siptrunk.vn:58089/ws"


class ASSET_STATUS:
    NEW = 'NEW'
    CLOSED = 'CLOSED'
    OWNING = 'OWNING'


class MODULES:
    COMPANY_MANAGEMENT = 'COMPANY_MANAGEMENT'
    ADMIN_MANAGEMENT = 'ADMIN_MANAGEMENT'
    USER_MANAGEMENT = 'USER_MANAGEMENT'
    MARKETING = 'MARKETING'
    DATA_MANAGEMENT = 'DATA_MANAGEMENT'
    PRODUCT_AND_WAREHOUSE = 'PRODUCT_AND_WAREHOUSE'
    ACCOUNTING = 'ACCOUNTING'
    SYSTEM_CONFIGURATION = 'SYSTEM_CONFIGURATION'
    REPORT = 'REPORT'


class CALL_DIRECTION:
    INCOMING = 'incoming'
    OUTGOING = 'outgoing'

