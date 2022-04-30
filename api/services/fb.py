from api.common.base_service import BaseService
from api.models.article import Article
from api.common.cookies import Cookies
from django.shortcuts import redirect
from pyfacebook import GraphAPI
from api.models.fbdata import FBUser, FBPage
from django.conf import settings
from api.fb.page import FBPageUtil
import base64
from Crypto.Cipher import AES
from api.services.utils import AESCipher
from api.services import exceptions
from django.contrib.auth import get_user_model
from api.models.organization import UserRole

User = get_user_model()


class FBLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user = request.user
        api = GraphAPI(app_id=settings.FB_APP_ID, app_secret=settings.FB_APP_SECRET, oauth_flow=True)

        aes = AESCipher(settings.FB_SECRET_KEY)
        api.STATE = aes.encrypt(str(user.id))

        uri = api.get_authorization_url(redirect_uri=settings.REDIRECT_URI, scope=settings.FB_SCOPE)
        return redirect(uri[0])


class FBLoginCallBackService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        state = kwargs.get('state')
        aes = AESCipher(settings.FB_SECRET_KEY)
     
        try:
            uid = int(aes.decrypt(state))
            if uid == 0:
                raise
            user = User.objects.get(id=uid)
            user_roles = UserRole.objects.filter(
                user__id=uid
            ).first()
            
            if not user_roles:
                raise
            
        except:
            raise
            
            
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
                company=user_roles.company,
                user=user,
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
                    company=user_roles.company,
                    page_id=page_info['id'],
                    page_name=page_info['name'],
                    access_token=page_info['access_token'],
                    expire_time=0,
                )

        return {}
