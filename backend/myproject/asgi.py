"""
ASGI config for myproject project.

It exposes the ASGI callable as a module-level variable named `[application](file:///Users/wang/code/fe_and_be/backend/myproject/asgi.py#L56-L61)`.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# 从messaging应用导入websocket路由
from messaging.urls import websocket_urlpatterns

# 导入Channels相关模块
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
import urllib.parse

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 从查询参数中获取token
        query_string = scope.get("query_string", b"").decode()
        params = urllib.parse.parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            token = token_list[0]
            user = await get_user_from_token(token)
            scope["user"] = user
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)


# 简化路由配置，确保正确处理WebSocket
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
