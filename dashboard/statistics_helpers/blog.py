"""
Статистика блога для dashboard.
"""

from __future__ import annotations

from datetime import date

from django.db.models import Count, Q
from django.urls import reverse

from blog.models import BlogArticle, BlogArticleView
from dashboard.schemas import BlogArticleTableRow, BlogArticlesCardOverview, DailyStatistics
from dashboard.statistics_helpers.common import (
    build_blog_overview_period,
    build_datetime_range,
    build_grouped_daily_statistics,
    build_period_comparison_stats,
)


def _collect_blog_article_views_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    exclude_views_q = Q(user__isnull=True) | Q(user__is_superuser=False)
    return build_grouped_daily_statistics(
        base_queryset=BlogArticleView.objects.filter(exclude_views_q),
        datetime_field='viewed_at',
        date_from=date_from,
        date_to=date_to,
        group_by=group_by,
    )


def _collect_blog_articles_added_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    return build_grouped_daily_statistics(
        base_queryset=BlogArticle.objects.all(),
        datetime_field='created_at',
        date_from=date_from,
        date_to=date_to,
        group_by=group_by,
    )


def collect_blog_last_added_articles_items(limit: int = 10) -> list[BlogArticleTableRow]:
    """Возвращает N последних добавленных статей с количеством просмотров."""
    exclude_views_article = Q(views__user__isnull=True) | Q(views__user__is_superuser=False)

    qs = (
        BlogArticle.objects.all()
        .annotate(view_count_total=Count('views', filter=exclude_views_article))
        .order_by('-created_at')[:limit]
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
            ),
        )
    return items


def collect_blog_top_viewed_articles_items(limit: int = 10) -> list[BlogArticleTableRow]:
    """Возвращает N самых просматриваемых статей с количеством просмотров."""
    exclude_views_article = Q(views__user__isnull=True) | Q(views__user__is_superuser=False)

    qs = (
        BlogArticle.objects.all()
        .annotate(view_count_total=Count('views', filter=exclude_views_article))
        .order_by('-view_count_total', '-created_at')[:limit]
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
            ),
        )
    return items


def count_blog_articles_added_in_range(date_from: date, date_to: date) -> int:
    dt_from, dt_to = build_datetime_range(date_from, date_to)
    return BlogArticle.objects.filter(created_at__gte=dt_from, created_at__lt=dt_to).count()


def count_blog_article_views_in_range(date_from: date, date_to: date) -> int:
    exclude_views_view = Q(user__isnull=True) | Q(user__is_superuser=False)
    dt_from, dt_to = build_datetime_range(date_from, date_to)
    return (
        BlogArticleView.objects.filter(viewed_at__gte=dt_from, viewed_at__lt=dt_to)
        .filter(exclude_views_view)
        .count()
    )


def collect_blog_last_added_card_overview(
    now_date: date, days: int = 30
) -> BlogArticlesCardOverview:
    """Карточка 'Последние добавленные статьи'."""
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)

    items = collect_blog_last_added_articles_items(limit=10)
    current_count = count_blog_articles_added_in_range(period_from, period_to)
    previous_count = count_blog_articles_added_in_range(prev_from, prev_to)

    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_blog_articles_added_by_group(
        date_from=period_from, date_to=period_to, group_by='day'
    )

    return BlogArticlesCardOverview(items=items, comparison=comparison, chart=chart)


def collect_blog_top_viewed_card_overview(
    now_date: date, days: int = 60
) -> BlogArticlesCardOverview:
    """Карточка 'Самые просматриваемые статьи'."""
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)

    items = collect_blog_top_viewed_articles_items(limit=10)
    current_count = count_blog_article_views_in_range(period_from, period_to)
    previous_count = count_blog_article_views_in_range(prev_from, prev_to)

    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_blog_article_views_by_group(
        date_from=period_from, date_to=period_to, group_by='day'
    )

    return BlogArticlesCardOverview(items=items, comparison=comparison, chart=chart)


__all__ = [
    '_collect_blog_article_views_by_group',
    '_collect_blog_articles_added_by_group',
    'collect_blog_last_added_articles_items',
    'collect_blog_top_viewed_articles_items',
    'count_blog_articles_added_in_range',
    'count_blog_article_views_in_range',
    'collect_blog_last_added_card_overview',
    'collect_blog_top_viewed_card_overview',
]
