from django.urls import path, include
from api.views import article
from api.views import auth


urlpatterns = [
    path('article/create/', article.ArticleCreateView.as_view(), name='article.create'),
    
    # auth
    path('auth/login/', auth.AuthLoginView.as_view(), name='auth.login'),
    path('auth/logout/', auth.AuthLogoutView.as_view(), name='auth.logout'), 
]
