import json
from django.test import TestCase
from django.urls import reverse
from django.test import Client
from rest_framework import status as http_status
from api.services.exceptions import AuthLoginInvalid
from django.contrib.auth import get_user_model


class TestUserAuth(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.User = get_user_model()

    def test_login_fail(self):
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'email': 'user@user.com',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], AuthLoginInvalid.code)
    
    def test_login_success(self):
        user = self.User.objects.create_user(
            email='user@user.com',
            password='123456aA@',
        )
         
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'email': 'user@user.com',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        record = resp.json()
        self.assertEqual(record['code'], 0)
    
    def test_logout(self):
        user = self.User.objects.create_user(
            email='user@user.com',
            password='123456aA@',
        )
         
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'email': 'user@user.com',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0)
        
        # Logout
        logout_func_url = reverse('auth.logout')
        self.assertEqual(logout_func_url, '/api/auth/logout/')
    
        self.assertTrue(self.client.login(**data))
        
        resp = self.client.post(logout_func_url, json.dumps({}), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0) 
