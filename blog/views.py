"""
Реализует классы для отображения статей блога.

* BlogArticleList - Отображает список статей
* BlogArticleDetail - Отображает полный текст статьи
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from typing import Any

from django.db.models import Count, Q, QuerySet
from django.http import HttpRequest
from django.views.generic import DetailView, ListView

from django.shortcuts import get_object_or_404

from blog.models import BlogArticle, BlogTag, BlogArticleView


class BlogArticleList(ListView):  # type: ignore[type-arg]
    """
    Отображает список статей блога с разделением по страницам.
    Поддерживает фильтрацию по тегу через URL blog/tag/<tag_slug>/.
    """

    model = BlogArticle
    paginate_by = 5
    ordering = '-created_at'
    template_name = 'blog/article_list.html'
    context_object_name = 'article_list'

    def get_queryset(self) -> QuerySet[BlogArticle]:
        qs = super().get_queryset().prefetch_related('tags', 'city')
        tag_slug = self.kwargs.get('tag_slug')

        if tag_slug is not None:
            qs = qs.filter(tags__slug=tag_slug)

        if self.request.user.is_superuser:
            qs = qs.annotate(
                view_count_total=Count('views'),
                view_count_auth=Count('views', filter=Q(views__user__isnull=False)),
                view_count_guest=Count('views', filter=Q(views__user__isnull=True)),
            )

        return qs

    def get_context_data(
        self, *, object_list: QuerySet[BlogArticle] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'blog'
        context['page_title'] = 'Блог о городах и достопримечательностях'
        context['page_description'] = (
            'Статьи о городах и достопримечательностях проекта «Мои города»'
        )
        tag_slug = self.kwargs.get('tag_slug')

        if tag_slug is not None:
            tag = get_object_or_404(BlogTag, slug=tag_slug)
            context['filter_tag'] = tag
            context['page_description'] = (
                f'Статьи о городах и достопримечательностях с тегом «{tag.name}»'
            )

        context['show_view_stats'] = self.request.user.is_superuser

        return context


class BlogArticleDetail(DetailView):  # type: ignore[type-arg]
    """
    Отображает полный текст статьи.
    При каждом просмотре создаёт запись BlogArticleView.
    """

    model = BlogArticle
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self) -> QuerySet[BlogArticle]:
        return super().get_queryset().prefetch_related('tags').select_related('city')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Создаём запись о просмотре
        ip_address = self._get_client_ip(self.request)
        BlogArticleView.objects.create(
            article=self.object,
            user=self.request.user if self.request.user.is_authenticated else None,
            ip_address=ip_address,
        )

        context['active_page'] = 'blog'
        context['page_title'] = self.object.title
        context['page_description'] = self.object.title
        if self.request.user.is_superuser:
            views_qs = self.object.views
            context['show_view_stats'] = True
            context['view_count_total'] = views_qs.count()
            context['view_count_auth'] = views_qs.filter(user__isnull=False).count()
            context['view_count_guest'] = views_qs.filter(user__isnull=True).count()
        else:
            context['show_view_stats'] = False

        return context

    def _get_client_ip(self, request: HttpRequest) -> str | None:
        """Извлекает IP-адрес клиента из запроса."""
        ip = request.META.get('REMOTE_ADDR')

        if ip:
            return ip

        return None
