import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Post, Comment, Like
from django.contrib.auth.models import User
from channels.layers import get_channel_layer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    @sync_to_async
    def save_message(self, username, message):
        user = User.objects.get(username=username)
        Post.objects.create(author=user, content=message)


class LikeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_layer = get_channel_layer()
        if self.channel_layer:
            await self.channel_layer.group_add("likes", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.channel_layer:
            await self.channel_layer.group_discard("likes", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        item_type = text_data_json['item_type']
        item_id = text_data_json['item_id']
        username = text_data_json['username']

        liked, like_count, liked_users = await self.toggle_like(username, item_type, item_id)

        if self.channel_layer:
            await self.channel_layer.group_send(
                "likes",
                {
                    'type': 'like_message',
                    'message': {
                        'item_type': item_type,
                        'item_id': item_id,
                        'liked': liked,
                        'like_count': like_count,
                        'liked_users': liked_users
                    }
                }
            )

    async def like_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @sync_to_async
    def toggle_like(self, username, item_type, item_id):
        user = User.objects.get(username=username)
        model = Post if item_type == 'post' else Comment
        item = model.objects.get(id=item_id)

        like, created = Like.objects.get_or_create(user=user, **{item_type: item})

        if not created:
            like.delete()

        likes = Like.objects.filter(**{item_type: item})
        like_count = likes.count()
        liked_users = list(likes.values_list('user__username', flat=True))

        return created, like_count, liked_users
