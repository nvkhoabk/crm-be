import json
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework import status as http_status
from api.services.exceptions import ManageDeleteCompanyNotFound


class TestManage(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_create_company(self):
        create_company_func_url = reverse('manage.create_company')
        self.assertEqual(create_company_func_url, '/api/manage/create_company/')
        
        data = {
            'name': 'Company A',
            'type': 'electronic',
            'owner': 'owner',
            'phone': '0363930123',
        }
        
        resp = self.client.post(create_company_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        resp = resp.json()
        
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data']['id'], 1)

    def test_delete_company(self):
        delete_company_func_url = reverse('manage.delete_company')
        self.assertEqual(delete_company_func_url, '/api/manage/delete_company/')
        
        data = {
            'id': 1,
        }
        
        resp = self.client.post(delete_company_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], ManageDeleteCompanyNotFound.code)
