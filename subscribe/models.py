from django.db import models
from django.contrib.auth.models import User

from city.models import City


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


class VisitedCityNotification(models.Model):
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Получатель'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='Отправитель',
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='city', verbose_name='Посещённый город'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
