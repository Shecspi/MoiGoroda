from rest_framework import serializers
from .models import VisitedCityNotification


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    city_title = serializers.CharField(source='city.title', read_only=True)

    class Meta:
        model = VisitedCityNotification
        fields = ['id', 'city', 'city_title', 'is_read', 'sender', 'sender_username']
        read_only_fields = ['id', 'city', 'city_title', 'sender', 'sender_username']
