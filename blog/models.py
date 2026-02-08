"""
Описывает модели приложения Blog.

* BlogTag - Теги для классификации статей
* BlogArticle - Статьи блога
* BlogArticleView - Лог просмотров статей
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field  # type: ignore[import-untyped]

from city.models import City


class BlogTag(models.Model):
    """
    Теги для классификации и поиска статей блога.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег блога'
        verbose_name_plural = 'Теги блога'

    def __str__(self) -> str:
        return self.name


class BlogArticle(models.Model):
    """
    Статья блога.
    """

    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок',
        blank=False,
        null=False,
    )
    content = CKEditor5Field(
        verbose_name='Содержание',
        blank=False,
        null=False,
    )
    city = models.ForeignKey(
        City,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name='Город',
        related_name='blog_articles',
    )
    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        verbose_name='Теги',
        related_name='articles',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статья блога'
        verbose_name_plural = 'Статьи блога'

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('blog-article-detail', kwargs={'pk': self.pk})


class BlogArticleView(models.Model):
    """
    Лог каждого просмотра страницы статьи.
    Позволяет считать просмотры за период (дашборд) и разделять по авторизованным/гостям.
    """

    article = models.ForeignKey(
        BlogArticle,
        on_delete=CASCADE,
        verbose_name='Статья',
        related_name='views',
    )
    user = models.ForeignKey(
        User,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name='Пользователь',
        related_name='blog_article_views',
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP-адрес',
    )
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата просмотра',
        db_index=True,
    )

    class Meta:
        ordering = ['-viewed_at']
        verbose_name = 'Просмотр статьи'
        verbose_name_plural = 'Просмотры статей'

    def __str__(self) -> str:
        user_str = str(self.user) if self.user else 'Гость'
        return f'{self.article.title} — {user_str} ({self.viewed_at})'
