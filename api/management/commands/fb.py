import os
import sys
import time
from api.utils.phone import extract_phone
from api.fb.page import FBPageUtil
from api.management.commands.daemon import Daemon
from api.models.fbdata import CrawlData, FBPage, FBUser
from django.core.management.base import BaseCommand
from django.db.models import F
from pyfacebook import FacebookApi
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
        posts = api.page.get_posts(
            object_id=page.page_id, count=100, limit=100).data
        for post in posts:
            fields = 'id,created_time,message,permalink_url,from'
            comments = api.page.get_comments(
                object_id=post.id, fields=fields, count=100, limit=100).data
            for comment in comments:
                comment = comment.to_dict()
                if not extract_phone(comment['message']):
                    continue
                CrawlData.objects.create(
                    source='fb',
                    ref_link=comment['permalink_url'],
                    uid=comment['from']['id'],
                    username=comment['from']['name'],
                    content=comment['message'],
                    phone=extract_phone(comment['message']),
                )

        page.last_check_time = int(time.time()) 
        page.save()

    def crawl_messages(self, page):
        api = FacebookApi(access_token=page.access_token)
        fb = FBPageUtil(access_token=page.access_token)

        messages = fb.get_page_messages()
        for message in messages:
            all_messages = ' '.join(message['messages'])
            if not extract_phone(all_messages):
                continue

            CrawlData.objects.create(
                source='fb',
                uid=message['senders']['data'][0]['id'],
                username=message['senders']['data'][0]['id'],
                content=all_messages,
                phone=extract_phone(all_messages),
            )

    def do_crawl(self):
        users = FBUser.objects.annotate(id_mod=F('id') % self.shard).filter(
            id_mod=self.id
        )[:self.BULK_SIZE]

        for user in users:
            fbpages = FBPage.objects.filter(
                user=user
            )
            for page in fbpages:
                posts = self.crawl_posts(page)
                messages = self.crawl_messages(page)

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

        for id in range(shard):
            crawler = FBCrawler(pidfile=pid_path, shard=shard, id=id)
            # crawler.do_crawl()

            if action == 'start':
                try:
                    pid = os.fork()
                    if pid == 0:
                        crawler.start()
                        sys.exit(0)
                except OSError as e:
                    sys.stderr.write("fork #1 failed: %d (%s)\n" %
                                     (e.errno, e.strerror))
                    sys.exit(1)
            elif action == 'stop':
                crawler.stop()
