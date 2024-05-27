from django.db import models
from django.contrib.auth.models import User


class Subscribe(models.Model):
    subscribe_from = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, который подписался',
        related_name='subscribe_from_set',
        blank=False,
        null=False,
    )
    subscribe_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, на которого подписались',
        related_name='subscribe_to_set',
        blank=False,
        null=False,
    )
