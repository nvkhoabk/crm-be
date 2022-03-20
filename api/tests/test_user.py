import json
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status as http_status


class TestUser(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        super_user = get_user_model().objects.create_user(username='testuser',
                                             password='12345',
                                             is_superuser=True,
                                        )
        self.assertTrue(self.client.login(username='testuser', password='12345'))
    
        create_company_func_url = reverse('manage.create_company')
        self.assertEqual(create_company_func_url,
                         '/api/manage/create_company/')
        
        data = {
            'name': 'Company A',
            'type': 'electronic',
            'owner': 'owner',
            'phone': '0363930123',
        }

        resp = self.client.post(create_company_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        resp = resp.json()

        self.assertEqual(resp['code'], 0)
        company_id = resp['data']['id']
        
        create_user_func_url = reverse('manage.create_user')
        self.assertEqual(create_user_func_url,
                         '/api/manage/create_user/')

        data = {
            'company_id': company_id,
            'username': 'username1',
            'password': '123456aA@',
        }

        resp = self.client.post(create_user_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        uid = resp['data']['id']
        self.assertGreater(uid, 0)

        update_user_url = reverse('manage.update_user')
        self.assertEqual(update_user_url, '/api/manage/update_user/')
        data = {
            'id': uid,
            'username': 'username2',
            'password': '123456aA@',
            'status': 1,
        }
        
        resp = self.client.post(update_user_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0)
    

        # Try to login
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'username': 'username2',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0)

        get_user_info_func_url = reverse('auth.get_user_info')
        self.assertEqual(get_user_info_func_url, '/api/auth/get_user_info/')
    
        resp = self.client.get(get_user_info_func_url, content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0)
    