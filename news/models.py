"""
Описывает модели приложения News.

* News - Модель, хранящая в себе всю информацию о новостиях.
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User
from django.db import models
from mdeditor.fields import MDTextField


class News(models.Model):
    """
    Хранит в себе всю информацию о новостях.
    """

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False,
        null=False,
        help_text='Указанный заголовок новости будет отображатьсят только в админ-панели.<br>'
        'Пользователи его не увидят. Для них необходимо указывать заголовок новости в поле ниже.',
    )
    content = MDTextField(verbose_name='Новость', blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    users_read = models.ManyToManyField(User, blank=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title
