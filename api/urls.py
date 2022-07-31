from django.urls import path, include

from api.const import Const
from api.views import auth
from api.views import manage
from api.views import product
from api.views import call_center
from api.views import crawl
from api.views import data
from api.views import system_configuration
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('manage/create_param/', manage.CreateParamView.as_view(), name='manage.create_param'),
    path('manage/get_param/', manage.GetParamView.as_view(), name='manage.get_param'),
    path('manage/update_param/', manage.UpdateParamView.as_view(), name='manage.update_param'),
    path('manage/filter_param/', manage.FilterParamView.as_view(), name='manage.filter_param'),

    path('manage/create_customer/', manage.CreateCustomerView.as_view(), name='manage.create_customer'),
    path('manage/get_customer/', manage.GetCustomerView.as_view(), name='manage.get_customer'),
    path('manage/update_customer/', manage.UpdateCustomerView.as_view(), name='manage.update_customer'),
    path('manage/filter_customer/', manage.FilterCustomerView.as_view(), name='manage.filter_customer'),

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
    path('callcenter/create_callcenter/', call_center.CreateCallCenterView.as_view(),
         name='callcenter.create_callcenter'),
    path('callcenter/get_callcenter/', call_center.GetCallCenterView.as_view(), name='callcenter.get_callcenter'),
    path('callcenter/update_callcenter/', call_center.UpdateCallCenterView.as_view(),
         name='callcenter.update_callcenter'),
    path('callcenter/filter_callcenter/', call_center.FilterCallCenterView.as_view(),
         name='callcenter.filter_callcenter'),
    path('callcenter/enable_callcenter/', call_center.EnableCallCenterView.as_view(),
         name='callcenter.enable_callcenter'),
    path('callcenter/disable_callcenter/', call_center.DisableCallCenterView.as_view(),
         name='callcenter.disable_callcenter'),

    path('callcenter/start_callin/', call_center.StartCallInView.as_view(), name='callcenter.start_callin'),
    path('callcenter/end_callin/', call_center.EndCallInView.as_view(), name='callcenter.end_callin'),
    path('callcenter/start_callout/', call_center.StartCallOutView.as_view(), name='callcenter.start_callout'),
    path('callcenter/end_callout/', call_center.EndCallOutView.as_view(), name='callcenter.end_callout'),

    path('callcenter/get_agents/', call_center.GetAgentsView.as_view(), name='callcenter.get_agents'),
    path('callcenter/update_agents/', call_center.UpdateAgentsView.as_view(), name='callcenter.update_agents'),
    path('callcenter/create_agent_register/', call_center.CreateAgentRegisterCenterView.as_view(),
         name='callcenter.create_agent_register'),
    path('callcenter/delete_agent_register/', call_center.DeleteAgentRegisterCenterView.as_view(),
         name='callcenter.delete_agent_register'),
    path('callcenter/filter_agent_register/', call_center.FilterAgentRegisterCenterView.as_view(),
         name='callcenter.filter_agent_register'),

    path('callcenter/get_company_call_history/', call_center.GetCompanyCallHistoryView.as_view(),
         name='callcenter.get_company_call_history'),
    path('callcenter/get_user_call_history/', call_center.GetUserCallHistoryView.as_view(),
         name='callcenter.get_user_call_history'),

    path('callcenter/get_call_report/', call_center.GetCallReportView.as_view(), name='callcenter.get_call_report'),
    path('callcenter/get_external_report/', call_center.GetExternalPaymentReportView.as_view(),
         name='callcenter.get_external_report'),
    path('callcenter/get_credit_payment_report/', call_center.GetCreditPaymentReportView.as_view(),
         name='callcenter.get_external_report'),
    path('callcenter/calculate_payment/', call_center.CalculatePayemntCallCenterView.as_view(),
         name='callcenter.calculate_payment'),
    path('callcenter/upload_ext_file/', call_center.UploadExtFile.as_view(), name='upload_ext_file'),
    path('callcenter/download_ext_file/', call_center.DownloadExtFile.as_view(), name='download_ext_file'),

    path('callcenter/incoming_call', call_center.IncomingCallView.as_view(), name='callcenter.incoming_call'),
    path('callcenter/outgoing_call', call_center.OutgoingCallView.as_view(), name='callcenter.outgoing_call'),
    path('callcenter/call_answered', call_center.CallAnsweredView.as_view(), name='callcenter.call_answered'),

    # Product
    path('product/create_product/', product.CreateProductView.as_view(), name='product.create_product'),
    path('product/filter_product/', product.FilterProductView.as_view(), name='product.filter_product'),
    path('product/get_product/', product.GetProductView.as_view(), name='product.get_product'),
    path('product/update_product/', product.UpdateProductView.as_view(), name='product.update_product'),
    path('product/delete_product/', product.DeleteProductView.as_view(), name='product.delete_product'),

    # Sysconfig
    path('sysconfig/create_company_email/', system_configuration.CreateCompanyEmailView.as_view(),
         name='sysconfig.create_company_email'),
    path('sysconfig/filter_company_email/', system_configuration.FilterCompanyEmailView.as_view(),
         name='sysconfig.filter_company_email'),
    path('sysconfig/get_company_email/', system_configuration.GetCompanyEmailView.as_view(),
         name='sysconfig.get_company_email'),
    path('sysconfig/update_company_email/', system_configuration.UpdateCompanyEmailView.as_view(),
         name='sysconfig.update_company_email'),
    path('sysconfig/delete_company_email/', system_configuration.DeleteCompanyEmailView.as_view(),
         name='sysconfig.delete_company_email'),

    path('sysconfig/create_data_status/', system_configuration.CreateDataStatusView.as_view(),
         name='sysconfig.create_data_status'),
    path('sysconfig/filter_data_status/', system_configuration.FilterDataStatusView.as_view(),
         name='sysconfig.filter_data_status'),
    path('sysconfig/get_data_status/', system_configuration.GetDataStatusView.as_view(),
         name='sysconfig.get_data_status'),
    path('sysconfig/update_data_status/', system_configuration.UpdateDataStatusView.as_view(),
         name='sysconfig.update_data_status'),
    path('sysconfig/delete_data_status/', system_configuration.DeleteDataStatusView.as_view(),
         name='sysconfig.delete_data_status'),

    path('sysconfig/create_data_sub_status/', system_configuration.CreateDataSubStatusView.as_view(),
         name='sysconfig.create_data_sub_status'),
    path('sysconfig/filter_data_sub_status/', system_configuration.FilterDataSubStatusView.as_view(),
         name='sysconfig.filter_data_sub_status'),
    path('sysconfig/get_data_sub_status/', system_configuration.GetDataSubStatusView.as_view(),
         name='sysconfig.get_data_sub_status'),
    path('sysconfig/update_data_sub_status/', system_configuration.UpdateDataSubStatusView.as_view(),
         name='sysconfig.update_data_sub_status'),
    path('sysconfig/delete_data_sub_status/', system_configuration.DeleteDataSubStatusView.as_view(),
         name='sysconfig.delete_data_sub_status'),

    path('sysconfig/create_data_source/', system_configuration.CreateDataSourceView.as_view(),
         name='sysconfig.create_data_source'),
    path('sysconfig/filter_data_source/', system_configuration.FilterDataSourceView.as_view(),
         name='sysconfig.filter_data_source'),
    path('sysconfig/get_data_source/', system_configuration.GetDataSourceView.as_view(),
         name='sysconfig.get_data_source'),
    path('sysconfig/update_data_source/', system_configuration.UpdateDataSourceView.as_view(),
         name='sysconfig.update_data_source'),
    path('sysconfig/delete_data_source/', system_configuration.DeleteDataSourceView.as_view(),
         name='sysconfig.delete_data_source'),

    path('sysconfig/create_data_channel/', system_configuration.CreateDataChannelView.as_view(),
         name='sysconfig.create_data_channel'),
    path('sysconfig/filter_data_channel/', system_configuration.FilterDataChannelView.as_view(),
         name='sysconfig.filter_data_channel'),
    path('sysconfig/get_data_channel/', system_configuration.GetDataChannelView.as_view(),
         name='sysconfig.get_data_channel'),
    path('sysconfig/update_data_channel/', system_configuration.UpdateDataChannelView.as_view(),
         name='sysconfig.update_data_channel'),
    path('sysconfig/delete_data_channel/', system_configuration.DeleteDataChannelView.as_view(),
         name='sysconfig.delete_data_channel'),

    path('sysconfig/create_email_syntax/', system_configuration.CreateEmailSyntaxView.as_view(),
         name='sysconfig.create_email_syntax'),
    path('sysconfig/filter_email_syntax/', system_configuration.FilterEmailSyntaxView.as_view(),
         name='sysconfig.filter_email_syntax'),
    path('sysconfig/get_email_syntax/', system_configuration.GetEmailSyntaxView.as_view(),
         name='sysconfig.get_email_syntax'),
    path('sysconfig/update_email_syntax/', system_configuration.UpdateEmailSyntaxView.as_view(),
         name='sysconfig.update_email_syntax'),
    path('sysconfig/delete_email_syntax/', system_configuration.DeleteEmailSyntaxView.as_view(),
         name='sysconfig.delete_email_syntax'),

    path('sysconfig/create_email_template/', system_configuration.CreateEmailTemplateView.as_view(),
         name='sysconfig.create_email_template'),
    path('sysconfig/filter_email_template/', system_configuration.FilterEmailTemplateView.as_view(),
         name='sysconfig.filter_email_template'),
    path('sysconfig/get_email_template/', system_configuration.GetEmailTemplateView.as_view(),
         name='sysconfig.get_email_template'),
    path('sysconfig/update_email_template/', system_configuration.UpdateEmailTemplateView.as_view(),
         name='sysconfig.update_email_template'),
    path('sysconfig/delete_email_template/', system_configuration.DeleteEmailTemplateView.as_view(),
         name='sysconfig.delete_email_template'),

    path('sysconfig/create_company_log/', system_configuration.CreateCompanyLogoView.as_view(),
         name='sysconfig.create_company_log'),
    path('sysconfig/get_company_log/', system_configuration.GetCompanyLogoView.as_view(),
         name='sysconfig.get_company_log'),
    path('sysconfig/update_company_log/', system_configuration.UpdateCompanyLogoView.as_view(),
         name='sysconfig.update_company_log'),
    path('sysconfig/delete_company_log/', system_configuration.DeleteCompanyLogoView.as_view(),
         name='sysconfig.delete_company_log'),

    # Auth
    path('auth/get_user_info/', auth.AuthGetUserInfoView.as_view(), name='auth.get_user_info'),

    path('auth/login/', TokenObtainPairView.as_view(), name='auth.login'),
    path('auth/token/refresh/', TokenRefreshView.as_view()),

    # FB crawler
    path('fb/login/', crawl.FBLoginView.as_view(), name='data.fb_login'),
    path('fb/login/callback', crawl.FBLoginCallBackView.as_view(), name='data.fb_login_callback'),
    path('zalo/login/', crawl.ZaloLoginView.as_view(), name='data.zalo_login'),
    path('zalo/login/callback', crawl.ZaloLoginCallBackView.as_view(), name='data.zalo_login_callback'),
    path('data/filter_crawl_data/', data.FilterCrawlDataView.as_view(), name='data.filter_crawl_data'),
    path('data/create_order/', data.CreateOrderView.as_view(), name='data.create_order'),
    path('data/filter_order/', data.FilterOrderView.as_view(), name='data.filter_order'),
    path('data/get_order/', data.GetOrderView.as_view(), name='data.get_order'),
    path('data/update_order/', data.UpdateOrderView.as_view(), name='data.update_order'),
    path('data/delete_order/', data.DeleteOrderView.as_view(), name='data.delete_order'),
    path('data/create_order_detail/', data.CreateOrderDetailView.as_view(), name='data.create_order_detail'),
    path('data/filter_order_detail/', data.FilterOrderDetailView.as_view(), name='data.filter_order_detail'),
    path('data/get_order_detail/', data.GetOrderDetailView.as_view(), name='data.get_order_detail'),
    path('data/update_order_detail/', data.UpdateOrderDetailView.as_view(), name='data.update_order_detail'),
    path('data/delete_order_detail/', data.DeleteOrderDetailView.as_view(), name='data.delete_order_detail'),
    path('data/filter_order_history/', data.FilterOrderHistoryView.as_view(), name='data.filter_order_history'),
    path('data/filter_order_detail_history/', data.FilterOrderDetailHistoryView.as_view(), name='data.filter_order_detail_history'),
    path('data/bulk_update_order_status/', data.BulkUpdateOrderStatusView.as_view(), name='data.bulk_update_order_status'),
    path('data/bulk_update_order_pic/', data.BulkUpdateOrderPicView.as_view(), name='data.bulk_update_order_pic'),
    path('data/filter_fbpage/', data.FilterFBPageView.as_view(), name='data.filter_fbpage'),
    path('data/update_fbpage/', data.UpdateFBPageView.as_view(), name='data.update_fbpage'),
    path('data/delete_fbpage/', data.DeleteFBPageView.as_view(), name='data.delete_fbpage'),
    path('data/get_synchronized_fbaccount/', data.GetSynchronizedFBAccountView.as_view(), name='data.get_synchronized_fbaccount'),
    path('data/delete_synchronized_fbaccount/', data.DeleteSynchronizedFBAccountView.as_view(), name='data.delete_synchronized_fbaccount'),
    path('data/create_payment/', data.CreatePaymentView.as_view(), name='data.create_payment'),
    path('data/filter_payment/', data.FilterPaymentView.as_view(), name='data.filter_payment'),
    path('data/get_payment/', data.GetPaymentView.as_view(), name='data.get_payment'),
    path('data/update_payment/', data.UpdatePaymentView.as_view(), name='data.update_payment'),
    path('data/delete_payment/', data.DeletePaymentView.as_view(), name='data.delete_payment'),
    path('data/approve_payment/', data.ApprovePaymentView.as_view(), name='data.approve_payment'),
    path('data/disapprove_payment/', data.DisapprovePaymentView.as_view(), name='data.disapprove_payment')


] + static('files/', document_root=Const.FILE_ROOT)
