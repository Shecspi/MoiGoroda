
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE

from region.models import Region


class City(models.Model):
    """
    Таблица, хранящая в себе список городов.
    Редактируется только из администраторской учётной записи.

    """
    title = models.CharField(
        max_length=100,
        verbose_name='Название',
        blank=False)
    region = models.ForeignKey(
        Region,
        on_delete=CASCADE,
        verbose_name='Регион',
        blank=False)
    population = models.PositiveIntegerField(
        verbose_name='Численность населения',
        blank=True,
        default=0)
    date_of_foundation = models.PositiveSmallIntegerField(
        verbose_name='Год основания',
        blank=True,
        default=0)
    coordinate_width = models.FloatField(
        verbose_name='Широта',
        blank=False)
    coordinate_longitude = models.FloatField(
        verbose_name='Долгота',
        blank=False)
    wiki = models.URLField(
        max_length=256,
        verbose_name='Ссылка на Wikipedia',
        blank=True,
        default='')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.title


class VisitedCity(models.Model):
    """
    Сводная таблица, хранящая информацию о посещённых городах пользователей.
    """
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь',
        blank=False)
    region = models.ForeignKey(
        Region,
        on_delete=CASCADE,
        verbose_name='Регион',
        blank=False)
    city = models.ForeignKey(
        City,
        on_delete=CASCADE,
        verbose_name='Город',
        blank=False)
    date_of_visit = models.DateField(
        verbose_name='Дата посещения',
        null=True,
        blank=True)
    has_magnet = models.BooleanField(
        verbose_name='Наличие магнита',
        blank=False)
    impression = models.TextField(
        verbose_name='Впечатления о городе',
        blank=True,
        default='')
    rating = models.SmallIntegerField(
        verbose_name='Рейтинг',
        blank=False,
        default=0)

    class Meta:
        verbose_name = 'Посещённый город'
        verbose_name_plural = 'Посещённые города'

    def __str__(self):
        return self.city.title
