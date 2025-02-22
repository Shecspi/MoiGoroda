"""
Сериалайзеры для посещённых и непосещённых городов.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from rest_framework import serializers

from city.models import VisitedCity, City


class VisitedCitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='city.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    title = serializers.CharField(source='city.title', read_only=True)
    region_title = serializers.CharField(source='city.region', read_only=True)
    region_id = serializers.IntegerField(source='city.region_id', read_only=True)
    lat = serializers.CharField(source='city.coordinate_width', read_only=True)
    lon = serializers.CharField(source='city.coordinate_longitude', read_only=True)
    year = serializers.SerializerMethodField()
    number_of_visits = serializers.IntegerField(read_only=True)
    date_of_first_visit = serializers.CharField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    def get_year(self, obj) -> int | None:
        if obj.date_of_visit:
            return obj.date_of_visit.year
        return None

    class Meta:
        model = VisitedCity
        fields = (
            'username',
            'id',
            'title',
            'region_title',
            'region_id',
            'lat',
            'lon',
            'year',
            'number_of_visits',
            'date_of_first_visit',
            'average_rating',
        )


class NotVisitedCitySerializer(serializers.ModelSerializer):
    region_title = serializers.CharField()
    lat = serializers.CharField(source='coordinate_width', read_only=True)
    lon = serializers.CharField(source='coordinate_longitude', read_only=True)

    class Meta:
        model = City
        fields = ('id', 'title', 'region', 'region_title', 'lat', 'lon')


class AddVisitedCitySerializer(serializers.ModelSerializer):
    city_title = serializers.CharField(source='city.title', read_only=True)
    region_title = serializers.CharField(source='city.region', read_only=True)
    lat = serializers.CharField(source='city.coordinate_width', read_only=True)
    lon = serializers.CharField(source='city.coordinate_longitude', read_only=True)

    class Meta:
        model = VisitedCity
        fields = (
            'id',
            'city',
            'city_title',
            'region_title',
            'date_of_visit',
            'has_magnet',
            'impression',
            'rating',
            'lat',
            'lon',
        )

    def create(self, validated_data):
        user = self.context['request'].user
        city = validated_data['city']

        # Проверяем, существует ли запись с этим пользователем и городом
        exists = VisitedCity.objects.filter(city=city, user=user).exists()

        validated_data['is_first_visit'] = not exists  # Если запись есть, ставим False, иначе True

        return VisitedCity.objects.create(**validated_data)
