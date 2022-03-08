"""
Definition of staff service.
"""
import json
from django.db import connection
from rest_framework import status
from django.db import transaction
import requests
import ast
from aim.apps.common.common import Common
from aim.apps.common.response import Response
from aim.apps.user.user_query import UserQuery
from aim.const import Const
from aim.message import Message


class UserService:

    def user_login(self, request):
        """
        user login
        :param request:
        :return:
        """
        try:
            # Inject require object
            user_query = UserQuery()
            common = Common()
            cursor = connection.cursor()

            # Get and check params
            request_body = json.loads(request.body)
            phone_number = request_body['phone_number']
            password = request_body['password']

            # Check login info
            if self.check_user_infor(phone_number, password):
                # Get user by phone from db
                cursor.execute(user_query.get_user_login_by_phone_number(), [phone_number])
                user_db = common.dictfetchall(cursor)
                if user_db is not None and len(list(user_db)) > 0:
                    user = user_db[0]
                    hash_pass = user['password']

                    if common.check_password_hash(hash_pass, password):
                        # Gen customer's token
                        access_token = common.gen_access_token(phone_number)

                        # Get menu
                        menu = self.get_menu_by_user(user['screen'], cursor, common, user_query)

                        result = {"token": access_token, "user_info": user, "menu": menu}

                        response = Response(data=result, mess=Message.SUCCESS, status=status.HTTP_200_OK)
                    else:
                        response = Response(mess=Message.USER_NOT_VALID, status=status.HTTP_403_FORBIDDEN)
                else:
                    response = Response(mess=Message.USER_NOT_VALID, status=status.HTTP_403_FORBIDDEN)
            else:
                response = Response(mess=Message.USER_NOT_VALID, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def check_user_infor(self, phone_number, password):
        """
        Check user name and password
        :param phone_number:
        :param password:
        :return:
        """
        if(phone_number != "" and phone_number is not None and password != "" and password is not None):
            return True
        return False

    def get_menu_by_user(self, screens, cursor, common, user_query):
        """
        Get menu by user
        :return:
        """
        result = []

        if not screens:
            return result

        # Get master screen
        screens = ast.literal_eval(screens)
        screens = set(screens)
        screens = tuple(screens)
        cursor.execute(user_query.get_list_menu(), [screens])
        result = common.dictfetchall(cursor)

        # # Get screen by role user
        # for screen in db_screens:
        #     item = {
        #         "title": screen["title"],
        #         "href": screen["href"],
        #         "icon": screen["icon"]
        #     }

        return result

    def get_list_group_user(self, request):
        """
        Get list group user
        :param request:
        :return:
        """
        try:
            # Inject require object
            user_query = UserQuery()
            common = Common()
            cursor = connection.cursor()

            # Get list group user
            cursor.execute(user_query.get_list_group_user())
            group_user = common.dictfetchall(cursor)

            response = Response(data=group_user, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def search_user(self, request):
        """
        Search user
        :param request:
        :return:
        """
        try:
            # Inject require params
            common = Common()
            cursor = connection.cursor()
            user_query = UserQuery()

            condition_search = " "

            # Get params from request
            user = json.loads(request.body)
            group_user_code_root = request.COOKIES['group_user_code']
            user_id = request.COOKIES['id']

            user_name = user['name']
            if user_name:
                condition_search = condition_search + " and lower(t.name) like " + "'%%" + user_name.replace("%","").lower() + "%%'"

            phone_number = user['phone_number']
            if phone_number:
                condition_search = condition_search + " and t.phone_number like " + "'%%" + phone_number.replace("%","") + "%%'"

            group_role_id = user['group_role_id']
            if group_role_id:
                condition_search = condition_search + " and t.group_role_id = '" + str(group_role_id) + "'"

            group_user_code = user['group_user_code']
            if group_user_code:
                condition_search = condition_search + " and t.group_user_code = '" + str(group_user_code) + "'"

            # Check group
            # if group_user_code_root != Const.GROUP_ADMIN_SYSTEM:
            #     condition_search = condition_search + " and t.group_user_code = '" + str(group_user_code_root) + "'"

            base_query = user_query.search_user() + condition_search + " order by t.updated_at desc"

            # Use for paging
            limit = request.GET.get("limit", None)
            offset = request.GET.get("offset", None)
            suffixes = common.get_row_index_by_offset_and_limit(offset, limit)

            # Query db: Get users
            base_query = base_query + suffixes
            cursor.execute(base_query + suffixes)
            users = common.dictfetchall(cursor)

            # Handle data
            if group_user_code_root != Const.GROUP_ADMIN_SYSTEM:
                for user in users:
                    if user['created_by'] == user_id:
                        user['is_owner'] = True
                    else:
                        user['is_owner'] = False

            # Query db: Get total page
            cursor.execute(base_query)
            total_row_db = common.dictfetchall(cursor)
            total_row = len(total_row_db)

            result = {"users": users, "total_row": total_row}

            response = Response(data=result, mess=Message.SUCCESS, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def add_user(self, request):
        """
        Add user
        :param request:
        :return:
        """
        try:
            # Inject require object
            common = Common()
            cursor = connection.cursor()
            user_query = UserQuery()

            # Get user information from request
            user = json.loads(request.body)
            user_id = request.COOKIES['id']
            group_user_code_root = request.COOKIES['group_user_code']
            group_user_code = user['group_user_code']

            # Check group user root
            if group_user_code_root != Const.GROUP_ADMIN_SYSTEM:
                group_user_code = group_user_code_root

            # check info register is not empty and email is not exist
            check_object = self.check_user_infor_register(user, cursor, user_query, common)
            if check_object is not None:
                return check_object

            # Hash password
            password_hash = common.hash_password(user['password'])

            # Insert user to db
            cursor.execute(user_query.insert_user(), [user['name'], user['phone_number'], password_hash,
                user['group_role_id'], group_user_code, user['mail'], user['address'], user_id, user_id])

            response = Response(mess=Message.SUCCESS, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def check_user_infor_register(self, user, cursor, user_query, common):
        """
        Check information register
        :param user:
        :return:
        """
        result = None

        if user is not None and user['phone_number'] != "" and user['phone_number'] is not None:
            # check email exist
            cursor.execute(user_query.get_user_id_by_phone_number(), [user['phone_number']])
            user_db = common.dictfetchall(cursor)
            if len(user_db) > 0:
                # Phone number is exist
                result = Response(mess=Message.PHONE_NUMBER_IS_EXIST, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            result = Response(mess=Message.REQUEST_BODY_WRONG_FORMAT, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return result

    def get_user_detail(self, request, id):
        """
        Get user detail
        :param request:
        :param id:
        :return:
        """
        try:
            # Inject require object
            common = Common()
            cursor = connection.cursor()
            user_query = UserQuery()

            # Get params from request
            user_id = request.COOKIES['id']
            group_user_code_root = request.COOKIES['group_user_code']
            cursor.execute(user_query.get_user_detail(), [id, group_user_code_root])
            users = common.dictfetchall(cursor)
            user = None
            if len(users) > 0:
                user = users[0]

            response = Response(data=user, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def update_user(self, request):
        """
        Update user
        :param request:
        :return:
        """
        try:
            # Inject require object
            common = Common()
            cursor = connection.cursor()
            user_query = UserQuery()

            # Get user information from request
            avatar = request.FILES.get("image", None)
            user_id = request.COOKIES['id']
            phone_number = request.POST.get("phone_number")
            name = request.POST.get("name")
            mail = request.POST.get("mail")
            address = request.POST.get("address")
            role_name = request.POST.get("role_name")
            group_user_code_root = request.COOKIES['group_user_code']

            user = {
                "id": user_id,
                "name": name,
                "phone_number": phone_number,
                "mail": mail,
                "address": address,
                "role_name": role_name,
            },

            if 'group_user_code' in user:
                group_user_code = user['group_user_code']

            # Check group user root
            if group_user_code_root != Const.GROUP_ADMIN_SYSTEM:
                group_user_code = group_user_code_root
            user = user[0]
            # check info register is not empty and email is not exist
            check_object = self.check_user_infor_update(user, cursor, user_query, common)
            if check_object is not None:
                return check_object

            image_name = None
            if avatar is not None:
                # Upload new image
                image_name = common.upload_image(avatar, "files/images/")

            # Insert customer to db
            cursor = connection.cursor()
            user_query = UserQuery()

            cursor.execute(user_query.update_user(), [user['name'], user['phone_number'],
                group_user_code, user['mail'], user['address'], image_name, user_id, user['id']])

            response = Response(mess=Message.SUCCESS, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    def check_user_infor_update(self, user, cursor, user_query, common):
        """
        Check information when update
        :param user:
        :return:
        """
        result = None

        if user is not None and user['id'] != "" and user['id'] is not None and user['phone_number'] != "" and user['phone_number'] is not None:
            # check email exist
            cursor.execute(user_query.get_user_id_by_phone_number_with_id(), [user['phone_number'], user['id']])
            user_db = common.dictfetchall(cursor)
            if user_db is not None and len(user_db) > 0:
                # Phone number is exist
                result = Response(mess=Message.PHONE_NUMBER_IS_EXIST, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            result = Response(mess=Message.REQUEST_BODY_WRONG_FORMAT, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return result

    def delete_user(self, request, id):
        """
        Delete user
        :param request:
        :param id:
        :return:
        """
        try:
            # Inject require object
            cursor = connection.cursor()
            user_query = UserQuery()

            # Get user information from request
            user_id = request.COOKIES['id']
            group_user_code = request.COOKIES['group_user_code']

            # Check role to delete
            if group_user_code == Const.GROUP_ADMIN_SYSTEM:
                cursor.execute(user_query.delete_user_by_admin(), [id])
            else:
                # Chỉ được xóa user mình tạo ra
                cursor.execute(user_query.delete_user_owner(), [id, user_id])

            response = Response(mess=Message.SUCCESS, status=status.HTTP_200_OK)
        except Exception as e:
            response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response

    # def get_user_by_phone_number(self, phone_number):
    #     """
    #     Get user information by phone number
    #     :param phone_number:
    #     :return:
    #     """
    #     user_query = UserQuery()
    #     user = COMMON.objects.raw(user_query.get_user_by_phone_number(), [phone_number])
    #     return user
    #
    # def get_user_by_phone_number_with_id(self, id, phone_number):
    #     """
    #     Get user information by phone number
    #     :param phone_number:
    #     :param id:
    #     :return:
    #     """
    #     user_query = UserQuery()
    #     user = COMMON.objects.raw(user_query.get_user_by_phone_number_with_id(), [phone_number, id])
    #     return user
    #
    #
    #
    #
    # def get_list_app_user_can_be_access(self, screens, cursor, user_query, common):
    #     """
    #     Get list app user can be access
    #     :return:
    #     """
    #     cursor.execute(user_query.get_master_menu_for_app())
    #     db_screens = common.dictfetchall(cursor)
    #
    #     screens = ast.literal_eval(screens)
    #     screen_of_user = []
    #     for screen in db_screens:
    #         if screen["id"] in screens:
    #             screen_of_user.append(screen)
    #
    #     return screen_of_user
    #
    #
    # def check_code_in_list_code(self, codes, code):
    #     """
    #     Check code contain list code
    #     :param codes:
    #     :param code:
    #     :return:
    #     """
    #     for code_temp in codes:
    #         if code_temp['code'] == code:
    #             return True
    #
    #     return False
    #
    #
    # def convert_bytes_to_json(self, my_bytes_value):
    #     """
    #     Convert bytes to input
    #     :param bytes:
    #     :return:
    #     """
    #     my_json = my_bytes_value.decode('utf8').replace("'", '"')
    #     data = json.loads(my_json)
    #
    #     return data
    #
    # def send_sms_message(self, phone_number, captcha):
    #     """
    #     Send sms message
    #     :return:
    #     """
    #     headers = {
    #         'content-type': 'application/json',
    #     }
    #     params = (
    #         ('key', Const.FIRE_BASE_API_KEY),
    #     )
    #
    #     if (phone_number[:1] == "0"):
    #         phone_number = "+84" + phone_number[1:]
    #
    #     data = "{'phoneNumber': '" + phone_number + "', 'recaptchaToken': '" + captcha + "'}"
    #     r = requests.post('https://www.googleapis.com/identitytoolkit/v3/relyingparty/sendVerificationCode',
    #                       headers=headers, params=params, data=data)
    #
    #     if (r.status_code != 200):
    #         return None
    #
    #     session_info = self.convert_bytes_to_json(r.content)
    #     session_info = session_info["sessionInfo"]
    #
    #     return session_info
    #
    #
    # def update_pass(self, request):
    #     """
    #     Update new pass word
    #     :param request:
    #     :return:
    #     """
    #     # Get user information from request
    #     user = json.loads(request.body)
    #     cursor = connection.cursor()
    #     user_query = UserQuery()
    #
    #     try:
    #         # check phone number
    #         user_db = self.get_user_by_phone_number(user['phone_number'])
    #         if(len(list(user_db)) == 0):
    #             return Response(mess=Message.PHONE_NUMBER_IS_NOT_EXIST, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    #
    #         # Send code active to phone number
    #         session_info = self.send_sms_message(user['phone_number'], user['captcha'])
    #         if (session_info is None):
    #             return Response(mess=Message.RECAPCHA_INVALID, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    #
    #         # Save user info into db
    #         cursor.execute(user_query.insert_user_forget_pass(), [user['phone_number'], user['new_pass'], session_info])
    #
    #         response = Response(mess=Message.SUCCESS, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #     return response
    #
    # def check_code_is_correct(self, session_info, code):
    #     """
    #     Check code is correct
    #     :param code:
    #     :return:
    #     """
    #     headers = {
    #         'content-type': 'application/json',
    #     }
    #     params = (
    #         ('key', Const.FIRE_BASE_API_KEY),
    #     )
    #
    #     data = "{'sessionInfo': '" + session_info + "', 'code': '" + code + "'}"
    #     r = requests.post('https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPhoneNumber',
    #                       headers=headers, params=params, data=data)
    #
    #     result = True
    #     if(r.status_code != 200):
    #         result = False
    #     return result
    #
    #
    # def active_user_pass(self, request):
    #     """
    #     Active user pass
    #     :param request:
    #     :return:
    #     """
    #     try:
    #         # Get user information from request
    #         user = json.loads(request.body)
    #
    #         # Check code in data base
    #         cursor = connection.cursor()
    #         common = Common()
    #         user_query = UserQuery()
    #
    #         cursor.execute(user_query.check_user_active_pass_code(), [user['phone_number']])
    #         object_check = common.dictfetchall(cursor)
    #
    #         if(len(list(object_check)) > 0):
    #             # Check code is correct
    #             flag_check = self.check_code_is_correct(object_check[0]['session_info'], user['code'])
    #             if (flag_check):
    #
    #                 # Hash password
    #                 new_pass = object_check[0]['name']
    #                 common = Common()
    #                 password_hash = common.hash_password(new_pass)
    #
    #                 with transaction.atomic():
    #                     # Set active user
    #                     cursor = connection.cursor()
    #                     cursor.execute(user_query.active_user_pass(), [password_hash, user['phone_number']])
    #
    #                     # Delete code active in data base
    #                     cursor.execute(user_query.delete_code_active_pass(), [user['phone_number']])
    #
    #                 response = Response(status=status.HTTP_200_OK)
    #             else:
    #                 response = Response(mess=Message.CODE_NOT_RIGHT, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    #         else:
    #             response = Response(mess=Message.USER_NOT_VALID, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    #
    #     except Exception as e:
    #         response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     return response
    #
    #
    # def change_pass(self, request):
    #     """
    #     Update new pass word
    #     :param request:
    #     :return:
    #     """
    #     try:
    #         # Get customer information from request
    #         id = request.COOKIES['id']
    #         user = json.loads(request.body)
    #         user_query = UserQuery()
    #
    #         # check old pass
    #         user_db = COMMON.objects.raw(user_query.get_user_by_id_check(), [id])
    #         if (len(list(user_db)) > 0):
    #             hash_pass = user_db[0].name
    #             common = Common()
    #             if (common.check_password_hash(hash_pass, user['old_password'])):
    #
    #                 # Hash new password
    #                 new_password_hash = common.hash_password(user['new_password'])
    #
    #                 # Update new pass
    #                 cursor = connection.cursor()
    #                 cursor.execute(user_query.update_new_user_pass(), [new_password_hash, id])
    #
    #                 response = Response(mess=Message.SUCCESS, status=status.HTTP_200_OK)
    #             else:
    #                 response = Response(mess=Message.OLD_PASS_NOT_RIGHT, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    #         else:
    #             response = Response(mess=Message.CUSTOMER_ID_NOT_RIGHT, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    #     except Exception as e:
    #         response = Response(mess=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    #
    #     return response



    # def check_store_to_delete(self, user_login_id, user_id):
    #     """
    #     Check store to delete
    #     :param user_login_id:
    #     :param user_id:
    #     :return:
    #     """
    #     user_query = UserQuery()
    #     users = COMMON.objects.raw(user_query.check_store_to_delete(), [user_login_id, user_id])
    #     if (len(list(users)) > 0):
    #         return True
    #     return False
    #


