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
        code = 'HEVqheLeoXnWsP30e4I8KdFqkTB4MfmiCl3Ac_vov10BmSchorEWTGt5WV7aIx1pKjw7ifzsrdDsmVFuW7dSU5BBdvkbPO09VTEqYjrwad0oqisonMJlDu7Eu9ii9laUjkI9WrXokHB-lSUmMqlNDAA2bQPIEAKdYP_css07mrARn_NNF7-ZQusAeSinR_mGXChNabDZXqY5vTso2a2GJwZuw-e21AnQlk3HXrPAZ5x4eeBN7JsZKUYrZTL6KPCtl_dKamSOerElKelW2h6FhECOhom1au6fk0gsxNcZaSAe5xD8NAoQoemOkJTwWeYGe3gC0ItYbytaM_Sv5EuJwVLY3LWP9QeSxukxhXLY-qYulyZMN7BnUAEWpODAPVfY-wBEhKWeZJh7pjIja9LqHvbkuXm'
        zalo = ZaloPage(code)

        oa_info = zalo.get_info()

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls):
        pass
     