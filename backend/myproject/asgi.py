import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# 先调用django.setup()，然后导入用户模型以确保应用加载
django.setup()
from django.contrib.auth import get_user_model

get_user_model()  # 触发用户模型的加载

application = get_asgi_application()

# 导入channels的路由
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from messaging.urls import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
