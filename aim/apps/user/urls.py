"""
Definition of urlpatterns.
"""

from django.urls import path
from . import views

urlpatterns = [

    # Login
    path('login', views.user_login, name='user_login'),

    # Get list group user
    path('get-list-group-user', views.get_list_group_user, name='get_list_group_user'),

    # Search user
    path('search', views.search_user, name='search_user'),

    # Add user
    path('add', views.add_user, name='add_user'),

    # Get detail
    path('<int:id>', views.get_user_detail, name='get_user_detail'),

    # Update staff
    path('update', views.update_user, name='update_user'),

    # Delete user
    path('delete/<int:id>', views.delete_user, name='delete_user'),


    # # Update pass
    # path('update-pass', views.update_pass, name='update_pass'),
    #
    # # Active pass
    # path('active-pass', views.active_pass, name='active_pass'),
    #
    # # Change pass
    # path('change-pass', views.change_pass_staff, name='change_pass_staff'),




]
