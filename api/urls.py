from django.urls import path, include
from api.views import article
from api.views import auth
from api.views import manage


urlpatterns = [
    path('article/create/', article.ArticleCreateView.as_view(), name='article.create'),
    
    # Auth
    path('auth/login/', auth.AuthLoginView.as_view(), name='auth.login'),
    path('auth/logout/', auth.AuthLogoutView.as_view(), name='auth.logout'), 

    path('manage/create_param/', manage.CreateParamView.as_view(), name='manage.create_param'),
    path('manage/update_param/', manage.UpdateParamView.as_view(), name='manage.update_param'),
    path('manage/filter_param/', manage.FilterParamView.as_view(), name='manage.filter_param'),

    path('manage/create_package/', manage.CreatePackageView.as_view(), name='manage.create_package'),
    path('manage/update_package/', manage.UpdatePackageView.as_view(), name='manage.update_package'),
    path('manage/filter_package/', manage.FilterPackageView.as_view(), name='manage.filter_package'),
    path('manage/delete_package/', manage.DeletePackageView.as_view(), name='manage.delete_package'),

    # Company management
    path('manage/create_company/', manage.CreateCompanyView.as_view(), name='manage.create_company'),
    path('manage/update_company/', manage.UpdateCompanyView.as_view(), name='manage.update_company'),
    path('manage/filter_company/', manage.FilterCompanyView.as_view(), name='manage.filter_company'),
    path('manage/delete_company/', manage.DeleteCompanyView.as_view(), name='manage.delete_company'),

    path('manage/create_department/', manage.CreateDepartmentView.as_view(), name='manage.create_department'),
    path('manage/update_department/', manage.UpdateDepartmentView.as_view(), name='manage.update_department'),
    path('manage/filter_department/', manage.FilterDepartmentView.as_view(), name='manage.filter_department'),
    path('manage/delete_department/', manage.DeleteDepartmentView.as_view(), name='manage.delete_department'),
]
