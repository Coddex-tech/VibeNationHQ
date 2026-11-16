from django.urls import path
from .views.notification_list import NotificationListView


urlpatterns = [
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list",
    ),
]
