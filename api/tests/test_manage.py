import json
from api.tests.base import TestCRMBase
from django.test import Client
from django.urls import reverse
from rest_framework import status as http_status
from django.contrib.auth import get_user_model
from api.services.exceptions import ManageCompanyNotFound
from rest_framework.test import APIClient


class TestManage(TestCRMBase):
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
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + access_token)
    
    def test_create_company(self):    
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
        self.assertEqual(resp['data']['id'], 1)

        delete_company_func_url = reverse('manage.delete_company')
        self.assertEqual(delete_company_func_url,
                         '/api/manage/delete_company/')

        data = {
            'id': 1,
        }

        resp = self.client.post(delete_company_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

    def test_update_company(self):
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

        update_company_func_url = reverse('manage.update_company')
        self.assertEqual(update_company_func_url,
                         '/api/manage/update_company/')

        data = {
            'id': resp['data']['id'],
            'name': 'Company B',
            'type': 'electronic',
            'owner': 'owner',
            'phone': '0363930123',
        }

        resp = self.client.post(update_company_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        resp = resp.json()

        self.assertEqual(resp['code'], 0)

    def test_delete_company_fail(self):
        super_user = get_user_model().objects.create_user(username='testuser',
                                             password='12345',
                                             is_superuser=True,
                                        )
        self.assertTrue(self.client.login(username='testuser', password='12345'))
    
        delete_company_func_url = reverse('manage.delete_company')
        self.assertEqual(delete_company_func_url,
                         '/api/manage/delete_company/')

        data = {
            'id': 1,
        }

        resp = self.client.post(delete_company_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], ManageCompanyNotFound.code)

    def test_filter_company(self):
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

        filter_company_func_url = reverse('manage.filter_company')
        self.assertEqual(filter_company_func_url,
                         '/api/manage/filter_company/')

        data = {
            'filter': {
                'name': 'Company',
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_company_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data']['total'], 1)

    def test_department(self):
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

        update_department_func_url = reverse('manage.update_department')
        self.assertEqual(update_department_func_url,
                         '/api/manage/update_department/')

        data = {
            'id': department_id,
            'department_name': 'name 2',
        }

        resp = self.client.post(update_department_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_department_func_url = reverse('manage.filter_department')
        self.assertEqual(filter_department_func_url,
                         '/api/manage/filter_department/')

        data = {
            'filter': {
                'company_id': company_id,
                'department_id': department_id,
                'department_name': 'name',
            },
            'paging': {
                'page': 1,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_department_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        delete_department_func_url = reverse('manage.delete_department')
        self.assertEqual(delete_department_func_url,
                         '/api/manage/delete_department/')

        data = {
           'id': department_id, 
        }

        resp = self.client.post(delete_department_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0) 
    
    def test_role(self):
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

        update_role_func_url = reverse('manage.update_role')
        self.assertEqual(update_role_func_url, '/api/manage/update_role/')
        data = {
            'id': role_id,
            'role_name': 'role name 2',
        }
         
        resp = self.client.post(update_role_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_role_func_url = reverse('manage.filter_role')
        self.assertEqual(filter_role_func_url,
                         '/api/manage/filter_role/')

        data = {
            'filter': {
                'company_id': company_id,
                'department_id': department_id,
                'role_id': role_id,
                'role_name': 'name',
            },
            'paging': {
                'page': 1,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_role_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        delete_role_func_url = reverse('manage.delete_role')
        self.assertEqual(delete_role_func_url,
                         '/api/manage/delete_role/')

        data = {
           'id': role_id, 
        }

        resp = self.client.post(delete_role_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0) 
    
    def test_permission(self):
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

        update_role_func_url = reverse('manage.update_role')
        self.assertEqual(update_role_func_url, '/api/manage/update_role/')
        data = {
            'id': role_id,
            'role_name': 'role name 2',
        }
         
        resp = self.client.post(update_role_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_role_func_url = reverse('manage.filter_role')
        self.assertEqual(filter_role_func_url,
                         '/api/manage/filter_role/')

        data = {
            'filter': {
                'company_id': company_id,
                'department_id': department_id,
                'role_id': role_id,
                'role_name': 'name',
            },
            'paging': {
                'page': 1,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_role_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        # Permission
        create_permission_func_url = reverse('manage.create_permission') 
        self.assertEqual(create_permission_func_url, '/api/manage/create_permission/')

        data = {
            'company_id': company_id,
            'department_id': department_id,
            'role_id': role_id,
            'edit_permissions': ['Marketing', 'Báo cáo'],
            'read_permissions': ['Sản phẩm và kho hàng', 'Quản lý data']
        }

        resp = self.client.post(create_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        permission_id = resp['data']['id']

        update_permission_func_url = reverse('manage.update_permission') 
        self.assertEqual(update_permission_func_url, '/api/manage/update_permission/')

        data = {
            'id': permission_id,
            'edit_permissions': ['Marketing', 'Báo cáo'],
            'read_permissions': ['Sản phẩm và kho hàng', 'Quản lý data']
        }

        resp = self.client.post(update_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
    
        filter_permission_func_url = reverse('manage.filter_permission')
        self.assertEqual(filter_permission_func_url,
                         '/api/manage/filter_permission/')

        data = {
            'filter': {
                'company_id': company_id,
                'department_id': department_id,
                'role_id': role_id,
                'permission_id': permission_id,
            },
            'paging': {
                'page': 1,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        delete_permisison_func_url = reverse('manage.delete_permission')
        self.assertEqual(delete_permisison_func_url,
                         '/api/manage/delete_permission/')

        data = {
           'id': permission_id, 
        }

        resp = self.client.post(delete_permisison_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0) 