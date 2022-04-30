from api.models.organization import Company, Department, Role, Permission, UserRole
from groups_manager.models import Group, GroupType, Member
from api.services import exceptions
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64


def get_company_group_name(id):
    return 'company_%d' % id


def get_company_admins_group(id):
    return 'company_%d_admin' % id


def has_company_permisison(user, *args, **kwargs):
    company_id = kwargs.get('company_id', 0)
    department_id = kwargs.get('department_id', 0)
    role_id = kwargs.get('role_id', 0)
    permission_id = kwargs.get('permission_id', 0)
    target_user = kwargs.get('target_user', None) 

    if user.is_superuser:
        return True

    if company_id:    
        pass
    elif department_id:
        try:
            department = Department.objects.get(pk=department_id)
            company_id = department.company.id
        except Department.DoesNotExist:
            raise exceptions.ManageDepartmentNotFound()
    elif role_id:
        try:
            role = Role.objects.get(pk=role_id)
            company_id = role.company.id
        except Role.DoesNotExist:
            raise exceptions.ManageRoleNotFound()
    elif permission_id:
        try:
            permisison = Permission.objects.get(pk=permission_id)
            company_id = permisison.company.id
        except Permission.DoesNotExist:
            raise exceptions.ManagePermissionNotFound() 
    elif target_user:
        user_role = UserRole.objects.filter(
            user=target_user,
        ).first()
        if not user_role:
            raise exceptions.PermissionDenied()
        company_id = user_role.company.id
    else:
        raise exceptions.PermissionDenied() 
    
    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        raise ManageCompanyNotFound()
 
    group_admins = Group.objects.get(name=get_company_admins_group(company_id))

    try:
        member = Member.objects.get(django_user=user)
    except Member.DoesNotExist:
        raise PermissionDenied()
    if member.has_perm('change_company', company):
        return True
    raise PermissionDenied()


class AESCipher:
    
    BS = 32

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:])).decode('utf8')

    def unpad(self, s):
        return s[0:-ord(s[-1:])]

    def pad(self, s):
        return bytes(s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS), 'utf-8')
