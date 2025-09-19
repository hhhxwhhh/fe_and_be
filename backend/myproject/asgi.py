"""
ASGI config for myproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from messaging import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# 从accounts应用导入认证中间件
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

django_asgi_app = get_asgi_application()

from messaging import consumers

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
                ]
            )
        ),
    }
)
