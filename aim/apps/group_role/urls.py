"""
Definition of urlpatterns.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Search
    path('list', views.list_role, name='list_role'),

    # Get master screen
    path('get-list-screen', views.get_list_screen, name='get_list_screen'),

    # Get detail
    path('<int:id>', views.detail_group_role, name='detail_group_role'),

    # Add
    path('add', views.add_group_role, name='add_group_role'),

    # Update
    path('update', views.update_group_role, name='update_group_role'),

    # Delete
    path('delete/<int:id>', views.delete_group_role, name='delete_group_role'),

    # Get list group role options
    path('get-group-role-option', views.get_group_role_option, name='get_group_role_option'),
]
