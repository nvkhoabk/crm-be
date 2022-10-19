import os
import sys
import time
from datetime import datetime

import json

import pytz

from api.const import Const
from api.models.system_configuration import DataStatus, DataSubStatus, DataSource, DataChannel
from api.services.data import create_order_history
from api.utils.phone import extract_phone
from api.fb.page import FBPageUtil
from api.management.commands.daemon import Daemon
from api.models.data import CrawlData, ZaloOA, FBUser, FBPage, CrawlObject, Order, Customer
from api.zalo.zutils import ZaloPage
from django.core.management.base import BaseCommand
from django.db.models import F
from pyfacebook import FacebookApi
from django.utils import timezone
import time

import logging
from logging.handlers import RotatingFileHandler

from crm.settings import LOG_ROOT, LOG_LEVEL


class FBCrawler(Daemon):
    BULK_SIZE = 10
    TIME = 120
    START_TIME = 1651289937

    def __init__(self, pidfile, shard=1, id=0):
        pidfile = '{}_{}'.format(pidfile, id)
        self.shard = shard
        self.id = id
        self.logger = None
        super().__init__(pidfile)

    def initializer_logger(self):
        logging.basicConfig(handlers=[RotatingFileHandler(filename=LOG_ROOT + 'crm.{}.log'.format(self.id),
                                                          maxBytes=2048000, backupCount=4)], level=LOG_LEVEL,
                            format='%(levelname)s %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %H:%M:%S %p')

        self.logger = logging.getLogger(__name__)

    def get_crawl_data(self, phone, uid, company_id):
        crawl_data = CrawlData.objects.filter(phone=phone, company_id=company_id).first()

        if crawl_data is None:
            crawl_data = CrawlData.objects.filter(uid=uid, company_id=company_id).first()

        return crawl_data

    def extract_phone_from_comment(self, last_check_time, comment_content, created_time):
        created_time = datetime.strptime(created_time, Const.FB_TIME_FORMAT)
        if created_time < last_check_time:
            return None

        return extract_phone(comment_content)

    def extract_phone_from_message(self, messages, last_check_time):
        result = []
        for message in reversed(messages['data']):
            if datetime.strptime(message['created_time'], Const.FB_TIME_FORMAT) > last_check_time and extract_phone(
                    message['message']) is not None:
                result.append({'phone': extract_phone(message['message']), 'uid': message['from']['id']})

        return result

    def crawl_posts(self, page, data_status, data_sub_status, data_source, data_channel):
        self.logger.debug('Crawling post for page: ' + page.page_name)
        api = FacebookApi(access_token=page.access_token)
        fb = FBPageUtil(access_token=page.access_token)

        offset = 0
        limit = 50

        last_post_check_time = page.last_post_check_time if page.last_post_check_time is not None else page.created_at
        lastest_updated_time = last_post_check_time

        while True:
            posts = fb.get_page_posts(page.page_id, offset, limit)
            offset = offset + limit

            if len(posts) == 0:
                break

            for post in posts:
                post_updated_time = datetime.strptime(post['updated_time'], Const.FB_TIME_FORMAT)
                if post_updated_time <= last_post_check_time:
                    continue
                lastest_updated_time = max(lastest_updated_time, post_updated_time)
                self.logger.debug('Crawling post: '.format(post['id']))
                c_offset = 0
                c_limit = 100
                post_in_db = CrawlObject.objects.filter(
                    object_id=post['id'],
                    company_id=page.company_id,
                    deleted_at__isnull=True
                ).first()

                last_check_time_int = 0
                while True:
                    comments = fb.get_page_comments(post['id'], c_offset, c_limit)
                    if len(comments) == 0:
                        break

                    created_timestamp = int(
                        datetime.strptime(comments[0]['created_time'], Const.FB_TIME_FORMAT).timestamp())
                    if post_in_db:
                        self.logger.debug('Use existing CrawObject for post: {}, last check time: {}'.format(post['id'],
                                                                                                        post_in_db.last_check_time_int))
                        if created_timestamp <= post_in_db.last_check_time_int:
                            break
                    else:
                        self.logger.debug('Create new CrawObject for post: {}'.format(post['id']))
                        new_last_check_time_int = int(page.created_at.timestamp())
                        post_in_db = CrawlObject.objects.create(company_id=page.company_id, object_id=post['id'],
                                                                source='fb', type='post', last_check_time_int=new_last_check_time_int)
                        if created_timestamp <= post_in_db.last_check_time_int:
                            break
                    c_offset = c_offset + c_limit

                    for comment in comments:
                        created_timestamp = int(
                            datetime.strptime(comment['created_time'], Const.FB_TIME_FORMAT).timestamp())
                        if created_timestamp < post_in_db.last_check_time_int:
                            break

                        last_check_time_int = max(last_check_time_int, created_timestamp)

                        phone = self.extract_phone_from_comment(lastest_updated_time, comment['message'],
                                                                comment['created_time'])
                        if not phone:
                            continue

                        self.logger.debug('Creating order from comment: {}'.format(comment['id']))
                        crawl_data = self.get_crawl_data(phone, comment['from']['id'], page.company_id)

                        if crawl_data:
                            self.logger.debug('Use existing CrawlData for comment with phone: ' + phone)
                            crawl_data.content = fb.dump_comment_hierarchy_to_json(comment['id'])
                            crawl_data.save()
                            customer = Customer.objects.filter(phone=phone,
                                                               company=page.company).first()
                            if not customer:
                                self.logger.debug('Creating new customer with phone number: ' + phone)
                                customer = Customer.objects.create(
                                    phone=phone,
                                    name=comment['from']['name'],
                                    company=page.company
                                )

                            duplicated_with = Order.objects.filter(crawl_data_id=crawl_data.id,
                                                                   company_id=page.company_id,
                                                                   deleted_at__isnull=True).order_by('-id').first()

                            new_order = Order.objects.create(
                                crawl_data=crawl_data,
                                customer=customer,
                                company=page.company,
                                created_date=datetime.today(),
                                data_status=data_status,
                                data_sub_status=data_sub_status,
                                data_source=data_source,
                                data_channel=data_channel,
                                customer_name=customer.name,
                                duplicated_with=duplicated_with.id,
                                created_by='system',
                                updated_by='system'
                            )
                            create_order_history(new_order)
                            self.logger.debug('Create new order, id = ' + str(new_order.id))
                        else:
                            self.logger.debug('Create new CrawlData for mess with phone: ' + phone)
                            crawl_data = CrawlData.objects.create(
                                source='fb',
                                object_id=comment['id'],
                                type=CrawlData.TYPE_POST,
                                ref_link=post['permalink_url'],
                                post_message=post['message'],
                                post_picture=post['full_picture'] if 'full_picture' in post else '',
                                uid=comment['from']['id'],
                                username=comment['from']['name'],
                                content=fb.dump_comment_hierarchy_to_json(comment['id']),
                                phone=phone,
                                company=page.company,
                            )

                            customer = Customer.objects.filter(phone=phone,
                                                               company=page.company).first()
                            if not customer:
                                self.logger.debug('Creating new customer with phone number: ' + phone)
                                customer = Customer.objects.create(
                                    phone=phone,
                                    name=comment['from']['name'],
                                    company=page.company
                                )

                            new_order = Order.objects.create(
                                crawl_data=crawl_data,
                                customer=customer,
                                company=page.company,
                                created_date=datetime.today(),
                                data_status=data_status,
                                data_sub_status=data_sub_status,
                                data_source=data_source,
                                data_channel=data_channel,
                                customer_name=customer.name,
                                created_by='system',
                                updated_by='system'
                            )
                            create_order_history(new_order)
                            self.logger.debug('Create new order, id = ' + str(new_order.id))

                if post_in_db is not None and last_check_time_int != 0:
                    post_in_db.last_check_time_int = last_check_time_int
                    post_in_db.save()

        page.last_post_check_time = lastest_updated_time
        page.save()

    def crawl_messages(self, page, data_status, data_sub_status, data_source, data_channel):
        self.logger.debug('Crawling fb mess for page: ' + page.page_name)
        api = FacebookApi(access_token=page.access_token)
        fb = FBPageUtil(access_token=page.access_token)

        offset = 0
        limit = 50

        last_message_check_time = page.last_message_check_time if page.last_message_check_time is not None else page.created_at
        lastest_updated_time = last_message_check_time
        while True:
            messages = fb.get_page_messages(page.page_id, offset, limit)
            if len(messages) == 0:
                break

            offset = offset + limit

            for message in messages:
                conversation_updated_time = datetime.strptime(message['updated_time'], Const.FB_TIME_FORMAT)
                if conversation_updated_time <= last_message_check_time:
                    continue
                lastest_updated_time = max(lastest_updated_time, conversation_updated_time)
                self.logger.debug('Crawling fb mess: {}'.format(message['id']))
                conversation_in_db = CrawlObject.objects.filter(
                    object_id=message['id'], source='fb', type='msg', company_id=page.company_id,
                    deleted_at__isnull=True
                ).first()

                if conversation_in_db is None:
                    self.logger.debug('Create new CrawlObject for mess: {}'.format(message['id']))
                    new_last_check_time_int = int(page.created_at.timestamp())
                    conversation_in_db = CrawlObject.objects.create(object_id=message['id'], source='fb', type='msg',
                                                                    company_id=page.company_id,
                                                                    last_check_time_int=new_last_check_time_int)

                updated_timestamp = int(conversation_updated_time.timestamp())

                if updated_timestamp <= conversation_in_db.last_check_time_int:
                    continue

                phone_list = self.extract_phone_from_message(message['messages'], last_message_check_time)
                conversation_in_db.last_check_time_int = updated_timestamp
                conversation_in_db.save()

                for phone_uid in phone_list:
                    phone = phone_uid['phone']
                    uid = phone_uid['uid']
                    crawl_data = self.get_crawl_data(phone, uid, page.company_id)

                    if crawl_data:
                        self.logger.debug('Use existing CrawlData for mess with phone: ' + phone)
                        crawl_data.content = json.dumps(message['messages'])
                        crawl_data.save()

                        customer = Customer.objects.filter(phone=phone).first()
                        if not customer:
                            self.logger.debug('Create new customer for mess with phone: ' + phone)
                            customer = Customer.objects.create(
                                phone=phone,
                                name=message['senders']['data'][0]['name']
                            )

                        duplicated_with = Order.objects.filter(crawl_data_id=crawl_data.id, company_id=page.company_id,
                                                               deleted_at__isnull=True).order_by('-id').first()

                        new_order = Order.objects.create(
                            crawl_data=crawl_data,
                            customer=customer,
                            company=page.company,
                            created_date=datetime.today(),
                            duplicated_with=duplicated_with.id,
                            data_status=data_status,
                            data_sub_status=data_sub_status,
                            data_source=data_source,
                            data_channel=data_channel,
                            customer_name=customer.name,
                            created_by='system',
                            updated_by='system'
                        )
                        create_order_history(new_order)
                        self.logger.debug('Create new order, id = ' + str(new_order.id))
                    else:
                        self.logger.debug('Create new CrawlData for mess with phone: ' + phone)
                        crawl_data = CrawlData.objects.create(
                            source='fb',
                            object_id=message['id'],
                            uid=uid,
                            username=message['senders']['data'][0]['id'],
                            content=json.dumps(message['messages']),
                            phone=phone,
                            company=page.company,
                            type=CrawlData.TYPE_MSG,
                        )

                        customer = Customer.objects.filter(phone=phone, company=page.company).first()
                        if not customer:
                            self.logger.debug('Create new customer for mess with phone: ' + phone)
                            customer = Customer.objects.create(
                                phone=phone,
                                name=message['senders']['data'][0]['name'],
                                company=page.company
                            )

                        new_order = Order.objects.create(
                            crawl_data=crawl_data,
                            customer=customer,
                            company=page.company,
                            created_date=datetime.today(),
                            data_status=data_status,
                            data_sub_status=data_sub_status,
                            data_source=data_source,
                            data_channel=data_channel,
                            customer_name=customer.name,
                            created_by='system',
                            updated_by='system'
                        )
                        create_order_history(new_order)
                        self.logger.debug('Create new order, id = ' + str(new_order.id))

        page.last_message_check_time = lastest_updated_time
        page.save()

    def do_crawl(self):
        users = FBUser.objects.annotate(id_mod=F('id') % self.shard).filter(
            id_mod=self.id,
            need_crawl=True,
            deleted_at__isnull=True
        )[:self.BULK_SIZE]

        for user in users:
            self.logger.debug('Crawling user: ' + user.name)
            fbpages = FBPage.objects.filter(
                user=user,
                deleted_at__isnull=True
            )
            data_status = DataStatus.objects.filter(company_id=user.company_id, name__iexact='Chưa xác nhận',
                                                    deleted_at__isnull=True).first()
            data_sub_status = DataSubStatus.objects.filter(company_id=user.company_id, name__iexact='Chưa xử lý',
                                                           deleted_at__isnull=True).first()
            data_source = DataSource.objects.filter(company_id=user.company_id, name__iexact='Facebook',
                                                    deleted_at__isnull=True).first()

            for page in fbpages:
                try:
                    self.logger.debug('Crawling page: ' + page.page_name)
                    data_channel = DataChannel.objects.filter(company_id=user.company_id, data_source=data_source,
                                                              name__iexact=page.page_name,
                                                              deleted_at__isnull=True).first()

                    self.crawl_posts(page, data_status, data_sub_status, data_source, data_channel)
                    self.crawl_messages(page, data_status, data_sub_status, data_source, data_channel)
                except Exception as e:
                    self.logger.debug('ERROR: ' + str(e))

    def run(self):
        self.initializer_logger()
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

