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
