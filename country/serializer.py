"""
Сериалайзеры для приложения country.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from rest_framework import serializers

from country.models import Country, VisitedCountry
from services import logger


class CountrySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Country."""

    class Meta:
        model = Country
        fields = '__all__'


class VisitedCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitedCountry
        fields = ['id', 'country']

    def create(self, validated_data):
        return VisitedCountry.objects.create(**validated_data)

    def validate_country(self, country):
        if VisitedCountry.objects.filter(
            country=country, user=self.context['request'].user.pk
        ).exists():
            logger.info(
                self.context['request'],
                '(API: Add visited country) An attempt to add a visited country that is already in the DB',
            )
            raise serializers.ValidationError(f'Страна {country} уже была добавлена ранее.')
        return country
