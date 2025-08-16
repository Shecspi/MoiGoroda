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

    def __str__(self):
        return f'Подписка {self.subscribe_from} на {self.subscribe_to}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('subscribe_from', 'subscribe_to')
