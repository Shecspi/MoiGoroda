from rest_framework import serializers

from city.models import VisitedCity


class CitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    title = serializers.CharField(source='city.title', read_only=True)
    lat = serializers.CharField(source='city.coordinate_width', read_only=True)
    lon = serializers.CharField(source='city.coordinate_longitude', read_only=True)

    class Meta:
        model = VisitedCity
        fields = ('username', 'id', 'title', 'lat', 'lon')
