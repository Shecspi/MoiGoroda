"""

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

"""

import uuid

from django.contrib.auth.models import User
from django.db import models


class TagOSM(models.Model):
    name = models.CharField(
        max_length=255, blank=False, null=False, unique=False, verbose_name='Название'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Category(models.Model):
    name = models.CharField(
        max_length=255, blank=False, null=False, unique=False, verbose_name='Название'
    )
    tags = models.ManyToManyField(TagOSM, blank=True, verbose_name='Теги OpenStreetMap')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class PlaceCollection(models.Model):
    """
    Коллекция мест пользователя. Название, привязка к пользователю, публичность.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='place_collections',
        verbose_name='Пользователь',
    )
    title = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Публичная коллекция',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    def __str__(self) -> str:
        return f'{self.user.username} - {self.title}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Коллекция мест'
        verbose_name_plural = 'Коллекции мест'


class Place(models.Model):
    name = models.CharField(
        max_length=255, blank=False, null=False, unique=False, verbose_name='Название'
    )
    latitude = models.FloatField(blank=False, null=False, unique=False, verbose_name='Широта')
    longitude = models.FloatField(blank=False, null=False, unique=False, verbose_name='Долгота')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время редактирования',
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    is_visited = models.BooleanField(
        default=True,
        verbose_name='Место посещено',
    )
    collection = models.ForeignKey(
        PlaceCollection,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='places',
        verbose_name='Коллекция',
    )

    class Meta:
        verbose_name = 'Интересное место'
        verbose_name_plural = 'Интересные места'
