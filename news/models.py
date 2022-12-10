from django.contrib.auth.models import User
from django.db import models


class News(models.Model):
    """
    Таблица с новостями.
    """
    title = models.CharField(
        max_length=300,
        verbose_name='Заголовок',
        blank=False
    )
    content = models.TextField(
        verbose_name='Новость',
        blank=False
    )
    date_of_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
        blank=False
    )
    date_of_change = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее редактирование',
        blank=False
    )
    users_checked = models.ManyToManyField(
        User,
        blank=True
    )

    class Meta:
        verbose_name = 'Новости'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title
