from rest_framework import serializers

from .models import Advertisement


class AdvertisementSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    click_url = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = [
            "id",
            "zone",
            "title",
            "client_name",
            "image_url",
            "video_url",
            "link_url",
            "click_url",
            "html_code",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url

    def get_video_url(self, obj):
        if not obj.video:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.video.url)

        return obj.video.url

    def get_click_url(self, obj):
        return f"/api/v1/ads/{obj.id}/click/"