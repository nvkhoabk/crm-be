from api.common.base_service import BaseService
from api.models.article import Article
from api.common.cookies import Cookies
from django.shortcuts import redirect
from pyfacebook import GraphAPI
from api.models.fbdata import FBUser, FBPage
from django.conf import settings
from api.fb.page import FBPageUtil


class FBLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        api = GraphAPI(app_id=settings.FB_APP_ID, app_secret=settings.FB_APP_SECRET, oauth_flow=True)
        uri = api.get_authorization_url(redirect_uri=settings.REDIRECT_URI, scope=settings.FB_SCOPE)
        return redirect(uri[0])


class FBLoginCallBackService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        response = settings.REDIRECT_URI + '?code=' + kwargs.get('code') + '&state=PyFacebook#_=_'

        api = GraphAPI(app_id=settings.FB_APP_ID, app_secret=settings.FB_APP_SECRET, oauth_flow=True)
        api.exchange_user_access_token(redirect_uri=settings.REDIRECT_URI, response=response)
        data = api.exchange_long_lived_user_access_token()
        
        fb = FBPageUtil(api.access_token)
        user_info = fb.get_user_info()
        
        try:
            user = FBUser.objects.get(uid=user_info['id'])
        except FBUser.DoesNotExist:
            user = FBUser.objects.create(
                uid=user_info['id'],
                name=user_info['name'],
            )
        user.access_token = api.access_token
        user.save()
        
        pages = fb.get_pages()
        for page_info in pages:
            try:
                page = FBPage.objects.get(user__uid=user.uid, page_id=page_info['id'])
                page.access_token = page_info['access_token']
                page.name = page_info['name']
                page.save()
            except FBPage.DoesNotExist:
                page = FBPage.objects.create(
                    user=user,
                    page_id=page_info['id'],
                    page_name=page_info['name'],
                    access_token=page_info['access_token'],
                    expire_time=0,
                )

        return {}
