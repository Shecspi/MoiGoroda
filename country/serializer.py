"""
Сериалайзеры для приложения country.

----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from rest_framework import serializers

from country.models import Country


class CountrySerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Country."""

    class Meta:
        model = Country
        fields = '__all__'
