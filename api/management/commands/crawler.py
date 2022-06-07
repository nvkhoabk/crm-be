import os
import sys
import time
from api.utils.phone import extract_phone
from api.fb.page import FBPageUtil
from api.management.commands.daemon import Daemon
from api.models.data import CrawlData, ZaloOA, FBUser, FBPage
from api.zalo.zutils import ZaloPage
from django.core.management.base import BaseCommand
from django.db.models import F
from pyfacebook import FacebookApi
from django.utils import timezone
import time


class FBCrawler(Daemon):
    BULK_SIZE = 10
    TIME = 5
    START_TIME = 1651289937

    def __init__(self, pidfile, shard=1, id=0):
        pidfile = '{}_{}'.format(pidfile, id)
        self.shard = shard
        self.id = id
        super().__init__(pidfile)

    def crawl_posts(self, page):
        api = FacebookApi(access_token=page.access_token)
        fb = FBPageUtil(access_token=page.access_token)

        offset = 0
        limit = 10
    
        while True:
            posts = fb.get_page_posts(page.page_id, offset, limit)
            offset = offset + limit

            if len(posts) == 0:
                break
    
            for post in posts:
                c_offset = 0
                c_limit = 10
                while True:     
                    comments = fb.get_page_comments(post['id'], c_offset, c_limit)
                    if len(comments) == 0:
                        break
            
                    c_offset = c_offset + c_limit

                    for comment in comments: 
                        if CrawlData.objects.filter(object_id=comment['id']).first():
                            continue
                
                        if not extract_phone(comment['message']):
                            continue

                        CrawlData.objects.create(
                            source='fb',
                            object_id=comment['id'],
                            type=CrawlData.TYPE_POST,
                            ref_link=post['permalink_url'],
                            uid=comment['from']['id'],
                            username=comment['from']['name'],
                            content=comment['message'],
                            phone=extract_phone(comment['message']),
                        )
        
    def crawl_messages(self, page):
        api = FacebookApi(access_token=page.access_token)
        fb = FBPageUtil(access_token=page.access_token)

        offset = 0
        limit = 10
        while True:
            messages = fb.get_page_messages(page.page_id, offset, limit)
            if len(messages) == 0:
                break
            
            offset = offset + limit
            
            for message in messages:
                all_messages = ' '.join(message['messages'])
                
                if CrawlData.objects.filter(object_id=message['id']).first():
                    continue
            
                if not extract_phone(all_messages):
                    continue

                CrawlData.objects.create(
                    source='fb',
                    object_id=message['id'],
                    type=CrawlData.TYPE_MSG,
                    uid=message['senders']['data'][0]['id'],
                    username=message['senders']['data'][0]['id'],
                    content=all_messages,
                    phone=extract_phone(all_messages),
                )

    def do_crawl(self):
        users = FBUser.objects.annotate(id_mod=F('id') % self.shard).filter(
            id_mod=self.id,
            need_crawl=True,
        )[:self.BULK_SIZE]

        for user in users:
            fbpages = FBPage.objects.filter(
                user=user
            )
            for page in fbpages:
                self.crawl_posts(page)
                self.crawl_messages(page)


    def run(self):
        while True:
            try:
                self.do_crawl() 
            except Exception as e:
                pass
            finally:
                time.sleep(self.TIME)


class ZaloCrawler(Daemon):
    BULK_SIZE = 10
    TIME = 5
    START_TIME = 1651289937

    def __init__(self, pidfile, shard=1, id=0):
        pidfile = '{}_{}'.format(pidfile, id)
        self.shard = shard
        self.id = id
        super().__init__(pidfile)
      
    def crawl_messages(self, oa):
        zalo = ZaloPage(access_token=oa.access_token)

        followers = zalo.get_followers()
        for zalo_user in followers:
            zalo_user_in_db = CrawlData.objects.filter(
                object_id=zalo_user,
            ).first()
            
            if not zalo_user_in_db:    
                new_check_time, messages = zalo.get_follower_message(zalo_user)
                all_messages = '\n'.join(messages)

                if not extract_phone(all_messages):
                    continue
                CrawlData.objects.create(
                        source='zalo',
                        user=oa.user,
                        company=oa.company,
                        object_id=zalo_user,
                        type=CrawlData.TYPE_MSG,
                        uid=zalo_user,
                        username=zalo_user,
                        content=all_messages,
                        phone=extract_phone(all_messages),
                        last_check_time_int=new_check_time,
                    )
            else:
                new_check_time, messages = zalo.get_follower_message(zalo_user, zalo_user_in_db.last_check_time_int)
                if len(messages) > 0:
                    zalo_user_in_db.last_check_time_int = new_check_time
                    zalo_user_in_db.content = zalo_user_in_db.content + '\n'.join(['\n'] + messages)
                    zalo_user_in_db.save()
        
    def do_crawl(self):
        check_time = timezone.now() - timezone.timedelta(minutes=1)
        
        oas = ZaloOA.objects.annotate(id_mod=F('id') % self.shard).filter(
            id_mod=self.id,
            need_crawl=True,
            last_check_time__lte=check_time,
        )[:self.BULK_SIZE]

        for oa in oas:
            self.crawl_messages(oa)
            oa.last_check_time = timezone.now()
            oa.save()

    def run(self):
        while True:
            try:
                self.do_crawl() 
            except Exception as e:
                pass
            finally:
                time.sleep(self.TIME)


class Command(BaseCommand):
    help = 'Runs a process as a daemon'
 
    def add_arguments(self, parser):
        parser.add_argument('--action')
        parser.add_argument('--pid')
        parser.add_argument('--shard')

    def handle(self, *args, **options):    
        action = options['action']
        pid_path = options['pid']
        shard = int(options['shard'])

        fb_path = pid_path + '.fb'
         
        for id in range(shard):
            fb_crawler = FBCrawler(pidfile=fb_path, shard=shard, id=id)
            if action == 'start':
                try:
                    pid = os.fork()
                    if pid == 0:
                        fb_crawler.start()
                        sys.exit(0)
                except OSError as e:
                    sys.stderr.write("fork #1 failed: %d (%s)\n" %
                                     (e.errno, e.strerror))
                    sys.exit(1)
            elif action == 'stop':
                fb_crawler.stop()
        
        zalo_path = pid_path + '.zalo'
         
        for id in range(shard):
            zalo_crawler = ZaloCrawler(pidfile=zalo_path, shard=shard, id=id)
            if action == 'start':
                try:
                    pid = os.fork()
                    if pid == 0:
                        zalo_crawler.start()
                        sys.exit(0)
                except OSError as e:
                    sys.stderr.write("fork #1 failed: %d (%s)\n" %
                                     (e.errno, e.strerror))
                    sys.exit(1)
            elif action == 'stop':
                zalo_crawler.stop()
