import random

from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .models import Advertisement
from .serializers import AdvertisementSerializer


class AdZoneAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, zone_slug):

        ads = list(
            Advertisement.objects
            .filter(
                zone__slug=zone_slug,
                is_active=True
            )
            .select_related("zone")
        )

        if not ads:
            return Response({
                "ad": None,
                "zone": zone_slug
            })

        ad = random.choice(ads)

        serializer = AdvertisementSerializer(
            ad,
            context={"request": request}
        )

        return Response({
            "ad": serializer.data,
            "zone": zone_slug
        })


class AdImpressionAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, ad_id):

        updated = (
            Advertisement.objects
            .filter(
                id=ad_id,
                is_active=True
            )
            .update(
                impressions=F("impressions") + 1
            )
        )

        if not updated:
            return Response(
                {"detail": "Advertisement not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"success": True},
            status=status.HTTP_200_OK
        )

class AdClickAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, ad_id):
        updated = (
            Advertisement.objects
            .filter(
                id=ad_id,
                is_active=True
            )
            .update(
                clicks=F("clicks") + 1
            )
        )

        if not updated:
            return Response(
                {"detail": "Advertisement not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"success": True},
            status=status.HTTP_200_OK
        )