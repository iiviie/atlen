from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import GroupChat, Message
from django.core.exceptions import ObjectDoesNotExist
import json
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from jwt import InvalidTokenError

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        self.room_group_name = f'chat_{self.trip_id}'
        
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', b'').decode()
        
        if not auth_header.startswith('Bearer '):
            await self.close()
            return
        
        token = auth_header.split(' ')[1]
        user = await self.get_user_from_token(token)
        if not user:
            await self.close()
            return
        
        self.scope['user'] = user

        try:
            chat = await self.get_chat()
            if not await self.is_trip_participant():
                await self.close()
                return
        except ObjectDoesNotExist:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content):
        message_type = content.get('type')
        if message_type == 'chat_message':
            message = await self.save_message(content.get('message', ''))
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    async def chat_message(self, event):
        await self.send_json(event['message'])

    @database_sync_to_async
    def get_chat(self):
        return GroupChat.objects.get(trip_id=self.trip_id)

    @database_sync_to_async
    def is_trip_participant(self):
        chat = GroupChat.objects.get(trip_id=self.trip_id)
        user = self.scope['user']
        trip = chat.trip
        return user == trip.creator or user in trip.companions.all()

    @database_sync_to_async
    def save_message(self, content):
        chat = GroupChat.objects.get(trip_id=self.trip_id)
        message = Message.objects.create(
            chat=chat,
            sender=self.scope['user'],
            content=content
        )
        return {
            'id': str(message.id),
            'sender': {
                'id': str(message.sender.id),
                'email': message.sender.email,
                'name': f"{message.sender.first_name} {message.sender.last_name}"
            },
            'content': message.content,
            'created_at': message.created_at.isoformat()
        }

    @database_sync_to_async
    def get_user_from_token(self, token):
        User = get_user_model()
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidTokenError, User.DoesNotExist):
            return None