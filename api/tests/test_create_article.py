import json
from django.test import TestCase
from django.urls import reverse
from django.test import Client
from rest_framework import status as http_status


class TestCreateArticle(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_create_article(self):
        create_func_url = reverse('article.create')
        self.assertEqual(create_func_url, '/api/article/create/')
        
        data = {
            'title': 'Test title',
        }
        
        resp = self.client.post(create_func_url, json.dumps(data), content_type='application/json')
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)
        
        record = resp.json()['data']
        
        self.assertEqual(record['title'], data['title']) 
        