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

from typing import Any

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.urls import reverse
from django.utils.text import slugify
from tinymce.models import HTMLField  # type: ignore[import-untyped]

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
    slug = models.SlugField(
        max_length=60,
        unique=True,
        verbose_name='Слаг для URL',
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег блога'
        verbose_name_plural = 'Теги блога'

    def __str__(self) -> str:
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = self._generate_slug()
        super().save(*args, **kwargs)

    def _generate_slug(self) -> str:
        base = slugify(self.name, allow_unicode=True) or 'tag'
        base = base[:60].rstrip('-')
        slug = base
        suffix = 0
        while True:
            qs = BlogTag.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if not qs.exists():
                return slug
            suffix += 1
            slug = f'{base}-{suffix}'[:60]


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
    slug = models.SlugField(
        max_length=256,
        unique=True,
        verbose_name='Слаг для URL',
        blank=False,
        null=False,
    )
    content = HTMLField(verbose_name='Содержание', blank=False, null=False)
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
    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликована',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статья блога'
        verbose_name_plural = 'Статьи блога'

    def __str__(self) -> str:
        return self.title

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = self._generate_slug()

        super().save(*args, **kwargs)

    def _generate_slug(self) -> str:
        base = slugify(self.title, allow_unicode=True) or 'article'
        base = base[:256].rstrip('-')
        slug = base
        suffix = 0

        while True:
            qs = BlogArticle.objects.filter(slug=slug)

            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if not qs.exists():
                return slug

            suffix += 1
            slug = f'{base}-{suffix}'[:256]

    def get_absolute_url(self) -> str:
        return reverse('blog-article-detail', kwargs={'slug': self.slug})


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
