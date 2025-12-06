"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from city.models import City


class Collection(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,
    )
    city = models.ManyToManyField(City, related_name='collections_list')

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return str(reverse('collection-detail-list', kwargs={'pk': self.pk}))

    class Meta:
        ordering = ['title']
        verbose_name = 'Коллекция'
        verbose_name_plural = 'Коллекции'


class FavoriteCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_collections')
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.username} - {self.collection.title}'

    class Meta:
        unique_together = ('user', 'collection')
        ordering = ['-created_at']
        verbose_name = 'Избранная коллекция'
        verbose_name_plural = 'Избранные коллекции'


class PersonalCollection(models.Model):
    """
    Персональная коллекция городов, созданная пользователем.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='personal_collections',
        verbose_name='Пользователь',
    )
    title = models.CharField(
        max_length=256,
        verbose_name='Название',
        blank=False,
    )
    city = models.ManyToManyField(
        City,
        related_name='personal_collections_list',
        verbose_name='Города',
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

    def get_absolute_url(self) -> str:
        # TODO: Создать URL для детального просмотра персональной коллекции
        return str(reverse('collection-list'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Персональная коллекция'
        verbose_name_plural = 'Персональные коллекции'
