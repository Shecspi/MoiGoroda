from django.contrib.auth.models import User
from django.db import models

from city.models import City


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
        City, on_delete=models.CASCADE, related_name='city', verbose_name='Посещённый город1'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
