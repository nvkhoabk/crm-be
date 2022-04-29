from api.common.base_service import BaseService
from api.models.article import Article
from api.common.cookies import Cookies
from django.shortcuts import redirect
from pyfacebook import GraphAPI
from django.conf import settings
from api.fb.page import FBPageUtil


class FBLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        api = GraphAPI(app_id=settings.FB_APP_ID, app_secret=settings.FB_APP_SECRET, oauth_flow=True)
        uri = api.get_authorization_url(redirect_uri=settings.REDIRECT_URI, scope=settings.SCOPE)
        return redirect(uri[0])
