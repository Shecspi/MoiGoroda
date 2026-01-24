"""
Сериалайзеры для посещённых и непосещённых городов.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.contrib.auth.models import User
from rest_framework import serializers

from city.models import City, CityDistrict, VisitedCity, VisitedCityDistrict


class VisitedCitySerializer(serializers.ModelSerializer[VisitedCity]):
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

    def get_year(self, obj: VisitedCity) -> int | None:
        if obj.date_of_visit:
            return obj.date_of_visit.year
        return None

    def get_visit_years(self, obj: VisitedCity) -> list[int] | None:
        """
        Возвращает список всех уникальных годов, в которые был посещён город.
        Использует visit_dates из аннотации queryset, если доступно,
        иначе fallback на date_of_visit текущей записи.
        """
        # Проверяем наличие visit_dates из аннотации queryset
        visit_dates = getattr(obj, 'visit_dates', None)

        if visit_dates:
            # Извлекаем уникальные годы из всех дат посещений
            years = sorted(set(date.year for date in visit_dates if date), reverse=True)
            return years if years else None

        # Fallback: если visit_dates нет, используем date_of_visit текущей записи
        if obj.date_of_visit:
            return [obj.date_of_visit.year]

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


class NotVisitedCitySerializer(serializers.ModelSerializer[City]):
    lat = serializers.CharField(source='coordinate_width', read_only=True)
    lon = serializers.CharField(source='coordinate_longitude', read_only=True)
    region: Any = serializers.StringRelatedField()
    country = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = City
        fields = ('id', 'title', 'region', 'country', 'lat', 'lon')


class AddVisitedCitySerializer(serializers.ModelSerializer[VisitedCity]):
    city_title = serializers.CharField(source='city.title', read_only=True)
    region_title = serializers.CharField(source='city.region', read_only=True)
    country = serializers.CharField(source='city.country.name', read_only=True)
    lat = serializers.CharField(source='city.coordinate_width', read_only=True)
    lon = serializers.CharField(source='city.coordinate_longitude', read_only=True)

    class Meta:
        model = VisitedCity
        fields = (
            'id',
            'city',
            'city_title',
            'region_title',
            'country',
            'date_of_visit',
            'has_magnet',
            'impression',
            'rating',
            'lat',
            'lon',
        )

    def create(self, validated_data: dict[str, Any]) -> VisitedCity:
        user = self.context['request'].user
        city = validated_data['city']

        # Проверяем, существует ли запись с этим пользователем и городом
        exists = VisitedCity.objects.filter(city=city, user=user).exists()

        validated_data['is_first_visit'] = not exists  # Если запись есть, ставим False, иначе True

        return VisitedCity.objects.create(**validated_data)


class CitySerializer(serializers.ModelSerializer[City]):
    region = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    def get_region(self, obj: City) -> str | None:
        """Возвращает полное название региона, если он указан."""
        if obj.region:
            return obj.region.full_name
        return None

    def get_country(self, obj: City) -> str | None:
        """Возвращает название страны, если country или country_id не указан в URL."""
        # Проверяем, есть ли country или country_id в контексте запроса
        request = self.context.get('request')
        if request and (request.GET.get('country') or request.GET.get('country_id')):
            return None  # Скрываем страну, если country или country_id указан в URL
        return obj.country.name if obj.country else None

    class Meta:
        model = City
        fields = ['id', 'title', 'region', 'country']


class CitySearchParamsSerializer(serializers.Serializer[dict[str, Any]]):
    query = serializers.CharField(
        required=True,
        min_length=1,
        max_length=100,
        help_text='Подстрока для поиска в названии города',
    )
    country = serializers.CharField(
        required=False, max_length=2, help_text='Код страны для дополнительной фильтрации'
    )
    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=200,
        default=50,
        help_text='Максимальное количество результатов (по умолчанию 50, максимум 200)',
    )


class CityDistrictSerializer(serializers.ModelSerializer[CityDistrict]):
    """
    Сериализатор для района города.
    """

    is_visited = serializers.SerializerMethodField()

    def get_is_visited(self, obj: CityDistrict) -> bool:
        """
        Проверяет, посещён ли район текущим пользователем.
        """
        visited_district_ids = self.context.get('visited_district_ids')
        if isinstance(visited_district_ids, set):
            return obj.pk in visited_district_ids

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            assert isinstance(request.user, User)
            return VisitedCityDistrict.objects.filter(user=request.user, city_district=obj).exists()
        return False

    class Meta:
        model = CityDistrict
        fields = ['id', 'title', 'area', 'population', 'is_visited']


class AddVisitedCityDistrictSerializer(serializers.Serializer[VisitedCityDistrict]):
    """
    Сериализатор для создания записи о посещении района.
    """

    city_district_id = serializers.IntegerField(required=True)

    def create(self, validated_data: dict[str, Any]) -> VisitedCityDistrict:
        """
        Создаёт запись о посещении района.
        """
        city_district_id = validated_data['city_district_id']

        try:
            city_district = CityDistrict.objects.get(pk=city_district_id)
        except CityDistrict.DoesNotExist:
            raise serializers.ValidationError(
                {'city_district_id': f'Район с id {city_district_id} не найден.'}
            )

        user = self.context['request'].user
        assert isinstance(user, User)

        if VisitedCityDistrict.objects.filter(user=user, city_district=city_district).exists():
            raise serializers.ValidationError({'detail': 'Район уже отмечен как посещённый.'})

        return VisitedCityDistrict.objects.create(user=user, city_district=city_district)
