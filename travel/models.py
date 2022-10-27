
from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE


class Area(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название', blank=False)

    class Meta:
        verbose_name = 'Федеральный округ'
        verbose_name_plural = 'Федеральные округа'

    def __str__(self):
        return self.title


class Region(models.Model):
    """
    Таблица, хранящая в себе список регионов.
    Редактируется только из администраторской учётной записи.

    """
    TYPES_OF_REGIONS = [
        ('R', 'республика'),
        ('K', 'край'),
        ('O', 'область'),
        ('G', 'город федерального значения'),
        ('AOb', 'автономная область'),
        ('AOk', 'автономный округ')
    ]

    area = models.ForeignKey(
        Area,
        on_delete=CASCADE,
        verbose_name='Федеральный округ',
        blank=False
    )
    title = models.CharField(
        max_length=100,
        verbose_name='Название',
        blank=False
    )
    type = models.CharField(
        max_length=100,
        choices=TYPES_OF_REGIONS,
        verbose_name='Тип субъекта',
        blank=False
    )
    iso3166 = models.CharField(
        max_length=10,
        verbose_name='Код ISO3166',
        blank=True,
        default=''
    )

    class Meta:
        ordering = ['title']
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        # Для городов федерального значения просто выводим название
        if self.type == 'G':
            return self.title
        # Для республик, кроме некоторых, слово "Республика" не используем)
        elif self.type == 'R':
            match self.title:
                case 'Кабардино-Балкарская' | 'Карачаево-Черкесская' | 'Удмуртская' | 'Чеченская' | 'Чувашская':
                    return self.title + ' республика'
                case _:
                    return self.title
        # Во всех остальных случаях выводим название + тип субъекта
        else:
            return self.title + ' ' + self.get_type_display().lower()


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
        blank=False)  # ToDo Добавить проверку от 1 до 5

    class Meta:
        verbose_name = 'Посещённый город'
        verbose_name_plural = 'Посещённые города'

    def __str__(self):
        return self.city.title
