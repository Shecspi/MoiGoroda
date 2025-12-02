"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User as DjangoUser
from django.urls import reverse


class User(DjangoUser):
    """Прокси-модель для добавления русских названий в админке."""

    class Meta:
        proxy = True
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class ShareSettings(models.Model):
    user = models.ForeignKey(
        DjangoUser, on_delete=CASCADE, verbose_name='Пользователь', blank=False, null=False
    )
    can_share = models.BooleanField(
        blank=True, null=False, default=False, verbose_name='Разрешить доступ к статистике'
    )
    can_share_dashboard = models.BooleanField(
        blank=True, null=False, default=False, verbose_name='Отображать общую информацию'
    )
    can_share_city_map = models.BooleanField(
        blank=True, null=False, default=False, verbose_name='Отображать карту городов'
    )
    can_share_region_map = models.BooleanField(
        blank=True, null=False, default=False, verbose_name='Отображать карту регионов'
    )
    can_subscribe = models.BooleanField(
        blank=True, null=False, default=False, verbose_name='Разрешить подписываться'
    )

    def get_absolute_url(self) -> str:
        return reverse('share', kwargs={'pk': self.pk})

    def __str__(self) -> str:
        return f'Параметры публикации статистики пользователя {self.user}'

    class Meta:
        verbose_name = 'Параметры публикации статистики'
        verbose_name_plural = 'Параметры публикации статистики'


class UserConsent(models.Model):
    user = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    consent_given = models.BooleanField(default=True, verbose_name='Согласие дано')
    consent_timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата и время согласия'
    )
    policy_version = models.CharField(max_length=10, verbose_name='Версия политики')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP-адрес')

    class Meta:
        verbose_name = 'Согласие пользователя'
        verbose_name_plural = 'Согласия пользователей'
