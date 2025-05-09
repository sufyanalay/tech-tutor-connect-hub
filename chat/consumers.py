
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Check if user is authorized to join this chat
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return
            
        is_participant = await self.is_user_participant(user, self.room_id)
        if not is_participant:
            await self.close()
            return
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        attachment = data.get('attachment', None)
        
        user = self.scope['user']
        
        # Save message to database
        db_message = await self.save_message(
            room_id=self.room_id,
            sender=user,
            content=message,
            attachment=attachment
        )
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': user.id,
                'sender_name': user.full_name,
                'sender_role': user.role,
                'message_id': db_message.id,
                'attachment': attachment,
                'timestamp': str(db_message.timestamp)
            }
        )
    
    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_role': event['sender_role'],
            'attachment': event.get('attachment'),
            'timestamp': event['timestamp']
        }))
    
    @database_sync_to_async
    def is_user_participant(self, user, room_id):
        try:
            room = ChatRoom.objects.get(pk=room_id)
            return room.participants.filter(pk=user.id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, room_id, sender, content, attachment=None):
        room = ChatRoom.objects.get(pk=room_id)
        message = Message(
            room=room,
            sender=sender,
            content=content
        )
        if attachment:
            message.attachment = attachment
        message.save()
        return message
