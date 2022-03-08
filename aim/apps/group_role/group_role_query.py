"""
Definition of role query.
"""


class RoleQuery:

    def list_by_group_user(self):
        """
        Get list group role by group user
        :return:
        """
        result = """
            SELECT t.id, (row_number() OVER (ORDER BY t.updated_at desc)) as stt, t.code, t.name, t.created_by, 
            t.group_user_code
            FROM group_role t
            where t.group_user_code = %s
            order by t.updated_at desc
        """
        return result

    def list_by_admin(self):
        """
        Get list role by admin
        :return:
        """
        result = """
            SELECT t.id, (row_number() OVER (order by t.is_root desc, t.updated_at desc)) as stt, t.code, t.name, t.created_by, 
            t.group_user_code, TRUE as is_owner
            FROM group_role t
            order by t.is_root desc, t.updated_at desc
        """
        return result

    def get_list_screen(self):
        """
        Get list screen
        :return:
        """
        result = """
            SELECT t.id, t.title, t.group, t.href
            FROM menu_web t
            order by t.index_item asc
        """
        return result

    def get_list_screen_by_list_id(self):
        """
        Get list screen by list id
        :return:
        """
        result = """
            SELECT t.id, t.title, t.group, t.href
            FROM menu_web t
            where id in %s
            order by t.index_item asc
        """
        return result

    def detail_group_role(self):
        """
        Detail role
        :return:
        """
        result = """
            SELECT t.id, t.code, t.name, t.screen, t.group_user_code
            FROM group_role t
            where t.id = %s
            limit 1
        """
        return result

    def detail_group_role_by_group_user(self):
        """
        Detail role
        :return:
        """
        result = """
            SELECT t.id, t.code, t.name, t.screen, t.group_user_code
            FROM group_role t
            where t.id = %s
            and t.group_user_code = %s
            limit 1
        """
        return result

    def add_group_role(self):
        """
        Add group role
        :return:
        """
        result = """
            insert into group_role
            (code, name, created_at, created_by, updated_at, updated_by, screen, group_user_code, is_root)
            values
            (%s, %s, now(), %s, now(), %s, %s, %s, %s)
        """
        return result

    def check_exist_role_when_add_by_admin(self):
        """
        Check exist role when add by admin
        :return:
        """
        result = """
            select t.id
            from group_role t
            where t.code = %s 
            or t.name =%s
            limit 1
        """
        return result

    def check_exist_role_when_add(self):
        """
        Check exist role when add
        :return:
        """
        result = """
            select t.id
            from group_role t
            where t.group_user_code = %s
            and (t.code = %s or t.name =%s)
            limit 1
        """
        return result

    def update(self):
        """
        Update role
        :return:
        """
        result = """
            update group_role
            set code = %s, name = %s, screen = %s, group_user_code = %s, updated_at = now(), updated_by = %s
            where id = %s
            and (%s = 'ADMIN' or created_by = %s)
        """
        return result

    def check_exist_role_when_update_by_admin(self):
        """
        Check exist role when update by admin
        :return:
        """
        result = """
            select t.id
            from group_role t
            where (t.code = %s or t.name = %s)
            and t.id != %s
            limit 1
        """
        return result

    def check_exist_role_when_update(self):
        """
        Check exist role when update
        :return:
        """
        result = """
            select t.id
            from group_role t
            where t.group_user_code = %s
            and (t.code = %s or t.name =%s)
            and t.id != %s
            limit 1
        """
        return result

    def get_list_group_role_option_by_admin(self):
        """
        Get list group role option by admin
        :return:
        """
        result = """
            SELECT t.id as value, t.name as text
            FROM "group_role" t
            where t.is_root = True
        """
        return result

    def get_list_group_role_option_by_group_user(self):
        """
        Get list group role option by group user
        :return:
        """
        result = """
            SELECT t.id as value, t.name as text
            FROM "group_role" t
            where t.group_user_code = %s
        """
        return result

    def check_role_applying(self):
        """
        Check role applying
        :return:
        """
        result = """
            select t.id
            from "user" t
            where t.group_role_id = %s
            and t.is_active = TRUE 
            limit 1
        """
        return result

    def delete_group_role_by_admin(self):
        """
        Delete group role by admin
        :return:
        """
        result = """
            delete from group_role where id = %s
        """
        return result

    def delete_group_role_by_owner(self):
        """
        Delete group role by owner
        :return:
        """
        result = """
            delete from group_role where id = %s and created_by = %s
        """
        return result
