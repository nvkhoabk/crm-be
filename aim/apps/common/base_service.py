class ServiceException(Exception):
    None


class BaseService:
    exception = None
    status = None
    pagination_class = None
