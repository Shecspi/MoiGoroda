from django.db import models


class TypeObject(models.Model):
    name = models.CharField(
        max_length=255, blank=False, null=False, unique=False, verbose_name='Название'
    )

    class Meta:
        verbose_name = 'Тип объекта'
        verbose_name_plural = 'Типы объектов'


class Place(models.Model):
    name = models.CharField(
        max_length=255, blank=False, null=False, unique=False, verbose_name='Название'
    )
    latitude = models.FloatField(blank=False, null=False, unique=False, verbose_name='Широта')
    longitude = models.FloatField(blank=False, null=False, unique=False, verbose_name='Долгота')
    type_object = models.ForeignKey(
        TypeObject, on_delete=models.PROTECT, verbose_name='Тип объекта'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время редактирования',
    )

    class Meta:
        verbose_name = 'Интересное место'
        verbose_name_plural = 'Интересные места'
