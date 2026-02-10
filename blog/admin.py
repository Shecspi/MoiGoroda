"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import cast

from django.contrib import admin
from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest

from .models import BlogArticle, BlogArticleView, BlogTag


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Административная панель для модели BlogTag."""

    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogArticle)
class BlogArticleAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Административная панель для модели BlogArticle."""

    list_display = (
        'title',
        'city',
        'is_published',
        'created_at',
        'get_views_authenticated',
        'get_views_guest',
        'get_views_total',
    )
    list_filter = ('is_published', 'city', 'tags', 'created_at')
    search_fields = ('title', 'content')
    autocomplete_fields = ('city',)
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('title',)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[BlogArticle]:
        base_qs = super().get_queryset(request)
        qs: QuerySet[BlogArticle] = cast(QuerySet[BlogArticle], base_qs)
        exclude_superuser = Q(views__user__is_superuser=False) | Q(views__user__isnull=True)
        return qs.annotate(
            _views_authenticated=Count(
                'views',
                filter=exclude_superuser & Q(views__user__isnull=False),
            ),
            _views_guest=Count(
                'views',
                filter=exclude_superuser & Q(views__user__isnull=True),
            ),
        )

    def get_views_authenticated(self, obj: BlogArticle) -> int:
        return getattr(obj, '_views_authenticated', 0)

    get_views_authenticated.short_description = 'Просмотры (авториз.)'  # type: ignore[attr-defined]
    get_views_authenticated.admin_order_field = '_views_authenticated'  # type: ignore[attr-defined]

    def get_views_guest(self, obj: BlogArticle) -> int:
        return getattr(obj, '_views_guest', 0)

    get_views_guest.short_description = 'Просмотры (гости)'  # type: ignore[attr-defined]
    get_views_guest.admin_order_field = '_views_guest'  # type: ignore[attr-defined]

    def get_views_total(self, obj: BlogArticle) -> int:
        auth = getattr(obj, '_views_authenticated', 0)
        guest = getattr(obj, '_views_guest', 0)
        return auth + guest

    get_views_total.short_description = 'Просмотры (всего)'  # type: ignore[attr-defined]


@admin.register(BlogArticleView)
class BlogArticleViewAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Административная панель для просмотра лога BlogArticleView."""

    list_display = ('article', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    readonly_fields = ('article', 'user', 'ip_address', 'viewed_at')
    search_fields = ('article__title', 'user__username', 'ip_address')
