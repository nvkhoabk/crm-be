import json
from django.test import Client, TestCase
from api.tests.base import TestCRMBase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


class TestPackage(TestCRMBase):
    def test_package(self):
        create_package_func_url = reverse('manage.create_package')
        self.assertEqual(create_package_func_url,
                         '/api/manage/create_package/')

        super_user = get_user_model().objects.create_user(username='testuser',
                                                          password='12345',
                                                          is_superuser=True,
                                                          )
        self.assertTrue(self.client.login(
            username='testuser', password='12345'))

        data = {
            'name': 'Package 1',
            'price': 100,
        }

        resp = self.client.post(create_package_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        package_id = resp['data']['id']
        self.assertGreater(package_id, 0)

        update_package_func_url = reverse('manage.update_package')
        self.assertEqual(update_package_func_url,
                         '/api/manage/update_package/')

        data = {
            'id': package_id,
            'name': 'Package 2',
            'price': 200,
        }

        resp = self.client.post(update_package_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_package_func_url = reverse('manage.filter_package')
        self.assertEqual(filter_package_func_url,
                         '/api/manage/filter_package/')

        data = {
            'filter': {
                'name': 'Package 2',
            },
            'paging': {
                'page': 0,
                'page_size': 10,
            }
        }

        resp = self.client.post(filter_package_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        self.assertEqual(len(resp['data']), 1)

        delete_package_func_url = reverse('manage.delete_package')
        self.assertEqual(delete_package_func_url,
                         '/api/manage/delete_package/')

        data = {
            'id': package_id,
        }

        resp = self.client.post(delete_package_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
