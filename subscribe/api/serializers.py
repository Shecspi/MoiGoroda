from typing import Any
from rest_framework import serializers


class NotificationSerializer(serializers.Serializer[dict[str, Any]]):
    id = serializers.IntegerField()
    city_id = serializers.IntegerField()
    city_title = serializers.CharField()
    region_id = serializers.IntegerField()
    region_title = serializers.CharField()
    country_code = serializers.CharField()
    country_title = serializers.CharField()
    is_read = serializers.BooleanField()
    read_at = serializers.DateTimeField()
    sender_id = serializers.IntegerField()
    sender_username = serializers.CharField()
