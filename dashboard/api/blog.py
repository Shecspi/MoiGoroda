"""
----------------------------------------------

Copyright © Egor Vavilov (Shecspi)
Licensed under the Apache License, Version 2.0

----------------------------------------------
"""

from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, F, Func, Max, OuterRef, Q, Subquery, Sum, Value
from django.db.models.fields import CharField
from django.db.models.functions.datetime import TruncDate, TruncDay
from django.urls import reverse

from blog.models import BlogArticle, BlogArticleView
from city.models import VisitedCity
from collection.models import PersonalCollection
from country.models import VisitedCountry
from dashboard.schemas import (
    BlogArticleTableRow,
    BlogArticlesPageQuery,
    BlogArticlesPageResponse,
    DailyStatistics,
    DaysPath,
    PeriodComparisonStatistics,
    Quantity,
    RegistrationsComparisonQuery,
    RegistrationsRangeQuery,
    UserStatistics,
)
from dmr import Controller, Path, Query
from dmr.plugins.msgspec import MsgspecSerializer
from utils.decorators import is_superuser_json
from place.models import Place


from dashboard.statistics_helpers import (
    _collect_added_visited_cities_by_group,
    _collect_added_visited_countries_by_group,
    _collect_blog_article_views_by_group,
    _collect_blog_articles_added_by_group,
    _collect_personal_collections_by_group,
    _collect_places_by_group,
    _collect_registrations_by_group,
)


@is_superuser_json
class GetBlogArticlesAddedByRangeController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    """
    График добавления статей по дням.
    """

    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by != 'day':
            raise ValueError('group_by must be "day" for blog added chart')
        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_blog_articles_added_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )

@is_superuser_json
class GetBlogArticlesAddedComparisonController(
    Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]
):
    """
    Сравнение количества добавленных статей с предыдущим равным периодом.
    """

    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to

        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        current_count = BlogArticle.objects.filter(created_at__date__range=[date_from, date_to]).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)

        previous_count = BlogArticle.objects.filter(
            created_at__date__range=[previous_date_from, previous_date_to],
        ).count()

        delta = current_count - previous_count
        delta_percent = 0.0 if previous_count == 0 else round((delta / previous_count) * 100, 2)

        return PeriodComparisonStatistics(
            current_count=current_count,
            previous_count=previous_count,
            delta=delta,
            delta_percent=delta_percent,
        )

@is_superuser_json
class GetBlogArticlesByPageController(
    Query[BlogArticlesPageQuery], Controller[MsgspecSerializer]
):
    """
    Список статей блога для dashboard:
    - пагинация
    - сортировка по дате публикации (created_at) по убыванию
    - подсчет просмотров (исключая просмотры суперюзеров)
    """

    def get(self) -> BlogArticlesPageResponse:
        page = max(1, self.parsed_query.page)
        per_page = max(1, min(self.parsed_query.per_page, 50))

        exclude_superuser = Q(views__user__is_superuser=False) | Q(views__user__isnull=True)
        qs = (
            BlogArticle.objects.all()
            .annotate(view_count_total=Count('views', filter=exclude_superuser))
            .order_by('-created_at')
        )

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        items: list[BlogArticleTableRow] = []
        for article in page_obj.object_list:
            items.append(
                BlogArticleTableRow(
                    id=article.id,
                    title=article.title,
                    slug=article.slug,
                    published_date=article.created_at.strftime('%d.%m.%Y'),
                    view_count_total=int(article.view_count_total or 0),
                    detail_url=reverse(
                        'blog-article-detail',
                        kwargs={'slug': article.slug},
                    ),
                )
            )

        return BlogArticlesPageResponse(
            page=page_obj.number,
            total_pages=paginator.num_pages,
            per_page=per_page,
            total_count=paginator.count,
            items=items,
        )

