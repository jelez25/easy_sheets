import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Verificar autenticación
            user = self.scope["user"]
            
            if user.is_anonymous:
                await self.close()
                return
            
            # Obtener thread_id y verificar formato
            self.thread_id = self.scope['url_route']['kwargs']['thread_id']
            self.room_group_name = f'thread_{self.thread_id}'
            
            # Verificar acceso al hilo
            has_access = await self.verify_thread_access()
            
            if not has_access:
                await self.close()
                return
            
            # Intentar conexión a Redis
            try:
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            except Exception as e:
                await self.close()
                return
            
            # Aceptar la conexión
            await self.accept()
            
        except Exception as e:
            await self.close()
            
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = self.scope['user'].id
        await self.save_message(sender_id, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
            }
        )

    async def chat_message(self, event):
        sender = await self.get_sender(event['sender_id'])
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': sender,
        }))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        Thread = apps.get_model('messaging', 'Thread')
        Message = apps.get_model('messaging', 'Message')
        CustomUser = apps.get_model('accounts', 'CustomUser')
        
        thread = Thread.objects.get(id=self.thread_id)
        sender = CustomUser.objects.get(id=sender_id)
        Message.objects.create(thread=thread, sender=sender, content=message)

    @database_sync_to_async
    def get_sender(self, sender_id):
        CustomUser = apps.get_model('accounts', 'CustomUser')
        user = CustomUser.objects.get(id=sender_id)
        return f"{user.name} {user.surname_1}"

    @database_sync_to_async
    def verify_thread_access(self):
        Thread = apps.get_model('messaging', 'Thread')
        try:
            thread = Thread.objects.get(id=self.thread_id)
            return thread.participants.filter(id=self.scope["user"].id).exists()
        except Thread.DoesNotExist:
            return False
