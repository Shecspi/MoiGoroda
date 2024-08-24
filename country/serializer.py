"""
Сериалайзеры для приложения country.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import TypedDict, NoReturn

from django.contrib.auth.models import User
from rest_framework import serializers
import rest_framework.exceptions as drf_exc

from country.models import Country, VisitedCountry


class CountryData(TypedDict):
    code: str
    name: str


class ValidatedData(TypedDict):
    country: CountryData
    user: User


class CountrySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Country"""

    class Meta:
        model = Country
        fields = '__all__'


class VisitedCountrySerializer(serializers.ModelSerializer):
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
