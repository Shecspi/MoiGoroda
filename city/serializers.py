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
    country = serializers.CharField(source='city.country', read_only=True)
    lat = serializers.CharField(source='city.coordinate_width', read_only=True)
    lon = serializers.CharField(source='city.coordinate_longitude', read_only=True)
    number_of_visits = serializers.IntegerField(read_only=True)
    first_visit_date = serializers.CharField(read_only=True)
    last_visit_date = serializers.CharField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    visit_years = serializers.SerializerMethodField()

    def get_year(self, obj) -> int | None:
        if obj.date_of_visit:
            return obj.date_of_visit.year
        return None

    def get_visit_years(self, obj) -> list[int] | None:
        if obj.visit_dates:
            return list(set(visit_date.year for visit_date in obj.visit_dates))
        return None

    class Meta:
        model = VisitedCity
        fields = (
            'username',
            'id',
            'title',
            'region_title',
            'region_id',
            'country',
            'lat',
            'lon',
            'number_of_visits',
            'first_visit_date',
            'last_visit_date',
            'average_rating',
            'visit_years',
        )


class NotVisitedCitySerializer(serializers.ModelSerializer):
    lat = serializers.CharField(source='coordinate_width', read_only=True)
    lon = serializers.CharField(source='coordinate_longitude', read_only=True)
    region = serializers.StringRelatedField()
    country = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = City
        fields = ('id', 'title', 'region', 'country', 'lat', 'lon')


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


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'title']
