import json
from django.test import Client, TestCase

from api.tests.base import TestCRMBase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status as http_status


class TestProduct(TestCRMBase):
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

    def create_product_read_permission(self, company_id, department_id, role_id):
        create_permission_func_url = reverse('manage.create_permission')
        self.assertEqual(create_permission_func_url, '/api/manage/create_permission/')

        data = {
            'company_id': company_id,
            'department_id': department_id,
            'role_id': role_id,
            'edit_permissions': [],
            'read_permissions': ['PRODUCT_AND_WAREHOUSE']
        }

        resp = self.client.post(create_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        return resp['data']['id']

    def create_product_edit_permission(self, company_id, department_id, role_id):
        create_permission_func_url = reverse('manage.create_permission')
        self.assertEqual(create_permission_func_url, '/api/manage/create_permission/')

        data = {
            'company_id': company_id,
            'department_id': department_id,
            'role_id': role_id,
            'edit_permissions': ['PRODUCT_AND_WAREHOUSE'],
            'read_permissions': []
        }

        resp = self.client.post(create_permission_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        return resp['data']['id']

    def test_product(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        self.create_company_admin(company_id)

        # Create product
        create_product_func_url = reverse('product.create_product')
        self.assertEqual(create_product_func_url,
                         '/api/product/create_product/')

        data = {
          "name": "product 1",
          "description": "product",
          "price": 1000,
          "payment_method": "DEBIT",
          "period_fee": 100,
          "date_in_month_payment": 1,
          "number_of_date_notify": 7,
          "company_id": company_id
        }

        resp = self.client.post(create_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        product_id = resp['data']['id']
        self.assertGreater(product_id, 0)

        update_product_func_url = reverse('product.update_product')
        self.assertEqual(update_product_func_url,
                         '/api/product/update_product/')

        data = {
            'id': product_id,
            'name': 'Product 2',
            'price': 200,
        }

        resp = self.client.post(update_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        get_product_func_url = reverse('product.get_product')
        self.assertEqual(get_product_func_url,
                         '/api/product/get_product/')

        data = {
            'id': product_id,
        }

        resp = self.client.post(get_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_product_func_url = reverse('product.filter_product')
        self.assertEqual(filter_product_func_url,
                         '/api/product/filter_product/')

        data = {
            'filter': {
                'name': 'pro',
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data']['total'], 1)

        delete_product_func_url = reverse('product.delete_product')
        self.assertEqual(delete_product_func_url,
                         '/api/product/delete_product/')

        data = {
            'id': product_id,
        }

        resp = self.client.post(delete_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)


    def test_write_fail_product_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_product_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_product_func_url = reverse('product.create_product')
        self.assertEqual(create_product_func_url,
                         '/api/product/create_product/')

        data = {
            "name": "product 1",
            "description": "product",
            "price": 1000,
            "payment_method": "DEBIT",
            "period_fee": 100,
            "date_in_month_payment": 1,
            "number_of_date_notify": 7,
            "company_id": company_id
        }

        resp = self.client.post(create_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_fail_product_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_product_func_url = reverse('product.get_product')
        self.assertEqual(get_product_func_url,
                         '/api/product/get_product/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


    def test_read_product_with_read_permission(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_product_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_product_func_url = reverse('product.get_product')
        self.assertEqual(get_product_func_url,
                         '/api/product/get_product/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 3001)


    def test_read_product_with_edit_permission(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_product_read_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        get_product_func_url = reverse('product.get_product')
        self.assertEqual(get_product_func_url,
                         '/api/product/get_product/')

        data = {
            'id': 1,
        }

        resp = self.client.post(get_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 3001)

    def test_write_product_with_normal_user(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_product_edit_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_product_func_url = reverse('product.create_product')
        self.assertEqual(create_product_func_url,
                         '/api/product/create_product/')

        data = {
            "name": "product 1",
            "description": "product",
            "price": 1000,
            "payment_method": "DEBIT",
            "period_fee": 100,
            "date_in_month_payment": 1,
            "number_of_date_notify": 7,
            "company_id": company_id
        }

        resp = self.client.post(create_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_write_duplicate_product(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_product_edit_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_product_func_url = reverse('product.create_product')
        self.assertEqual(create_product_func_url,
                         '/api/product/create_product/')

        data = {
            "name": "product 1",
            "description": "product",
            "price": 1000,
            "payment_method": "DEBIT",
            "period_fee": 100,
            "date_in_month_payment": 1,
            "number_of_date_notify": 7,
            "company_id": company_id
        }

        resp = self.client.post(create_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = {
            "name": "product 1",
            "description": "product dup",
            "price": 1001,
            "payment_method": "CREDIT",
            "period_fee": 5,
            "date_in_month_payment": 2,
            "number_of_date_notify": 5,
            "company_id": company_id
        }

        resp = self.client.post(create_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = resp.json()
        self.assertEqual(resp['code'], 3002)

    def test_create_product_with_wrong_company_product(self):
        self.create_super_user_and_set_credentials()
        company_id = self.create_company()
        department_id = self.create_department(company_id)
        role_id = self.create_role(company_id, department_id)
        self.create_product_edit_permission(company_id, department_id, role_id)
        self.create_normal_user(company_id, department_id, role_id)

        create_product_func_url = reverse('product.create_product')
        self.assertEqual(create_product_func_url,
                         '/api/product/create_product/')

        data = {
            "name": "product 1",
            "description": "product",
            "price": 1000,
            "payment_method": "DEBIT",
            "period_fee": 100,
            "date_in_month_payment": 1,
            "number_of_date_notify": 7,
            "company_id": company_id + 1
        }

        resp = self.client.post(create_product_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

