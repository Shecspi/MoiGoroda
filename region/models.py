"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db import models
from django.db.models import CASCADE, PROTECT
from django.urls import reverse

from country.models import Country

TYPES_OF_REGIONS = [
    ('R', 'республика'),
    ('K', 'край'),
    ('O', 'область'),
    ('G', 'город федерального значения'),
    ('AOb', 'автономная область'),
    ('AOk', 'автономный округ'),
]


class Area(models.Model):
    country = models.ForeignKey(
        Country, on_delete=PROTECT, verbose_name='Страна', blank=False, null=False
    )
    title = models.CharField(
        max_length=100, verbose_name='Название', blank=False, null=False, unique=True
    )

    class Meta:
        verbose_name = 'Федеральный округ'
        verbose_name_plural = 'Федеральные округа'

    def __str__(self):
        return self.title


class Region(models.Model):
    area = models.ForeignKey(
        Area, on_delete=CASCADE, verbose_name='Федеральный округ', blank=True, null=True
    )
    country = models.ForeignKey(
        Country, on_delete=PROTECT, verbose_name='Страна', blank=False, null=False
    )
    title = models.CharField(max_length=100, verbose_name='Название', blank=False, null=False)
    type = models.CharField(
        max_length=100,
        choices=TYPES_OF_REGIONS,
        verbose_name='Тип субъекта',
        blank=False,
        null=False,
    )
    iso3166 = models.CharField(
        max_length=10, verbose_name='Код ISO3166', blank=False, null=False, unique=True
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'
        unique_together = ('title', 'type')

    def __str__(self):
        # Для городов федерального значения просто выводим название
        if self.type == 'G':
            return self.title
        # Для республик, кроме некоторых, слово "Республика" не используем
        elif self.type == 'R':
            match self.title:
                case (
                    'Кабардино-Балкарская'
                    | 'Карачаево-Черкесская'
                    | 'Удмуртская'
                    | 'Чеченская'
                    | 'Чувашская'
                ):
                    return self.title + ' республика'
                case _:
                    return self.title
        # Во всех остальных случаях выводим название + тип субъекта
        else:
            return self.title + ' ' + self.get_type_display().lower()

    def get_absolute_url(self):
        return reverse('region-selected-list', kwargs={'pk': self.pk})
