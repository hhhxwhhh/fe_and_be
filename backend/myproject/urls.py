"""
URL configuration for myproject project.

The [urlpatterns](file:///Users/wang/code/fe_and_be/backend/myproject/urls.py#L23-L31) list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView


def api_root(request):
    """
    API根路径视图，显示可用的API端点
    """
    return JsonResponse(
        {
            "message": "欢迎使用我们的API",
            "endpoints": {
                "admin": "/admin/",
                "auth": "/api/auth/",
                "posts": "/api/posts/",
                "interactions": "/api/interactions/",
                "messages": "/api/messages/",
                "ai": "/api/ai/deepseek/",
                "token_refresh": "/api/token/refresh/",
            },
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/interactions/", include("interactions.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/messages/", include("messaging.urls")),
    path("api/ai/deepseek/", include("ai.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
