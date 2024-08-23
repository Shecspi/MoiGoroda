"""
Сериалайзеры для приложения country.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import TypedDict

from django.contrib.auth.models import User
from rest_framework import serializers
import rest_framework.exceptions as drf_exc

from country.models import Country, VisitedCountry


class RequestedData(TypedDict):
    country: Country
    user: User


class CountrySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Country."""

    class Meta:
        model = Country
        fields = '__all__'


class VisitedCountrySerializer(serializers.ModelSerializer):
    country = serializers.CharField()

    class Meta:
        model = VisitedCountry
        fields = ['country']

    def create(self, validated_data: RequestedData):
        return VisitedCountry.objects.create(
            country=validated_data['country'], user=validated_data['user']
        )

    def validate_country(self, country_code: str):
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

        return country_instance
