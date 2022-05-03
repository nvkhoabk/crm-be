import json

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.data import CrawlData
from api.services import utils


class FilterCrawlDataService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        query_set = CrawlData.objects.all()

        filters = ['source', 'phone', 'status', ]
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if value is None:
                continue
            if key not in filters:
                continue

            if key == 'source':
                query_set = query_set.filter(
                    source=value,
                )
            if key == 'status':
                query_set = query_set.filter(
                    status=value,
                )
            if key == 'phone':
                query_set = query_set.filter(
                    phone__icontains=value,
                )

        return query_set