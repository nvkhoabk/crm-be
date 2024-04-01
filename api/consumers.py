from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.const import WS_USER_GROUP
import api.services.manage as manage
from asgiref.sync import sync_to_async

from django.core.cache import cache

class CrmConsumer(AsyncJsonWebsocketConsumer):
    groups = ['crm']

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                group=WS_USER_GROUP.USER,
                channel=self.channel_name
            )

            if await manage.is_technical_staff(user):
                await self.channel_layer.group_add(
                    group=WS_USER_GROUP.PHONE_NUMBER_MANAGE,
                    channel=self.channel_name
                )

            await self.accept()

    async def disconnect(self, code):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_discard(
                group=WS_USER_GROUP.USER,
                channel=self.channel_name
            )

            if await manage.is_technical_staff(user):
                await self.channel_layer.group_discard(
                    group=WS_USER_GROUP.PHONE_NUMBER_MANAGE,
                    channel=self.channel_name
                )

        await super().disconnect(code)

    async def echo_message(self, message):
        await self.send_json(message)

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'take_number':
            await self.take_number(content)
        elif message_type == 'release_number':
            await self.release_number(content)
        elif message_type == 'echo_message':
            await self.echo_message(content)
        elif message_type == 'open_ticket':
            await self.open_ticket(content)

    async def take_number(self, message):
        data = message.get('data')
        await self.send_json({
            "result": "ALLOW",
            "user_id": data["user_id"],
            "phone_number": data["phone_number"],
            "phone_number_id": data["phone_number_id"]
        })
        cache.set(data["phone_number_id"], data["user_id"])


    async def release_number(self, message):
        data = message.get('data')

    async def open_ticket(self, message):
        data = message.get('data')

        # Send rider requests to all drivers.
        await self.channel_layer.group_send(group=WS_USER_GROUP.PHONE_NUMBER_MANAGE, message={
            'type': 'open.ticket',
            'data': {
                "test_all": "Hello"
            }
        })


