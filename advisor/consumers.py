import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat between students and advisors."""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        sender_id = text_data_json.get('sender_id')
        recipient_id = text_data_json.get('recipient_id')
        
        # Save message to database
        await self.save_message(sender_id, recipient_id, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'timestamp': timezone.now().isoformat(),
            }
        )
    
    async def chat_message(self, event):
        """Receive message from room group."""
        message = event['message']
        sender_id = event['sender_id']
        timestamp = event['timestamp']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'timestamp': timestamp,
        }))
    
    @database_sync_to_async
    def save_message(self, sender_id, recipient_id, message):
        """Save chat message to database."""
        from .models import ChatMessage
        from authentication.models import User
        
        try:
            sender = User.objects.get(id=sender_id)
            recipient = User.objects.get(id=recipient_id)
            
            ChatMessage.objects.create(
                sender=sender,
                recipient=recipient,
                message=message
            )
        except User.DoesNotExist:
            pass
