
class InvalidPhoneFormat:
    code = 1
    msg = 'Invalid phone format'


class DataStatusEmptyDataSubStatusNotEmpty:
    code = 2
    msg = 'Data status is empty but data sub status is not empty'


class DataStatusNotFound:
    code = 3
    msg = 'Data status is not found'


class DataSubStatusNotFound:
    code = 4
    msg = 'Data sub status is not found'


class IdIsEmpty:
    code = 5
    msg = 'Id is empty'


class IdIsNotNumeric:
    code = 6
    msg = 'Id is not numeric'


class DataSourceEmptyDataChannelNotEmpty:
    code = 7
    msg = 'Data source is empty but data channel is not empty'


class DataSourceNotFound:
    code = 8
    msg = 'Data source is not found'


class DataChannelNotFound:
    code = 9
    msg = 'Data channel is not found'


class InvalidEmailFormat:
    code = 10
    msg = 'Invalid email format'


class OrderIdEmpty:
    code = 11
    msg = 'Order id is empty'


class OrderIdIsNotNumeric:
    code = 12
    msg = 'Order id is not numeric'


class OrderNotFound:
    code = 13
    msg = 'Order is not found'


class AmountIsNotNumeric:
    code = 14
    msg = 'Amount is not numeric'


class PaymentForNoProductOrder:
    code = 15
    msg = 'Create payment for order that have no product'
