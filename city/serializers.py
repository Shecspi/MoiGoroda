from rest_framework import serializers

from city.models import VisitedCity, City


class VisitedCitySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='city.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    title = serializers.CharField(source='city.title', read_only=True)
    lat = serializers.CharField(source='city.coordinate_width', read_only=True)
    lon = serializers.CharField(source='city.coordinate_longitude', read_only=True)

    class Meta:
        model = VisitedCity
        fields = ('username', 'id', 'title', 'lat', 'lon')


class NotVisitedCitySerializer(serializers.ModelSerializer):
    lat = serializers.CharField(source='coordinate_width', read_only=True)
    lon = serializers.CharField(source='coordinate_longitude', read_only=True)

    class Meta:
        model = City
        fields = ('id', 'title', 'lat', 'lon')
