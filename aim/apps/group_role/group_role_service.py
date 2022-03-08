"""
    Define of role service
"""
from rest_framework import status
from django.db import connection
import json
import ast
from aim.apps.group_role.group_role_query import RoleQuery
from aim.apps.common.common import Common
from aim.apps.common.response import Response
from aim.const import Const
from aim.message import Message


class RoleService:

    def list(self, request):
        """
        Search role list
        :return:
        """
        try:
            # Injection require object
            common = Common()
            role_query = RoleQuery()
            cursor = connection.cursor()

            # Get params from request
            user_id = request.COOKIES['id']
            group_code = request.COOKIES['group_user_code']

            # Get from DB and Handle data
            if group_code != Const.GROUP_ADMIN_SYSTEM:
                cursor.execute(role_query.list_by_group_user(), [group_code])
                roles = common.dictfetchall(cursor)

                for role in roles:
                    if group_code == role['group_user_code']:
                        if role['created_by'] == user_id:
                            role['is_owner'] = True
                        else:
                            role['is_owner'] = False
            else:
                cursor.execute(role_query.list_by_admin())
                roles = common.dictfetchall(cursor)

            response = Response(data=roles, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def get_list_screen(self, request):
        """
        Get list screen
        :return:
        """
        try:
            # Injection require object
            common = Common()
            role_query = RoleQuery()
            cursor = connection.cursor()

            # Get params from request
            group_user_code = request.COOKIES['group_user_code']
            owner_screen = request.COOKIES['screen']

            # Get list screen
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                cursor.execute(role_query.get_list_screen())
                screens = common.dictfetchall(cursor)
            else:
                owner_screen = ast.literal_eval(owner_screen)
                owner_screen = set(owner_screen)
                owner_screen = tuple(owner_screen)
                cursor.execute(role_query.get_list_screen_by_list_id(), [owner_screen])
                screens = common.dictfetchall(cursor)

            # Handle data
            screens = self.handle_list_screen(screens)

            response = Response(data=screens, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def handle_list_screen(self, screens):
        """
        Handle list screens
        """
        # Get list group
        groups = []
        for screen in screens:
            if screen["group"] not in groups:
                groups.append(screen["group"])

        # Handle screen
        result = []
        for group in groups:
            group_temp = {
                "group_name": str(group)
            }
            items = []
            for screen in screens:
                if screen["group"] == group and screen["href"] is not None:
                    item = {
                        "screen_id": screen["id"]
                        , "screen_name": screen["title"]
                    }
                    items.append(item)
            group_temp["screen"] = items

            result.append(group_temp)

        return result

    def detail_group_role(self, request, id):
        """
        Detail group role
        :return:
        """
        try:
            # Injection require object
            common = Common()
            role_query = RoleQuery()
            cursor = connection.cursor()

            # Get params from request
            group_user_code = request.COOKIES['group_user_code']

            # Get data from db
            role = None
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                cursor.execute(role_query.detail_group_role(), [id])
                roles = common.dictfetchall(cursor)
            else:
                cursor.execute(role_query.detail_group_role_by_group_user(), [id, group_user_code])
                roles = common.dictfetchall(cursor)

            if len(roles) > 0:
                role = roles[0]
                if role:
                    role['screen'] = ast.literal_eval(role['screen'])

            response = Response(data=role, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def add_group_role(self, request):
        """
        Add group role
        :return:
        """
        try:
            # Injection require object
            common = Common()
            role_query = RoleQuery()
            cursor = connection.cursor()

            # Get params from request
            params = json.loads(request.body)
            group_user_code = request.COOKIES['group_user_code']
            user_id = request.COOKIES['id']
            group_user_code_input = group_user_code
            is_root = False

            # Check exist role
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                cursor.execute(role_query.check_exist_role_when_add_by_admin(), [params["code"], params["name"]])
                roles = common.dictfetchall(cursor)

                group_user_code_input = params["group_user_code"]
                is_root = True
            else:
                cursor.execute(role_query.check_exist_role_when_add(),
                               [group_user_code, params["code"], params["name"]])
                roles = common.dictfetchall(cursor)
            if len(roles) > 0:
                return Response(mess=Message.CODE_OR_NAME_ROLE_IS_EXIST, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Insert into db
            cursor.execute(role_query.add_group_role(), [params["code"], params["name"], user_id, user_id,
                                                         str(params["screen"]), group_user_code_input, is_root])

            response = Response(data=None, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def update_group_role(self, request):
        """
        Update group role
        :return:
        """
        try:
            # Injection require object
            common = Common()
            role_query = RoleQuery()
            cursor = connection.cursor()

            # Get params from request
            params = json.loads(request.body)
            group_user_code = request.COOKIES['group_user_code']
            user_id = request.COOKIES['id']
            group_user_code_input = group_user_code

            # Check exist role
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                cursor.execute(role_query.check_exist_role_when_update_by_admin(),
                               [params["code"], params["name"], params["id"]])
                roles = common.dictfetchall(cursor)

                group_user_code_input = params["group_user_code"]
            else:
                cursor.execute(role_query.check_exist_role_when_update(),
                               [group_user_code, params["code"], params["name"], params["id"]])
                roles = common.dictfetchall(cursor)

            if len(roles) > 0:
                return Response(mess=Message.CODE_OR_NAME_ROLE_IS_EXIST, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Update data in db
            cursor.execute(role_query.update(), [params["code"], params["name"], str(params["screen"]),
                                                 group_user_code_input, user_id, params["id"], group_user_code, user_id])

            response = Response(data=None, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def delete_group_role(self, request, id):
        """
        Delete group role
        :return:
        """
        try:
            # Injection require object
            role_query = RoleQuery()
            cursor = connection.cursor()
            common = Common()

            # Get params from request
            user_id = request.COOKIES['id']
            group_user_code = request.COOKIES['group_user_code']

            # Check role applying for user
            cursor.execute(role_query.check_role_applying(), [id])
            roles = common.dictfetchall(cursor)
            if len(roles) > 0:
                return Response(mess=Message.ROLE_IS_APPLYING, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Check role to delete
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                # Delete from db
                cursor.execute(role_query.delete_group_role_by_admin(), [id])
            else:
                # Chỉ được xóa group role mình tạo ra
                cursor.execute(role_query.delete_group_role_by_owner(), [id, user_id])

            response = Response(status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def get_group_role_option(self, request):
        """
        Get group role option
        :return:
        """
        try:
            # Injection require object
            role_query = RoleQuery()
            cursor = connection.cursor()
            common = Common()

            # Get params from request
            group_user_code = request.COOKIES['group_user_code']

            # Check exist role
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                # Get all group role
                cursor.execute(role_query.get_list_group_role_option_by_admin())
                roles = common.dictfetchall(cursor)
            else:
                # Get list group role owner by group user
                cursor.execute(role_query.get_list_group_role_option_by_group_user(), [group_user_code])
                roles = common.dictfetchall(cursor)

            response = Response(data=roles, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response
