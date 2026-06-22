from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

from api.const import WS_USER_GROUP
import api.services.manage as manage
import api.utils.cache as cache
from asgiref.sync import sync_to_async

from api.models.phone_number import PhoneNumber

User = get_user_model()


class CrmConsumer(AsyncJsonWebsocketConsumer):
    groups = ['crm']

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            await self.accept()

            await self.channel_layer.group_add(
                group=WS_USER_GROUP.USER,
                channel=self.channel_name
            )

            if await manage.is_technical_staff(user):
                await self.channel_layer.group_add(
                    group=WS_USER_GROUP.PHONE_NUMBER_MANAGE,
                    channel=self.channel_name
                )
                phone_number_cache = cache.get_phone_number_cache()
                await self.update_phone_number_to_client({'data': phone_number_cache})

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
                phone_number_cache = cache.get_phone_number_cache()
                for key, value in phone_number_cache.items():
                    if value == user.username:
                        phone_number_cache = cache.delete_phone_number_to_cache(key)
                        await self.phone_number_updated(phone_number_cache)

        await super().disconnect(code)

    async def echo_message(self, message):
        await self.channel_layer.group_send(group=WS_USER_GROUP.PHONE_NUMBER_MANAGE, message={
            'type': 'send_all',
            'data': message
        })

    async def send_all(self, message):
        await self.send_json(message)

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'take_number':
            await self.take_number(content)
        elif message_type == 'release_number':
            await self.release_number(content)
        elif message_type == 'unlock_number':
            await self.unlock_number(content)
        elif message_type == 'echo_message':
            await self.echo_message(content)
        elif message_type == 'ping':
            await self.pong()

    async def take_number(self, message):
        data = message.get('data', None)
        request_phone_number = data.get('phone_number', None)
        if request_phone_number is not None:
            db_phone_number = await PhoneNumber.objects.filter(phone_number__iexact=request_phone_number,
                                                         deleted_at__isnull=True).afirst()
            user = await User.objects.filter(pk=data["user_id"]).afirst()
            if db_phone_number and user:
                if not cache.is_phone_number_opening(request_phone_number):
                    phone_number_dict = cache.add_phone_number_to_cache(request_phone_number, user.username)
                    await self.send_json({
                        "result": "ALLOW",
                        "user_id": data["user_id"],
                        "phone_number": data["phone_number"],
                        "phone_number_id": data["phone_number_id"]
                    })
                    await self.phone_number_updated(phone_number_dict)
                    return
                else:
                    print('phone number already opened')
            else:
                print('not found phone number in db')
        else:
            print('not found phone number in message')

        await self.send_json({
            "result": "DENIED",
            "user_id": data["user_id"],
            "phone_number": data["phone_number"],
            "phone_number_id": data["phone_number_id"]
        })

    async def release_number(self, message):
        data = message.get('data')
        request_phone_number = data.get('phone_number', None)
        if request_phone_number is not None:
            phone_number_list = cache.delete_phone_number_to_cache(request_phone_number)
            await self.phone_number_updated(phone_number_list)

    async def unlock_number(self, message):
        data = message.get('data')
        request_phone_number = data.get('phone_number', None)
        if request_phone_number is not None:
            phone_number_list = cache.delete_phone_number_to_cache(request_phone_number)
            await self.phone_number_updated(phone_number_list)

    async def phone_number_updated(self, phone_number_dict):
        await self.channel_layer.group_send(group=WS_USER_GROUP.PHONE_NUMBER_MANAGE, message={
            "type": "update_phone_number_to_client",
            "data": phone_number_dict
        })

    async def pong(self):
            await self.send_json({
            "type": "pong",
            "data": ''
        })

    async def update_phone_number_to_client(self, message):
        list_phone_number = []
        for key, value in message['data'].items():
            list_phone_number.append({
                'phone_number': key,
                'user': value
            })

        await self.send_json({
            "type": "update_phone_number",
            "data": list_phone_number
        })

    async def trigger_update_phone_number_queue(self, message):
        await self.send_json({
            "type": "update_phone_number_queue",
            "data": ""
        })


