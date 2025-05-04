from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/match/$', consumers.MatchmakerConsumer.as_asgi()),
    re_path(r'ws/call/(?P<room_name>[^/]+)/$', consumers.CallConsumer.as_asgi()),
]
