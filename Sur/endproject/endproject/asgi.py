import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from monklingo import consumers  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'endproject.settings')  

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<int:room_id>/", consumers.ChatConsumer.as_asgi()),
        ])
    ),
})
