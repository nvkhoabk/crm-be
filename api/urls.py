from django.urls import path, include
from api.views import auth
from api.views import manage
from api.views import product
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('manage/create_param/', manage.CreateParamView.as_view(), name='manage.create_param'),
    path('manage/get_param/', manage.GetParamView.as_view(), name='manage.get_param'),
    path('manage/update_param/', manage.UpdateParamView.as_view(), name='manage.update_param'),
    path('manage/filter_param/', manage.FilterParamView.as_view(), name='manage.filter_param'),

    path('manage/create_package/', manage.CreatePackageView.as_view(), name='manage.create_package'),
    path('manage/get_package/', manage.GetPackageView.as_view(), name='manage.get_package'),
    path('manage/update_package/', manage.UpdatePackageView.as_view(), name='manage.update_package'),
    path('manage/filter_package/', manage.FilterPackageView.as_view(), name='manage.filter_package'),
    path('manage/delete_package/', manage.DeletePackageView.as_view(), name='manage.delete_package'),

    path('manage/create_company/', manage.CreateCompanyView.as_view(), name='manage.create_company'),
    path('manage/get_company/', manage.GetCompanyView.as_view(), name='manage.get_company'),
    path('manage/update_company/', manage.UpdateCompanyView.as_view(), name='manage.update_company'),
    path('manage/filter_company/', manage.FilterCompanyView.as_view(), name='manage.filter_company'),
    path('manage/delete_company/', manage.DeleteCompanyView.as_view(), name='manage.delete_company'),

    path('manage/create_department/', manage.CreateDepartmentView.as_view(), name='manage.create_department'),
    path('manage/get_department/', manage.GetDepartmentView.as_view(), name='manage.get_department'),
    path('manage/update_department/', manage.UpdateDepartmentView.as_view(), name='manage.update_department'),
    path('manage/filter_department/', manage.FilterDepartmentView.as_view(), name='manage.filter_department'),
    path('manage/delete_department/', manage.DeleteDepartmentView.as_view(), name='manage.delete_department'),

    path('manage/create_role/', manage.CreateRoleView.as_view(), name='manage.create_role'),
    path('manage/get_role/', manage.GetRoleView.as_view(), name='manage.get_role'),
    path('manage/update_role/', manage.UpdateRoleView.as_view(), name='manage.update_role'),
    path('manage/filter_role/', manage.FilterRoleView.as_view(), name='manage.filter_role'),
    path('manage/delete_role/', manage.DeleteRoleView.as_view(), name='manage.delete_role'),

    path('manage/create_permission/', manage.CreatePermissionView.as_view(), name='manage.create_permission'),
    path('manage/get_permission/', manage.GetPermissionView.as_view(), name='manage.get_permission'),
    path('manage/update_permission/', manage.UpdatePermissionView.as_view(), name='manage.update_permission'),
    path('manage/filter_permission/', manage.FilterPermissionView.as_view(), name='manage.filter_permission'),
    path('manage/delete_permission/', manage.DeletePermissionView.as_view(), name='manage.delete_permission'),

    path('manage/create_user/', manage.CreateUserView.as_view(), name='manage.create_user'),
    path('manage/filter_user/', manage.FilterUserView.as_view(), name='manage.filter_user'),
    path('manage/get_user/', manage.GetUserView.as_view(), name='manage.get_user'),
    path('manage/update_user/', manage.UpdateUserView.as_view(), name='manage.update_user'),
    path('manage/delete_user/', manage.DeleteUserView.as_view(), name='manage.delete_user'),

    # Call center
    path('callcenter/incoming_call/', manage.DeleteUserView.as_view(), name='callcenter.incoming_call'),
    path('callcenter/outgoing_call/', manage.DeleteUserView.as_view(), name='callcenter.outgoing_call'),
    path('callcenter/call_answered/', manage.DeleteUserView.as_view(), name='callcenter.call_answered'),
    path('callcenter/call_logs/', manage.DeleteUserView.as_view(), name='callcenter.call_logs'),
    path('callcenter/get_call_history/', manage.DeleteUserView.as_view(), name='callcenter.get_call_history'),
    path('callcenter/register/', manage.DeleteUserView.as_view(), name='callcenter.register'),
    path('callcenter/register/', manage.DeleteUserView.as_view(), name='callcenter.register'),

    # Product
    path('product/create_product/', product.CreateProductView.as_view(), name='product.create_product'),
    path('product/filter_product/', product.FilterProductView.as_view(), name='product.filter_product'),
    path('product/get_product/', product.GetProductView.as_view(), name='product.get_product'),
    path('product/update_product/', product.UpdateProductView.as_view(), name='product.update_product'),
    path('product/delete_product/', product.DeleteProductView.as_view(), name='product.delete_product'),


    # Auth
    path('auth/get_user_info/', auth.AuthGetUserInfoView.as_view(), name='auth.get_user_info'),

    path('auth/login/', TokenObtainPairView.as_view(), name='auth.login'),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
]
