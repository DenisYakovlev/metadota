from django.urls import re_path 
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/gsi/(?P<gsi_token>[A-Za-z0-9_-]+)", consumers.GSIConsumer.as_asgi())
]