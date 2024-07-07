from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class LikeConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'like_updates'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        postid = data.get('postid')
        likes = data.get('likes')
        print(postid, likes)
        
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type' : 'update_like',
                'postid' : postid,
                'likes' : likes
            }
        )

    def update_like(self, event):
        postid = event['postid']
        likes = event['likes']

        self.send(text_data=json.dumps({
            'postid' : postid,
            'likes' : likes
        }))
        
    