from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer for VibeNation music models.

    Keeps shared serializer behavior in one place so individual
    serializer modules remain clean and focused.
    """

    class Meta:
        abstract = True


def validate_half_star_rating(value):
    """
    Validate that a rating is between 0.5 and 5.0
    and uses 0.5-star increments.
    """

    if value < 0.5 or value > 5.0:
        raise serializers.ValidationError(
            "Rating must be between 0.5 and 5.0."
        )

    if (value * 2) % 1 != 0:
        raise serializers.ValidationError(
            "Rating must use 0.5-star increments."
        )

    return value