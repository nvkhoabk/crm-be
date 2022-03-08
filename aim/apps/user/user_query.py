"""
Definition of staff query.
"""


class UserQuery:

    def get_user_login_by_phone_number(self):
        """
        Get user by phone number
        :return:
        """
        result = """
            SELECT t.id, t.name, t.phone_number, t.password, t.group_role_id, t.group_user_code, t.mail, t.address, 
            t.avatar, t.is_active, t.created_at, t.created_by, t.updated_at, t.updated_by, g."name" as role_name,
            g.screen
            FROM "user" t
            left join group_role g on t.group_role_id = g.id
            where t.is_active = TRUE
            and t.phone_number = %s
        """
        return result

    def get_list_menu(self):
        """
        Get list menu
        :return:
        """
        result = """
            select t.title, t.href, t.icon
            from menu_web t
            where t.id in %s
            order by t.index_item asc
        """
        return result

    def get_user_id_by_phone_number(self):
        """
        Get user id by phone number
        :return:
        """
        result = """
            SELECT t.id, t.name, t.phone_number, t.group_role_id, r.code as role_code, r.name as role_name, 
            t.created_at, r.screen, t.group_user_code
            FROM "user" t
            left JOIN group_role r on t.group_role_id = r.id
            where t.phone_number = %s
            and t.is_active = TRUE
        """
        return result

    def get_user_id_by_phone_number_with_id(self):
        """
        Get user id by phone number and id
        :return:
        """
        result = """
            SELECT t.id
            FROM "user" t
            where t.phone_number = %s
            and t.id != %s
            and t.is_active = TRUE
        """
        return result

    def get_list_group_user(self):
        """
        Get list group user
        :return:
        """
        result = """
            SELECT t.id, t.code, t.name
            FROM group_user t
            order by t.index_sort asc
        """
        return result

    def search_user(self):
        """
        Search user
        :return:
        """
        result = """
            SELECT t.id, (row_number() OVER (ORDER BY t.updated_at desc)) as stt, t."name", t.phone_number, 
            t.group_role_id, gr."name" as role_name, t.group_user_code, gu.name as group_user_name, t.mail, t.address,
            t.created_by, TRUE as is_owner
            FROM "user" t
            left join group_role gr on gr.id = t.group_role_id
            left join group_user gu on gu.code = t.group_user_code
            where t.is_active = TRUE
        """
        return result

    def insert_user(self):
        """
        Insert user
        :return:
        """
        result = """
            insert into "user"
            (name, phone_number, password, group_role_id, group_user_code, mail, address, is_active, 
            created_at, created_by, updated_at, updated_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,TRUE,now(),%s,now(),%s)
        """
        return result

    def get_user_detail(self):
        """
        Get user detail
        :return:
        """
        result = """
            SELECT t.id, t.name, t.phone_number, t.group_role_id, t.group_user_code, t.mail, t.address, 
            concat(sc.value, case when t.avatar is not null then t.avatar else 'default.png' end) as avatar,
            t.created_at, t.created_by, t.updated_at, t.updated_by
            FROM "user" t
            left join group_user gu on t.group_user_code = gu.code
            left join system_conts sc on 1=1 and sc.code = 'url_image_file_root'
            where t.id = %s and group_user_code = %s
            limit 1
        """
        return result

    def update_user(self):
        """
        Update user
        :return:
        """
        result = """
            update "user" set name=%s,phone_number=%s,group_user_code=%s,mail=%s,address=%s,avatar=%s,
            updated_at=now(),updated_by=%s 
            where id=%s
        """
        return result

    def delete_user_by_admin(self):
        """
        Delete user by admin
        :return:
        """
        result = """
            update "user" set is_active = FALSE where id=%s
        """
        return result

    def delete_user_owner(self):
        """
        Delete user owner
        :return:
        """
        result = """
            update "user" set is_active = FALSE where id=%s and created_by = %s
        """
        return result



    # def get_staff_by_phone_number(self):
    #     """
    #     Get staff by phone number
    #     :return:
    #     """
    #     result = """
    #         select t.id, t.password as name
    #         from staff t
    #         where t.phone_number = %s
    #         and t.active = TRUE
    #     """
    #     return result
    #
    # def get_staff_by_phone_number_with_id(self):
    #     """
    #     Get staff by phone number with id
    #     :return:
    #     """
    #     result = """
    #         select t.id, t.password as name
    #         from staff t
    #         where t.phone_number = %s
    #         and t.id != %s
    #         and t.active = TRUE
    #     """
    #     return result
    #
    # def insert_staff(self):
    #     """
    #     Insert staff
    #     :return:
    #     """
    #     result = """
    #         insert into staff
    #         (name,phone_number,password,role_id,store_id,created_at,update_at,is_root, active, brand_id)
    #         VALUES (%s,%s,%s,%s,%s,now(),now(),%s, TRUE, %s ) RETURNING id
    #     """
    #     return result
    #
    # def insert_staff_forget_pass(self):
    #     """
    #     Insert staff forget pass
    #     :return:
    #     """
    #     result = """
    #         insert into staff_forget_pass
    #         (phone_number,new_pass, session_info) VALUES (%s,%s, %s)
    #     """
    #     return result
    #
    # def check_staff_active_pass_code(self):
    #     """
    #     Check active pass code
    #     :return:
    #     """
    #     result = """
    #         SELECT t.id, t.new_pass as name, t.session_info
    #         from staff_forget_pass t
    #         where t.phone_number = %s
    #     """
    #     return result
    #
    # def active_staff_pass(self):
    #     """
    #     Active staff pass
    #     :return:
    #     """
    #     result = """
    #         update staff set password = %s where phone_number = %s
    #     """
    #     return result
    #
    # def delete_code_active_pass(self):
    #     """
    #     Delete code active pass
    #     :return:
    #     """
    #     result = """
    #         delete from staff_forget_pass where phone_number = %s
    #     """
    #     return result
    #

    #
    # def search_staff(self):
    #     """
    #     Search staff
    #     :return:
    #     """
    #     result = """
    #         select t.id, t.name, t.phone_number, r.name as role_name, s.name as store_name, t.created_at
    #         from staff t
    #         left JOIN group_role r on t.role_id = r.id
    #         left JOIN store s on t.store_id = s.id
    #         where t.is_root != TRUE
    #         and t.active = TRUE
    #     """
    #     return result
    #
    # def search_admin_staff_with_paging(self):
    #     """
    #     Search admin staff with paging
    #     :return:
    #     """
    #     result = """
    #         select count(t.id) as id, '' as name
    #         from staff t
    #         left JOIN group_role r on t.role_id = r.id
    #         left JOIN store s on t.store_id = s.id
    #         where t.is_root != TRUE
    #         and t.active = TRUE
    #     """
    #     return result
    #
    # def get_staff_by_id(self):
    #     """
    #     Get staff by id
    #     :return:
    #     """
    #     result = """
    #         select t.id, t.name, t.phone_number, t.role_id, r.name as role_name, r.screen, t.store_id, s.name as store_name,
    #         t.brand_id, s.city_id, t.is_root, t.is_super
    #         from staff t
    #         left JOIN group_role r on t.role_id = r.id
    #         LEFT JOIN store s on t.store_id = s.id
    #         left join brand b on t.brand_id = b.id
    #         where t.id = %s
    #     """
    #     return result
    #
    # def get_staff_by_id_and_store(self):
    #     """
    #     Get staff by id and store id
    #     :return:
    #     """
    #     result = """
    #         select t.id, t.name, t.phone_number, t.role_id, r.name as role_name, r.screen, t.store_id,
    #         s.name as store_name, t.brand_id, s.city_id, t.is_root, t.is_super
    #         from staff t
    #         INNER JOIN group_role r on t.role_id = r.id
    #         LEFT JOIN store s on t.store_id = s.id
    #         left join brand b on t.brand_id = b.id
    #         where t.id = %s and t.store_id = %s
    #     """
    #     return result
    #

    # def delete_staff(self):
    #     """
    #     Delete staff
    #     :return:
    #     """
    #     result = """
    #         update staff set active = FALSE  where id = %s
    #     """
    #     return result
    #
    # def check_store_to_delete(self):
    #     """
    #     Check store to delete
    #     :return:
    #     """
    #     result = """
    #         SELECT t.id, '' as name
    #         from staff t
    #         where t.id = %s
    #         and t.store_id in (select store_id from staff where id = %s)
    #     """
    #     return result
    #
    # def get_staff_by_id_check(self):
    #     """
    #     Get staff by id: use check
    #     :return:
    #     """
    #     result = """
    #         select t.id, t.password as name  from staff t where t.id = %s
    #     """
    #     return result
    #
    # def update_new_staff_pass(self):
    #     """
    #     Update new pass
    #     :return:
    #     """
    #     result = """
    #         update staff set password = %s where id = %s
    #     """
    #     return result
