from django.contrib.auth.models import User
from django.db import models


class AdvertisementException(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, которому не показывается реклама',
    )
    deadline = models.DateField(
        null=False, blank=False, verbose_name='Дата, до которой реклама не показывается'
    )

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Исключённый пользователь'
        verbose_name_plural = 'Исключённые пользователи'
