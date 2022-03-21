import json
from django.test import TestCase
from api.tests.base import TestCRMBase
from django.urls import reverse
from django.test import Client
from rest_framework import status as http_status
from api.services.exceptions import AuthLoginInvalid
from django.contrib.auth import get_user_model


class TestUserAuth(TestCRMBase):
    def setUp(self):
        self.User = get_user_model()

    def test_login_fail(self):
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'username': 'user@user.com',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        resp = resp.json()
        self.assertEqual(resp['code'], AuthLoginInvalid.code)
    
    def test_login_success(self):
        user = self.User.objects.create_user(
            username='user@user.com',
            password='123456aA@',
        )
         
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'username': 'user@user.com',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertGreater(len(resp['access']), 0)
    