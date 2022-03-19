import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model


class TestParam(TestCase):
    def setUp(self):
        self.client = Client()

    def test_param(self):
        create_param_func_url = reverse('manage.create_param')
        self.assertEqual(create_param_func_url, '/api/manage/create_param/')

        super_user = get_user_model().objects.create_user(username='testuser',
                                             password='12345',
                                             is_superuser=True,
                                        )
        self.assertTrue(self.client.login(username='testuser', password='12345'))

        data = {
            'key': 'INTRODUCTION',
            'value': 'Hello',
        }

        resp = self.client.post(create_param_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)

        filter_param_func_url = reverse('manage.filter_param')
        self.assertEqual(filter_param_func_url, '/api/manage/filter_param/')

        data = {
        }

        resp = self.client.post(filter_param_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
        records = resp['data']
        self.assertEqual(len(records), 1)

        update_param_func_url = reverse('manage.update_param')
        self.assertEqual(update_param_func_url, '/api/manage/update_param/')

        data = {
            'key': 'INTRODUCTION',
            'value': 'Hello 2',
        }

        resp = self.client.post(update_param_func_url, json.dumps(
            data), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = resp.json()
        self.assertEqual(resp['code'], 0)
