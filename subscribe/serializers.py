from rest_framework import serializers
from .models import VisitedCityNotification


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    city_title = serializers.CharField(source='city.title', read_only=True)
    region_id = serializers.CharField(source='city.region.id', read_only=True)
    region_title = serializers.CharField(source='city.region.full_name', read_only=True)
    country_code = serializers.CharField(source='city.country.code', read_only=True)
    country_title = serializers.CharField(source='city.country.name', read_only=True)

    class Meta:
        model = VisitedCityNotification
        fields = [
            'id',
            'city',
            'city_title',
            'region_id',
            'region_title',
            'country_code',
            'country_title',
            'is_read',
            'sender',
            'sender_username',
        ]
        read_only_fields = [
            'id',
            'city',
            'city_title',
            'region_id',
            'region_title',
            'country_code',
            'country_title',
            'sender',
            'sender_username',
        ]
