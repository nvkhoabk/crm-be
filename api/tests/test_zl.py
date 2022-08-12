from django.test import Client, TestCase, SimpleTestCase
import facebook
import json
import re
from api.fb.page import FBPageUtil
from api.management.commands.crawler import FBCrawler
from api.utils.phone import extract_phone
from api.services.crawl import CrawlService
from api.models.data import FBPage
from api.zalo.zutils import ZaloPage


class TestCrawlZalo(SimpleTestCase):
    databases = ['default']

    def test_crawl_page(self):
        code = 'Gxq2WDkKinTdWsRk_hZnMNIkJ_oQfkKdDQeyjQ2FdHi0bJZlhBpa5Z2CJxM3eyrXTfPZljwOlrblYnxsmf2lRNgnJOJMj-SXUfXPWuEN-LyrcIMwC9YjCENRHiqmbiihgh1bd03vWsQpg6py2zdG3hh8PwaPnDOjlzCEtp2ZfdoRdMYOFC-L9i6IDfqrd9evcfuucmENdnhuW4p1LhwlFEhb5v8NkPGllhXEq5JxiY72wsxSGzFUVl3yMzW9-l8HmgHyeZ3i9GEgXT3mixix22wAbh6OenW5nvsmh9wgQqecliFgZQ9XFYM3kTUVYYT4FPVetEgXK39nTdKJatVgX0iOnPi9EIbIfX3cXNCjB3NsDk22DozTUlucYyGsMre7h3-Id2PZKb8coJFxOiUIcnS'
        zalo = ZaloPage(code)

        oa_info = zalo.get_info()

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass
     