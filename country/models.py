"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User
from django.db import models

from city.models import City


class PartOfTheWorld(models.Model):
    name = models.CharField(
        max_length=20, unique=True, blank=False, null=False, verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Часть света'
        verbose_name_plural = 'Части света'

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(
        max_length=50, unique=True, blank=False, null=False, verbose_name='Название'
    )
    part_of_the_world = models.ForeignKey(
        PartOfTheWorld, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Часть света'
    )

    class Meta:
        verbose_name = 'Расположение'
        verbose_name_plural = 'Расположения'

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(
        max_length=255, unique=True, blank=False, null=False, verbose_name='Название'
    )
    fullname = models.CharField(
        max_length=255, unique=True, blank=True, null=True, verbose_name='Полное название'
    )
    english_name = models.CharField(
        max_length=255,
        unique=False,
        blank=True,
        null=True,
        verbose_name='Название на-английском языке',
    )
    english_fullname = models.CharField(
        max_length=255,
        unique=False,
        blank=True,
        null=True,
        verbose_name='Полное название на-английском языке',
    )
    iso3166_1_alpha2 = models.CharField(
        max_length=2,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Двухбуквенный код ISO 3166-1',
    )
    iso3166_1_alpha3 = models.CharField(
        max_length=3,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Трёхбуквенный код ISO 3166-1',
    )
    iso3166_1_numeric = models.CharField(
        max_length=3,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Цифровой код ISO 3166-1',
    )
    capital = models.OneToOneField(
        City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Столица'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Расположение'
    )

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return self.name


class VisitedCountry(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Страна'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Пользователь'
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Посещенная страна'
        verbose_name_plural = 'Посещенные страны'
        unique_together = ('country', 'user')

    def __str__(self):
        return self.country
