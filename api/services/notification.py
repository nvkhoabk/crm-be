from api.common.base_service import BaseService
from api.common.cookies import Cookies
from api.models.organization import UserRole
from api.models.notification import Notification
from api.services.exceptions import (NotificationNotFound)


class FilterNotificationService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        filter = {
            'user': request.user,
            'deleted_at__isnull': True
        }
        user_roles = UserRole.objects.filter(**filter)

        query_set = Notification.objects.filter(company_id=user_roles.first().company_id, user=request.user,
                                                deleted_at__isnull=True)

        filters = ['from_time', 'unread']
        params = dict(kwargs.get('filter', []))
        for key, value in params.items():
            if key not in filters:
                continue

            if key == 'from_time' and value is not None:
                query_set = query_set.filter(
                    created_at__gt=value,
                )

            if key == 'unread' and value is not None:
                query_set = query_set.filter(unread=value)

        return query_set


class UpdateUnreadNotificationService(BaseService):
    def serve(self, request, cookies: Cookies, *args, **kwargs):
        try:
            filter = {
                'user': request.user,
                'deleted_at__isnull': True
            }
            user_roles = UserRole.objects.filter(**filter)

            notification = Notification.objects.get(
                pk=kwargs['id'],
                company_id=user_roles.first().company_id,
                user=request.user
            )
            notification.unread = True
            notification.save()
            return notification

        except Notification.DoesNotExist as e:
            raise NotificationNotFound()
