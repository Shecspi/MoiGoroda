
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE
from django.urls import reverse

from region.models import Region


class City(models.Model):
    """
    Таблица, хранящая в себе список городов.
    Редактируется только из администраторской учётной записи.

    """
    title = models.CharField(
        max_length=100,
        verbose_name='Название',
        blank=False,
        null=False
    )
    region = models.ForeignKey(
        Region,
        on_delete=CASCADE,
        verbose_name='Регион',
        blank=False,
        null=False
    )
    population = models.PositiveIntegerField(
        verbose_name='Численность населения',
        blank=True,
        null=True
    )
    date_of_foundation = models.PositiveSmallIntegerField(
        verbose_name='Год основания',
        blank=True,
        null=True
    )
    coordinate_width = models.FloatField(
        verbose_name='Широта',
        blank=False,
        null=False
    )
    coordinate_longitude = models.FloatField(
        verbose_name='Долгота',
        blank=False,
        null=False
    )
    wiki = models.URLField(
        max_length=256,
        verbose_name='Ссылка на Wikipedia',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['title']
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
        blank=False,
        null=False
    )
    region = models.ForeignKey(
        Region,
        on_delete=CASCADE,
        verbose_name='Регион',
        help_text='Выберите регион, в котором находится посещённый город. '
                  'Список городов выбранного региона подгрузится автоматически в поле "Город".',
        blank=False,
        null=False
    )
    city = models.ForeignKey(
        City,
        on_delete=CASCADE,
        verbose_name='Город',
        help_text='Выберите город, который посетили.',
        related_name='visitedcity',
        blank=False,
        null=False
    )
    date_of_visit = models.DateField(
        verbose_name='Дата посещения',
        help_text='Укажите дату посещения города в формате ДД.ММ.ГГГГ. '
                  'На основе этой даты будет происходить сортировка городов, '
                  'а также это влияет на отображаемую статистику посещённых городов за год.',
        blank=True,
        null=True,
    )
    has_magnet = models.BooleanField(
        verbose_name='Наличие магнита',
        help_text='Отметьте этот пункт, если у Вас есть магнитик с названием города. '
                  'В списке городов можно будет отфильтровать только те города, которые без магнитов.',
        blank=True,
        null=False,
        default=False
    )
    impression = models.TextField(
        verbose_name='Впечатления о городе',
        blank=True,
        null=True
    )
    rating = models.SmallIntegerField(
        verbose_name='Рейтинг',
        help_text='Поставьте оценку городу. 1 - плохо, 5 - отлично.',
        blank=False,
        null=False
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Посещённый город'
        verbose_name_plural = 'Посещённые города'

    def __str__(self):
        return self.city.title

    def get_absolute_url(self):
        return reverse('city-selected', kwargs={'pk': self.pk})
