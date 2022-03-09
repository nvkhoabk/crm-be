from django.urls import path, include
from api import views


urlpatterns = [
    path('article/create/', views.ArticleCreateView.as_view(), name='article.create'),
]
