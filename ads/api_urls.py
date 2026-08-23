from django.urls import path

from .api_views import (
    AdZoneAPIView,
    AdImpressionAPIView,
    AdClickAPIView,
)

urlpatterns = [
    path(
        "zone/<slug:zone_slug>/",
        AdZoneAPIView.as_view(),
        name="ad-zone",
    ),

    path(
        "<int:ad_id>/impression/",
        AdImpressionAPIView.as_view(),
        name="ad-impression",
    ),

    path(
        "<int:ad_id>/click/",
        AdClickAPIView.as_view(),
        name="ad-click",
    ),
]