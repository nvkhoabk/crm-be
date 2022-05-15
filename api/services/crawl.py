import base64
import json

from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.fb.page import FBPageUtil
from api.models.article import Article
from api.models.data import FBComment, FBMessage, FBPage, FBPost, FBUser, ZaloOA
from api.models.organization import UserRole
from api.services import exceptions
from api.services.utils import AESCipher
from api.utils.phone import extract_phone
from Crypto.Cipher import AES
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from pyfacebook import GraphAPI
from api.zalo.zutils import ZaloPage

User = get_user_model()


class FBLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user = request.user
        api = GraphAPI(app_id=settings.FB_APP_ID,
                       app_secret=settings.FB_APP_SECRET, oauth_flow=True)

        aes = AESCipher(settings.FB_SECRET_KEY)
        api.STATE = aes.encrypt(str(user.id))

        uri = api.get_authorization_url(
            redirect_uri=settings.REDIRECT_URI, scope=settings.FB_SCOPE)
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

        response = settings.REDIRECT_URI + '?code=' + \
            kwargs.get('code') + '&state=PyFacebook#_=_'

        api = GraphAPI(app_id=settings.FB_APP_ID,
                       app_secret=settings.FB_APP_SECRET, oauth_flow=True)
        api.exchange_user_access_token(
            redirect_uri=settings.REDIRECT_URI, response=response)
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
        user.need_crawl = True
        user.save()

        pages = fb.get_pages()
        for page_info in pages:
            try:
                page = FBPage.objects.get(
                    user__uid=user.uid, page_id=page_info['id'])
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


class CrawlService(BaseService):
    def crawl_posts(self, page_id):
        page = FBPage.objects.get(page_id=page_id)
        access_token = page.access_token

        fb = FBPageUtil(access_token)
        page_info = fb.get_page_info()

        page.name = page_info['name']
        page.save()

        posts = fb.get_page_posts(page_id)
        for post in posts:
            post_obj, created = FBPost.objects.get_or_create(
                page=page,
                post_id=post['id'],
                defaults={
                    'page': page,
                    'post_id': post['id'],
                    'post_created_time': post['created_time'],
                    'message': post['message'],
                    'permalink_url': post['permalink_url'],
                },
            )

            comments = fb.get_page_comments(post['id'])
            for comment in comments:
                comment_obj, created = FBComment.objects.get_or_create(
                    post=post_obj,
                    comment_id=comment['id'],
                    defaults={
                        'post': post_obj,
                        'comment_id': comment['id'],
                        'comment_created_time': comment['created_time'],
                        'username': comment['from']['name'],
                        'user_id': comment['from']['id'],
                        'message': comment['message'],
                        'phone': extract_phone(comment['message']),
                    }
                )

    def crawl_messages(self, page_id):
        page = FBPage.objects.get(page_id=page_id)
        access_token = page.access_token

        fb = FBPageUtil(access_token)
        page_info = fb.get_page_info()

        page.name = page_info['name']
        page.save()

        messages = fb.get_page_messages()
        for message in messages:
            message_obj, created = FBMessage.objects.get_or_create(
                page=page,
                message_id=message['id'],
                defaults={
                    'page': page,
                    'message_id': message['id'],
                    'username': message['senders']['data'][0]['name'],
                    'user_id':  message['senders']['data'][0]['id'],
                    'message': json.dumps(message['messages']),
                    'phone': extract_phone(''.join(message['messages'])),
                }
            )


class ZaloLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user = request.user
        redirect_uri = settings.ZALO_REDIRECT_URI
        aes = AESCipher(settings.ZALO_SECRET_KEY)
        state = aes.encrypt(str(user.id)).decode('utf-8')

        login_url = 'https://oauth.zaloapp.com/v4/oa/permission?app_id=2252452034861651725&redirect_uri={}&state={}'.format(redirect_uri, state)
        
        return redirect(login_url)


class ZaloLoginCallBackService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        code = kwargs.get('code')
        state = kwargs.get('state')
        aes = AESCipher(settings.ZALO_SECRET_KEY)

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
        
        try:
            zalo = ZaloPage(code)
        except Exception as e:
            raise
        
        oa_info = zalo.get_info()
        
        try:
            user = ZaloOA.objects.get(oa_id=oa_info['oa_id'])
        except ZaloOA.DoesNotExist:
            user = ZaloOA.objects.create(
                oa_id=oa_info['oa_id'],
                name=oa_info['name'],
                access_token=zalo.access_token,
                company=user_roles.company,
                user=user,
            )

        user.access_token = zalo.access_token
        user.need_crawl = True
        user.save()

        return {}
 