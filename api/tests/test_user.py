import json
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status as http_status
from api.tests.base import TestCRMBase


class TestUser(TestCRMBase):
    def test_create_user(self):
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
            'company_id': company_id,
            'username': 'username2',
            'password': '123456aA@',
            'status': 1,
        }
        
        resp = self.client.post(update_user_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0)
        
        filter_user_url = reverse('manage.filter_user')
        self.assertEqual(filter_user_url, '/api/manage/filter_user/')
      
        data = {
            'filter': {
                'company_id': company_id,
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }
        
        resp = self.client.post(filter_user_url, json.dumps(data), content_type='application/json')
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
        
        resp = resp.json()
        self.assertGreater(len(resp['access']), 0)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp['access'])

        get_user_info_func_url = reverse('auth.get_user_info')
        self.assertEqual(get_user_info_func_url, '/api/auth/get_user_info/')
    
        resp = self.client.get(get_user_info_func_url, content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()
        self.assertEqual(record['code'], 0)
   
        delete_user_func_url = reverse('manage.delete_user')
        self.assertEqual(delete_user_func_url, '/api/manage/delete_user/')
        
        data = {
            'id': uid,
        }
        
        resp = self.client.post(delete_user_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
    
    def test_create_user_with_permission(self):
        super_user = get_user_model().objects.create_user(username='testuser',
                                             password='12345',
                                             is_superuser=True,
                                        )
        self.assertTrue(self.client.login(username='testuser', password='12345'))
    
        data = {
            'name': 'Company A',
            'type': 'electronic',
            'owner': 'owner',
            'phone': '0363930123',
        }

        resp = self.client.post(reverse('manage.create_company'), json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        company_id = resp.json()['data']['id']

        create_department_func_url = reverse('manage.create_department')
        self.assertEqual(create_department_func_url,
                         '/api/manage/create_department/')

        data = {
            'company_id': company_id,
            'department_name': 'department name',
        }

        resp = self.client.post(create_department_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        department_id = resp['data']['id']

        create_role_func_url = reverse('manage.create_role')
        self.assertEqual(create_role_func_url, '/api/manage/create_role/')

        data = {
            'company_id': company_id,
            'department_id': department_id,
            'role_name': 'Role name',
        }

        resp = self.client.post(create_role_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        role_id = resp['data']['id']
        
        
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
        
        login_func_url = reverse('auth.login')
        self.assertEqual(login_func_url, '/api/auth/login/')
        
        data = {
            'username': 'username1',
            'password': '123456aA@',
        }
        
        resp = self.client.post(login_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        resp = resp.json()
        self.assertGreater(len(resp['access']), 0)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + resp['access'])
        
        # Create member as a admin
        create_user_func_url = reverse('manage.create_user')
        self.assertEqual(create_user_func_url,
                         '/api/manage/create_user/')

        data = {
            'company_id': company_id,
            'username': 'username2',
            'password': '123456aA@',
        }

        resp = self.client.post(create_user_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        resp = resp.json()
        self.assertEqual(resp['code'], 1)

        data = {
            'company_id': company_id,
            'roles': [{
                'department_id': department_id,
                'role_id': role_id,
            }],
            'username': 'username2',
            'password': '123456aA@',
        }

        resp = self.client.post(create_user_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        uid = resp['data']['id']

        get_user_func_url = reverse('manage.get_user')
        self.assertEqual(get_user_func_url,
                         '/api/manage/get_user/')

        data = {
            'id': uid,
        }

        resp = self.client.post(get_user_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        resp = resp.json()
        self.fail(resp)
        self.assertEqual(resp['code'], 0)