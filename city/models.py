"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import CASCADE, PROTECT
from django.urls import reverse

from country.models import Country
from region.models import Region


class City(models.Model):
    """
    Таблица, хранящая в себе список городов.
    Редактируется только из администраторской учётной записи.
    """

    title = models.CharField(max_length=100, verbose_name='Название', blank=False, null=False)
    country = models.ForeignKey(
        Country, on_delete=PROTECT, verbose_name='Страна', blank=False, null=False
    )
    region = models.ForeignKey(
        Region, on_delete=CASCADE, verbose_name='Регион', blank=True, null=True
    )
    population = models.PositiveIntegerField(
        verbose_name='Численность населения', blank=True, null=True
    )
    date_of_foundation = models.PositiveSmallIntegerField(
        verbose_name='Год основания', blank=True, null=True
    )
    coordinate_width = models.FloatField(verbose_name='Широта', blank=False, null=False)
    coordinate_longitude = models.FloatField(verbose_name='Долгота', blank=False, null=False)
    wiki = models.URLField(
        max_length=256, verbose_name='Ссылка на Wikipedia', blank=True, null=True
    )
    image = models.URLField(
        verbose_name='Ссылка на изображение',
        blank=True,
        null=False,
        max_length=2048,
    )
    image_source_text = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Название источника изображения'
    )
    image_source_link = models.URLField(
        blank=True, null=True, verbose_name='Ссылка на источник изображения'
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('city-selected', kwargs={'pk': self.pk})


class VisitedCity(models.Model):
    """
    Сводная таблица, хранящая информацию о посещённых городах пользователей.
    """

    user = models.ForeignKey(
        User, on_delete=CASCADE, verbose_name='Пользователь', blank=False, null=False
    )
    city = models.ForeignKey(
        City,
        on_delete=CASCADE,
        verbose_name='Город',
        help_text='Выберите город, который посетили.',
        related_name='visitedcity',
        blank=False,
        null=False,
    )
    date_of_visit = models.DateField(
        verbose_name='Дата посещения',
        help_text='Укажите дату посещения города в формате ДД.ММ.ГГГГ. '
        'На основе этой даты будет происходить сортировка городов, '
        'а также это влияет на отображаемую статистику посещённых городов за год.',
        blank=True,
        null=True,
        db_index=True,
    )
    has_magnet = models.BooleanField(
        verbose_name='Наличие сувенира из города',
        help_text='Отметьте этот пункт, если у Вас в коллекции есть сувенир из города. '
        'В списке городов можно будет отфильтровать только те города, сувенира из которых у Вас ещё нет.',
        blank=True,
        null=False,
        default=False,
    )
    impression = models.TextField(
        verbose_name='Впечатления о городе',
        blank=True,
        null=True,
        help_text='В этом поле Вы можете использовать некоторые элементы разметки Markdown, для того, чтобы стилизовать текст.<br>Доступные элементы: заголовки, жирный и курсивный шрифты, ссылки, нумерованные и ненумерованные списки, разделительная линия.',
    )
    rating = models.SmallIntegerField(
        verbose_name='Рейтинг',
        help_text='Поставьте оценку городу. 1 - плохо, 5 - отлично.',
        blank=False,
        null=False,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_index=True,
    )
    is_first_visit = models.BooleanField(
        verbose_name='Первый раз в городе?',
        blank=True,
        null=True,
        default=True,
        db_index=True,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Посещённый город'
        verbose_name_plural = 'Посещённые города'
        unique_together = ['user', 'city', 'date_of_visit']

    def __str__(self) -> str:
        return self.city.title

    def get_absolute_url(self) -> str:
        return reverse('city-selected', kwargs={'pk': self.pk})
