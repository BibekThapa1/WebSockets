import json
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync

class MyConsumer(WebsocketConsumer):
    def connect(self):
        self.group_name = "demo"
        layer = get_channel_layer()
        async_to_sync(layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({
            'message': 'hello bibek'
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # Echo message back
        self.send(text_data=json.dumps({
            'message': f"You said: {text_data}"
        }))

    def add_function(self, event):
        print("Entered here3")
        print("Event")
        self.send(
            text_data=json.dumps({
                'added':event
            })
        )