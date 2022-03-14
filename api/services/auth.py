from api.common.base_service import BaseService
from api.common.cookies import Cookies
from django.contrib.auth import authenticate, login, logout
from api.services.exceptions import AuthLoginInvalid, AuthLogoutNotLoggedIn


class AuthLoginService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        user = authenticate(**kwargs)
        if user is None:
            raise AuthLoginInvalid()
        login(request, user)
        return user


class AuthLogoutService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        if not request.user.is_authenticated:
            raise AuthLogoutNotLoggedIn()
        logout(request)
