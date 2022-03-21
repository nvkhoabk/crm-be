import json

from api.services.exceptions import ManageCompanyNotFound
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status as http_status
from rest_framework.test import APIClient


class TestCRMBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        super_user = get_user_model().objects.create_user(username='root',
                                                          password='123456aA@',
                                                          is_superuser=True,
                                                          )
        login_url = reverse('auth.login')
        self.assertEqual(login_url,
                         '/api/auth/login/')
        resp = self.client.post(login_url, json.dumps({
            'username': 'root',
            'password': '123456aA@'
        }), content_type='application/json')
        resp = resp.json()
        access_token = resp['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
