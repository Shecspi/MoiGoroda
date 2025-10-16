"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import TypedDict, NoReturn

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import serializers
import rest_framework.exceptions as drf_exc

from country.models import Country, VisitedCountry, PartOfTheWorld, Location


class CountryData(TypedDict):
    code: str
    name: str


class ValidatedData(TypedDict):
    country: CountryData
    user: User


class PartOfTheWorldSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = PartOfTheWorld
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Сериалайзер для модели Location"""

    class Meta:
        model = Location
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Сериалайзер для модели Country"""

    to_delete = serializers.SerializerMethodField(read_only=True)
    part_of_the_world = serializers.CharField(source='location.part_of_the_world', read_only=True)
    location = serializers.CharField(source='location.name', read_only=True)
    owner = serializers.CharField(source='owner.name', read_only=True)

    def get_to_delete(self, country: Country) -> str:
        return reverse('api__delete_visited_countries', kwargs={'code': country.code})

    class Meta:
        model = Country
        fields = '__all__'


class CountrySimpleSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    number_of_visited_cities = serializers.IntegerField(read_only=True)
    number_of_cities = serializers.IntegerField(read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'code', 'name', 'number_of_visited_cities', 'number_of_cities']


class VisitedCountrySerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Сериалайзер для модели VisitedCountry"""

    code = serializers.CharField(source='country.code', max_length=2, min_length=2)
    name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = VisitedCountry
        fields = ['code', 'name']
        extra_kwargs = {'country': {'read_only': True}}

    def create(self, validated_data: ValidatedData) -> VisitedCountry:
        # Проверка наличия страны в базе данных уже была сделана в validate_code, поэтому здесь она не требуется
        country = Country.objects.get(code=validated_data['country']['code'])
        return VisitedCountry.objects.create(country=country, user=validated_data['user'])

    def validate_code(self, country_code: str) -> str | NoReturn:
        try:
            country_instance = Country.objects.get(code=country_code)
        except Country.DoesNotExist:
            raise drf_exc.ValidationError(f"Страны с кодом '{country_code}' не существует.")

        if VisitedCountry.objects.filter(
            country=country_instance, user=self.context['request'].user.pk
        ).exists():
            raise serializers.ValidationError(
                f'Страна {country_instance} уже была добавлена ранее.'
            )

        return country_code
