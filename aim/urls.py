"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from aim import settings
from aim.const import Const

urlpatterns = [

    # Staff
    path('api/user/', include('aim.apps.user.urls')),

    # Store role
    path('api/group-role/', include('aim.apps.group_role.urls')),

    # Asset
    path('api/asset/', include(('aim.apps.asset.urls', 'asset'), namespace='asset')),

    # Trading
    path('api/trading/', include(('aim.apps.trading.urls', 'trading'), namespace='trading')),

    # Accounting
    path('api/accounting/', include(('aim.apps.accounting.urls', 'accounting'), namespace='accounting')),

    # Address
    path('api/address/', include(('aim.apps.address.urls', 'address'), namespace='address')),

] + static('files/', document_root=Const.FILE_ROOT)


schema_view = get_schema_view(
    openapi.Info(
        title='AIM',
        default_version='v3',
        description='',
    ),
    public=True,
    permission_classes = (permissions.AllowAny, ),
)
urlpatterns.extend([
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
])
