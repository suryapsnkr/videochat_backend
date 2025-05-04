from django.urls import re_path
from .consumers import MatchmakerConsumer

websocket_urlpatterns = [
    re_path(r'ws/match/$', MatchmakerConsumer.as_asgi()),  # Matchmaker endpoint
    re_path(r'ws/call/(?P<room_name>[^/]+)/$', MatchmakerConsumer.as_asgi()),  # Call signaling endpoint
]
