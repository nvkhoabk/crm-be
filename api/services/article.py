from api.common.base_service import BaseService
from api.models import Article
from api.common.cookies import Cookies


class ArticleCreateService(BaseService):
    def serve(self, cookies: Cookies, *args, **kwargs):
        return Article.objects.create(**kwargs)
