from django.urls import path, include
from api.views import article
from api.views import auth
from api.views import manage


urlpatterns = [
    path('article/create/', article.ArticleCreateView.as_view(), name='article.create'),
    
    # Auth
    path('auth/login/', auth.AuthLoginView.as_view(), name='auth.login'),
    path('auth/logout/', auth.AuthLogoutView.as_view(), name='auth.logout'), 

    # Company management
    path('manage/create_company/', manage.CreateCompanyView.as_view(), name='manage.create_company'),
    path('manage/update_company/', manage.UpdateCompanyView.as_view(), name='manage.update_company'),
    path('manage/filter_company/', manage.FilterCompanyView.as_view(), name='manage.filter_company'),
    path('manage/delete_company/', manage.DeleteCompanyView.as_view(), name='manage.delete_company'),
]
