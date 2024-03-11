from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections

from channels.auth import AuthMiddleware
from channels.db import database_sync_to_async
from channels.sessions import CookieMiddleware, SessionMiddleware

from api.models.organization import TokenUserStatus

User = get_user_model()


@database_sync_to_async
def check_token_status(user_id, token):
    current_token = TokenUserStatus.objects.filter(user_id=user_id, current_token=token)
    if current_token:
        return True

    return False


@database_sync_to_async
def get_user(scope):
    print('checking user....')
    close_old_connections()
    query_string = parse_qs(scope['query_string'].decode())
    token = query_string.get('token')
    if not token:
        return AnonymousUser()
    try:
        from rest_framework_simplejwt.authentication import JWTAuthentication
        auth = JWTAuthentication()
        validated_token = auth.get_validated_token(token[0])
        user = auth.get_user(validated_token)
        if not check_token_status(user.id, validated_token):
            return AnonymousUser()

    except Exception as exception:
        return AnonymousUser()
    if not user.is_active:
        return AnonymousUser()
    return user


class TokenAuthMiddleware(AuthMiddleware):
    async def resolve_scope(self, scope):
        scope['user']._wrapped = await get_user(scope)


def TokenAuthMiddlewareStack(inner):
    return CookieMiddleware(SessionMiddleware(TokenAuthMiddleware(inner)))
