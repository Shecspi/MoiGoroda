from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User


class ShareSettings(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь',
        blank=False,
        null=False
    )
    switch_share_general = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Разрешить доступ к статистике'
    )
    switch_share_basic_info = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Отображать общую информацию'
    )
    switch_share_city_map = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Отображать карту городов'
    )
    switch_share_region_map = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Отображать карту регионов'
    )
