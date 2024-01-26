"""
Celery tasks
"""
import requests
from celery import shared_task

from api.models.organization import Company


@shared_task
def get_company_information(id):
    company = Company.objects.get(pk=id)
    print(company.name)
