from django.urls import path
from aim.apps.asset import views

urlpatterns = [

    # Asset api
    path('create', views.AssetCreateView.as_view()),
    path('filter', views.AssetFilterView.as_view()),
    path('get/<int:id>', views.AssetGetView.as_view()),
    path('update', views.AssetUpdateView.as_view()),
    path('delete/<int:id>', views.AssetDeleteView.as_view()),
    path('get-new', views.AssetGetNewView.as_view()),
    path('get-buying', views.AssetGetBuyingView.as_view()),
    path('get-owning', views.AssetGetOwningView.as_view()),
    path('get-transferring', views.AssetGetTransferringView.as_view()),

    # Asset type api
    path('asset-type/get', views.AssetTypeGetAllView.as_view()),
    path('asset-type/get/<int:id>', views.AssetTypeGetView.as_view()),

    # Asset status api
    path('asset-status/get', views.AssetStatusGetAllView.as_view()),
    path('asset-status/get/<int:id>', views.AssetStatusGetView.as_view()),

]
