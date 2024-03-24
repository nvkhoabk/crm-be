from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.const import WS_USER_GROUP
import api.services.manage as manage
from asgiref.sync import sync_to_async

# from trips.models import Trip
# from trips.serializers import NestedTripSerializer, TripSerializer


class CrmConsumer(AsyncJsonWebsocketConsumer):
    groups = ['crm']

    @database_sync_to_async
    def _create_trip(self, data):
        serializer = TripSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.create(serializer.validated_data)

    @database_sync_to_async
    def _get_trip_data(self, trip):
        return NestedTripSerializer(trip).data

    @database_sync_to_async
    def _get_trip_ids(self, user):
        user_groups = user.groups.values_list('name', flat=True)
        if 'driver' in user_groups:
            trip_ids = user.trips_as_driver.exclude(
                status=Trip.COMPLETED
            ).only('id').values_list('id', flat=True)
        else:
            trip_ids = user.trips_as_rider.exclude(
                status=Trip.COMPLETED
            ).only('id').values_list('id', flat=True)
        return map(str, trip_ids)

    @database_sync_to_async
    def _get_user_group(self, user):
        return user.groups.first().name

    @database_sync_to_async
    def _update_trip(self, data):
        instance = Trip.objects.get(id=data.get('id'))
        serializer = TripSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.update(instance, serializer.validated_data)

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

    async def take_number(self, message):
        data = message.get('data')

    async def release_number(self, message):
        data = message.get('data')

    async def open_ticket(self, message):
        data = message.get('data')
        trip = await self._create_trip(data)
        trip_data = await self._get_trip_data(trip)

        # Send rider requests to all drivers.
        await self.channel_layer.group_send(group=WS_USER_GROUP.PHONE_NUMBER_MANAGE, message={
            'type': 'open.ticket',
            'data': {

            }
        })


