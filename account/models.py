from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User
from django.urls import reverse


class ShareSettings(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=CASCADE,
        verbose_name='Пользователь',
        blank=False,
        null=False
    )
    can_share = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Разрешить доступ к статистике'
    )
    can_share_dashboard = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Отображать общую информацию'
    )
    can_share_city_map = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Отображать карту городов'
    )
    can_share_region_map = models.BooleanField(
        blank=True,
        null=False,
        default=False,
        verbose_name='Отображать карту регионов'
    )

    def get_absolute_url(self):
        return reverse('share', kwargs={'pk': self.pk})
