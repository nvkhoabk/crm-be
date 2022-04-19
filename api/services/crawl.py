import json
from api.common.base_service import BaseService
from api.fb.page import FBPageUtil
from api.models.fbdata import FBComment, FBPage, FBPost, FBMessage
from api.utils.phone import extract_phone


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
        