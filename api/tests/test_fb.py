from django.test import Client, TestCase
import facebook
import json
import re
from api.fb.page import FBPageUtil
from api.utils.phone import extract_phone
from api.services.crawl import CrawlService
from api.models.data import FBPage


class TestCrawl(TestCase):
    def test_extract_phone(self):
        data = 'test 0363930208 0363930208 ne'
        r = extract_phone(data)

    def test_get_page_info(self):
        access_token="EAAEhtTd5YR4BAMgWPZA5ZCyZCJgysL8L86QrvEkoL6xnwQTTJLTjKLdhFmFiyZAUCfwFfNZBhkcU4T0R5qdYZAGqEoiml0F0kjyOtGDeIgMEF1Y2mnB5f6daDVZAdrkMXgk3n3DUoQclnLaLoG4Rj1WZBW0Upv248aUJU7W4FnZAgzi50IkpUYF1mUXv9Bzg4DSywFzuT3P0jyY7vjRcx15B9"
        fb = FBPageUtil(access_token) 
        page = fb.get_page_info()
        
        posts = fb.get_page_posts(page['id'])
        for post in posts:
            comment = fb.get_page_comments(post['id']) 
        messages = fb.get_page_messages()

    def test_page_service(self):
        FBPage.objects.create(
            page_id='112992571381772',
            access_token='EAAEhtTd5YR4BAGsSbeT9PtxvK4qHelHKqH1liC1tIf1jzXbFYPIXOHOxbFGW4BZCWohashH8ZCwIQB6D8Pb4IMZAFscUAPIEbZAQUNNmadEo4lu6ZBo2RYwxzSnxBKYExA92N1QZBbiRfWZBoIeCbv4iQfEu1ljXZBB3tW8PArsVyt3snkZBSDKjmGxZBnVqK26uIyIPj7ZAmZCPE3OcKq7HZCc4U',
        )
        
        c = CrawlService()
        c.crawl_posts('112992571381772')

    def test_page_message(self):
        FBPage.objects.create(
            page_id='112992571381772',
            access_token='EAAEhtTd5YR4BAGsSbeT9PtxvK4qHelHKqH1liC1tIf1jzXbFYPIXOHOxbFGW4BZCWohashH8ZCwIQB6D8Pb4IMZAFscUAPIEbZAQUNNmadEo4lu6ZBo2RYwxzSnxBKYExA92N1QZBbiRfWZBoIeCbv4iQfEu1ljXZBB3tW8PArsVyt3snkZBSDKjmGxZBnVqK26uIyIPj7ZAmZCPE3OcKq7HZCc4U',
        )
        
        c = CrawlService()
        c.crawl_messages('112992571381772')
     