@is_superuser_json
class GetBlogArticlesViewsByRangeController(
    Query[RegistrationsRangeQuery], Controller[MsgspecSerializer]
):
    """
    График просмотров статей по дням за диапазон.
    """

    def get(self) -> list[DailyStatistics]:
        group_by = self.parsed_query.group_by
        if group_by != 'day':
            raise ValueError('group_by must be "day" for blog views')

        if self.parsed_query.date_from > self.parsed_query.date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        return _collect_blog_article_views_by_group(
            date_from=self.parsed_query.date_from,
            date_to=self.parsed_query.date_to,
            group_by=group_by,
        )

@is_superuser_json
class GetBlogArticlesViewsComparisonController(
    Query[RegistrationsComparisonQuery], Controller[MsgspecSerializer]
):
    """
    Сравнение количества просмотров статей с предыдущим равным периодом.
    """

    def get(self) -> PeriodComparisonStatistics:
        date_from = self.parsed_query.date_from
        date_to = self.parsed_query.date_to

        if date_from > date_to:
            raise ValueError('date_from must be less than or equal to date_to')

        exclude_views_q = Q(user__isnull=True) | Q(user__is_superuser=False)

        current_count = BlogArticleView.objects.filter(
            viewed_at__date__range=[date_from, date_to],
        ).filter(exclude_views_q).count()

        period_days = (date_to - date_from).days + 1
        previous_date_to = date_from - timedelta(days=1)
        previous_date_from = previous_date_to - timedelta(days=period_days - 1)

        previous_count = BlogArticleView.objects.filter(
            viewed_at__date__range=[previous_date_from, previous_date_to],
        ).filter(exclude_views_q).count()

        delta = current_count - previous_count
        delta_percent = 0.0 if previous_count == 0 else round((delta / previous_count) * 100, 2)

        return PeriodComparisonStatistics(
            current_count=current_count,
            previous_count=previous_count,
            delta=delta,
            delta_percent=delta_percent,
        )

@is_superuser_json
class GetBlogArticlesViewsTotalController(Controller[MsgspecSerializer]):
    """
    Общее количество просмотров статей:
    исключаем просмотры суперюзеров, учитываем гостей (user = NULL) и обычных пользователей.
    """

    def get(self) -> Quantity:
        exclude_views_q = Q(user__isnull=True) | Q(user__is_superuser=False)
        qty = BlogArticleView.objects.filter(exclude_views_q).count()
        return Quantity(count=qty)

@is_superuser_json
class GetBlogLastAddedArticlesController(Controller[MsgspecSerializer]):
    """
    10 последних добавленных статей (по созданию).
    """

    def get(self) -> list[BlogArticleTableRow]:
        exclude_superuser = Q(views__user__is_superuser=False) | Q(views__user__isnull=True)
        qs = (
            BlogArticle.objects.all()
            .annotate(view_count_total=Count('views', filter=exclude_superuser))
            .order_by('-created_at')[:10]
        )

        items: list[BlogArticleTableRow] = []
        for article in qs:
            items.append(
                BlogArticleTableRow(
                    id=article.id,
                    title=article.title,
                    slug=article.slug,
                    published_date=article.created_at.strftime('%d.%m.%Y'),
                    view_count_total=int(article.view_count_total or 0),
                    detail_url=reverse('blog-article-detail', kwargs={'slug': article.slug}),
                )
            )
        return items

@is_superuser_json
class GetBlogTopViewedArticlesController(Controller[MsgspecSerializer]):
    """
    10 самых просматриваемых статей (по общему числу просмотров).
    """

    def get(self) -> list[BlogArticleTableRow]:
        exclude_superuser = Q(views__user__is_superuser=False) | Q(views__user__isnull=True)
        qs = (
            BlogArticle.objects.all()
            .annotate(view_count_total=Count('views', filter=exclude_superuser))
            .order_by('-view_count_total', '-created_at')[:10]
        )

        items: list[BlogArticleTableRow] = []
        for article in qs:
            items.append(
                BlogArticleTableRow(
                    id=article.id,
                    title=article.title,
                    slug=article.slug,
                    published_date=article.created_at.strftime('%d.%m.%Y'),
                    view_count_total=int(article.view_count_total or 0),
                    detail_url=reverse('blog-article-detail', kwargs={'slug': article.slug}),
                )
            )
        return items

