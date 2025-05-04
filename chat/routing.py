# routing.py
from django.urls import re_path
from .consumers import MatchmakerConsumer
from .consumers import CallConsumer

websocket_urlpatterns = [
    re_path(r'ws/match/$', MatchmakerConsumer.as_asgi()),
    re_path(r'ws/call/(?P<room_name>[^/]+)/$', CallConsumer.as_asgi()),
]