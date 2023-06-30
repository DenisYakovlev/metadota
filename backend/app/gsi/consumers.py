import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from user.models import User

# gsi token format(uuid):006e81a5-aed0-4419-9eea-aa0066ebb79b

class GSIConsumer(WebsocketConsumer):
    def connect(self):
        self.gsi_token = self.scope["url_route"]["kwargs"]["gsi_token"]
        self.room_group_name = "gsi_%s" % self.gsi_token
        token_exists = User.objects.filter(gsi_token=self.gsi_token).first()

        if token_exists:
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, 
                self.channel_name
            )
            self.accept()

            # send acception message
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'gsi_message',
                    'message': {
                        'status': {
                            'is_going': 'false'
                        },
                        'game': {
                            "msg": f"Connected to room: {self.room_group_name}",
                        }
                    }
                }
            )
        else:
            # reject connection
            return 

    def gsi_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type':'gsi_message',
            'message':message
        }))