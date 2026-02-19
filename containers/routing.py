from django.urls import re_path
from .consumers import TerminalConsumer , LogsConsumer ,StatusConsumer

websocket_urlpatterns = [
    re_path(r"ws/terminal/(?P<name>[^/]+)/$", TerminalConsumer.as_asgi()),
    re_path(r"ws/logs/(?P<name>[^/]+)/$", LogsConsumer.as_asgi()),
    re_path(r"ws/status/$", StatusConsumer.as_asgi()),

]
