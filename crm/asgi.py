import os

from django.core.asgi import get_asgi_application
from django.urls import path

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

from api.middleware import TokenAuthMiddlewareStack
from api.consumers import CrmConsumer

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('ws/', CrmConsumer.as_asgi()),
        ])
    ),
})
