import json
from django.test import Client, TestCase

from api.const import MODULES
from api.tests.base import TestCRMBase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status as http_status


class BaseTestSysConfig(TestCRMBase):
    def setUp(self):
        self.client = APIClient()

    def create_super_user_and_set_credentials(self):
        # Create super user
        get_user_model().objects.create_user(username='root',
                                             password='123456aA@',
                                             is_superuser=True)
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

    def create_company(self):
        # Create company
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
        return resp['data']['id']

    def create_company_admin(self, company_id):
        # Create admin for company
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

        # Login
        login_url = reverse('auth.login')
        resp = self.client.post(login_url, json.dumps({
            'username': 'username1',
            'password': '123456aA@'
        }), content_type='application/json')
        resp = resp.json()
        access_token = resp['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def create_department(self, company_id):
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
        return resp['data']['id']

    def create_role(self, company_id, department_id):
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
        return resp['data']['id']

    def create_normal_user(self, company_id, department_id, role_id):
        create_user_func_url = reverse('manage.create_user')
        self.assertEqual(create_user_func_url,
                         '/api/manage/create_user/')

        data = {
            'company_id': company_id,
            'username': 'normal_user',
            'password': '123456aA@',
            'roles': [
                {
                    'department_id': department_id,
                    'role_id': role_id
                }
            ]
        }

        resp = self.client.post(create_user_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        # Login
        login_url = reverse('auth.login')
        resp = self.client.post(login_url, json.dumps({
            'username': 'normal_user',
            'password': '123456aA@'
        }), content_type='application/json')
        resp = resp.json()
        access_token = resp['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
    def create_sys_config_read_permission(self, company_id, department_id, role_id):
        create_permission_func_url = reverse('manage.create_permission')
        self.assertEqual(create_permission_func_url, '/api/manage/create_permission/')

        data = {
            'company_id': company_id,
            'department_id': department_id,
            'role_id': role_id,
            'edit_permissions': [],
            'read_permissions': [MODULES.SYSTEM_CONFIGURATION]
        }

        resp = self.client.post(create_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        return resp['data']['id']

    def create_sys_config_edit_permission(self, company_id, department_id, role_id):
        create_permission_func_url = reverse('manage.create_permission')
        self.assertEqual(create_permission_func_url, '/api/manage/create_permission/')

        data = {
            'company_id': company_id,
            'department_id': department_id,
            'role_id': role_id,
            'edit_permissions': [MODULES.SYSTEM_CONFIGURATION],
            'read_permissions': []
        }

        resp = self.client.post(create_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        return resp['data']['id']



class TestCompanyEmail(BaseTestSysConfig):
    def test_company_email(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        self.create_company_admin(company_id)

        # Create product
        create_company_email_func_url = reverse('sysconfig.create_company_email')
        self.assertEqual(create_company_email_func_url,
                         '/api/sysconfig/create_company_email/')

        data = {
            "email": "testemail@gmail.com",
            "password": "123456a@",
            "company_id": company_id
        }

        resp = self.client.post(create_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        company_email_id = resp['data']['id']
        self.assertGreater(company_email_id, 0)

        update_company_email_func_url = reverse('sysconfig.update_company_email')
        self.assertEqual(update_company_email_func_url,
                         '/api/sysconfig/update_company_email/')

        data = {
            'id': company_email_id,
            'email': 'testemail2@gmail.com',
            "password": "123456a@",
        }

        resp = self.client.post(update_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        get_company_email_func_url = reverse('sysconfig.get_company_email')
        self.assertEqual(get_company_email_func_url,
                         '/api/sysconfig/get_company_email/')

        data = {
            'id': company_email_id,
        }

        resp = self.client.post(get_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_company_email_func_url = reverse('sysconfig.filter_company_email')
        self.assertEqual(filter_company_email_func_url,
                         '/api/sysconfig/filter_company_email/')

        data = {
            'filter': {
                'email': 'test',
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data']['total'], 1)

        delete_company_email_func_url = reverse('sysconfig.delete_company_email')
        self.assertEqual(delete_company_email_func_url,
                         '/api/sysconfig/delete_company_email/')

        data = {
            'id': company_email_id,
        }

        resp = self.client.post(delete_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

    def test_write_fail_product_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_company_email_func_url = reverse('sysconfig.create_company_email')
        self.assertEqual(create_company_email_func_url,
                         '/api/sysconfig/create_company_email/')

        data = {
            "email": "testemail@gmail.com",
            "password": "123456a@",
            "company_id": company_id
        }

        resp = self.client.post(create_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_fail_company_email_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_company_email_func_url = reverse('sysconfig.get_company_email')
        self.assertEqual(get_company_email_func_url,
                         '/api/sysconfig/get_company_email/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_product_with_read_permission(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_company_email_func_url = reverse('sysconfig.get_company_email')
        self.assertEqual(get_company_email_func_url,
                         '/api/sysconfig/get_company_email/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 4002)

    def test_read_product_with_edit_permission(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_edit_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_company_email_func_url = reverse('sysconfig.get_company_email')
        self.assertEqual(get_company_email_func_url,
                         '/api/sysconfig/get_company_email/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 4002)

    def test_write_product_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_edit_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_company_email_func_url = reverse('sysconfig.create_company_email')
        self.assertEqual(create_company_email_func_url,
                         '/api/sysconfig/create_company_email/')

        data = {
            "email": "testemail@gmail.com",
            "password": "123456a@",
            "company_id": company_id
        }

        resp = self.client.post(create_company_email_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)


class TestDataStatus(BaseTestSysConfig):
    def test_data_status(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        self.create_company_admin(company_id)

        # Create product
        create_func_url = reverse('sysconfig.create_data_status')
        self.assertEqual(create_func_url,
                         '/api/sysconfig/create_data_status/')

        data = {
            "name": "data_status_1",
            "company_id": company_id
        }

        resp = self.client.post(create_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        data_status_id = resp['data']['id']
        self.assertGreater(data_status_id, 0)

        update_func_url = reverse('sysconfig.update_data_status')
        self.assertEqual(update_func_url,
                         '/api/sysconfig/update_data_status/')

        data = {
            'id': data_status_id,
            'name': 'data status 2',
        }

        resp = self.client.post(update_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        get_func_url = reverse('sysconfig.get_data_status')
        self.assertEqual(get_func_url,
                         '/api/sysconfig/get_data_status/')

        data = {
            'id': data_status_id,
        }

        resp = self.client.post(get_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_func_url = reverse('sysconfig.filter_data_status')
        self.assertEqual(filter_func_url,
                         '/api/sysconfig/filter_data_status/')

        data = {
            'filter': {
                'name': 'data',
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data']['total'], 1)

        delete_func_url = reverse('sysconfig.delete_data_status')
        self.assertEqual(delete_func_url,
                         '/api/sysconfig/delete_data_status/')

        data = {
            'id': data_status_id,
        }

        resp = self.client.post(delete_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

    def test_write_fail_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_func_url = reverse('sysconfig.create_data_status')
        self.assertEqual(create_func_url,
                         '/api/sysconfig/create_data_status/')

        data = {
            "name": "data_status_1",
            "company_id": company_id
        }

        resp = self.client.post(create_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_fail_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_func_url = reverse('sysconfig.get_data_status')
        self.assertEqual(get_func_url,
                         '/api/sysconfig/get_data_status/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_with_read_permission(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_func_url = reverse('sysconfig.get_data_status')
        self.assertEqual(get_func_url,
                         '/api/sysconfig/get_data_status/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 4004)

    def test_read_with_edit_permission(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_sys_config_edit_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_func_url = reverse('sysconfig.get_data_status')
        self.assertEqual(get_func_url,
                         '/api/sysconfig/get_data_status/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 4004)


class TestDataSubStatus(BaseTestSysConfig):
    def test_data_sub_status(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        self.create_company_admin(company_id)

        # Create product
        create_func_url = reverse('sysconfig.create_data_status')
        self.assertEqual(create_func_url,
                         '/api/sysconfig/create_data_status/')

        data = {
            "name": "data_status_1",
            "company_id": company_id
        }

        resp = self.client.post(create_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        data_status_id = resp['data']['id']
        self.assertGreater(data_status_id, 0)

        create_func_url = reverse('sysconfig.create_data_sub_status')
        self.assertEqual(create_func_url,
                         '/api/sysconfig/create_data_sub_status/')

        data = {
            "name": "data_sub_status_1",
            "data_status_id": data_status_id,
            "company_id": company_id
        }

        resp = self.client.post(create_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        data_sub_status_id = resp['data']['id']
        self.assertGreater(data_sub_status_id, 0)

        update_func_url = reverse('sysconfig.update_data_sub_status')
        self.assertEqual(update_func_url,
                         '/api/sysconfig/update_data_sub_status/')

        data = {
            'id': data_sub_status_id,
            'name': 'data sub status 2',
        }

        resp = self.client.post(update_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        get_func_url = reverse('sysconfig.get_data_sub_status')
        self.assertEqual(get_func_url,
                         '/api/sysconfig/get_data_sub_status/')

        data = {
            'id': data_sub_status_id,
        }

        resp = self.client.post(get_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_func_url = reverse('sysconfig.filter_data_sub_status')
        self.assertEqual(filter_func_url,
                         '/api/sysconfig/filter_data_sub_status/')

        data = {
            'filter': {
                'name': 'data',
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data']['total'], 1)

        delete_func_url = reverse('sysconfig.delete_data_sub_status')
        self.assertEqual(delete_func_url,
                         '/api/sysconfig/delete_data_sub_status/')

        data = {
            'id': data_sub_status_id,
        }

        resp = self.client.post(delete_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

