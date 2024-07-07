from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/like-update/', consumers.LikeConsumer.as_asgi())
]