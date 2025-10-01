from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkAllAsReadView,
    NotificationMarkAsReadView,
    UnreadNotificationCountView,
)

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/<int:pk>/read/",
        NotificationMarkAsReadView.as_view(),
        name="notification-mark-as-read",
    ),
    path(
        "notifications/read-all/",
        NotificationMarkAllAsReadView.as_view(),
        name="notification-mark-all-as-read",
    ),
    path(
        "notifications/unread-count/",
        UnreadNotificationCountView.as_view(),
        name="notification-unread-count",
    ),
]