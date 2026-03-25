"""
Вспомогательные функции для подсчёта статистики dashboard.

Перенесены из `dashboard/api.py`, чтобы в `api.py` оставались только эндпоинты.
"""

from __future__ import annotations

from datetime import date, timedelta, timezone

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions.datetime import TruncDate, TruncDay, TruncMonth, TruncWeek
from django.urls import reverse

from blog.models import BlogArticle, BlogArticleView
from city.models import VisitedCity
from collection.models import PersonalCollection
from country.models import VisitedCountry
from dashboard.schemas import (
    BlogArticleTableRow,
    BlogArticlesCardOverview,
    DailyStatistics,
    PeriodComparisonStatistics,
)
from place.models import Place


def _get_group_trunc_function(group_by: str) -> type[TruncDay] | type[TruncWeek] | type[TruncMonth]:
    if group_by == 'day':
        return TruncDay
    if group_by == 'week':
        return TruncWeek
    if group_by == 'month':
        return TruncMonth
    raise ValueError('group_by must be one of: day, week, month')


def _format_group_label(group_date: date, group_by: str) -> str:
    if group_by == 'day':
        return group_date.strftime('%d.%m.%Y')
    if group_by == 'week':
        iso_year, iso_week, _ = group_date.isocalendar()
        return f'{iso_week:02d}.{iso_year}'
    return group_date.strftime('%m.%Y')


def _next_group_date(group_date: date, group_by: str) -> date:
    if group_by == 'day':
        return group_date + timedelta(days=1)
    if group_by == 'week':
        return group_date + timedelta(weeks=1)

    # Переход на первый день следующего месяца
    if group_date.month == 12:
        return date(group_date.year + 1, 1, 1)
    return date(group_date.year, group_date.month + 1, 1)


def _collect_registrations_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        User.objects.filter(
            date_joined__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('date_joined', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_added_visited_cities_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        VisitedCity.objects.filter(
            created_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_added_visited_countries_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        VisitedCountry.objects.filter(
            added_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('added_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_places_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        Place.objects.filter(
            created_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}
    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_personal_collections_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    queryset = (
        PersonalCollection.objects.filter(
            created_at__date__range=[date_from, date_to],
        )
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}
    if not grouped_data:
        return []

    first_date = min(grouped_data.keys())
    last_date = max(grouped_data.keys())

    result: list[DailyStatistics] = []
    current_date = first_date
    while current_date <= last_date:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_blog_article_views_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    exclude_views_q = Q(user__isnull=True) | Q(user__is_superuser=False)

    queryset = (
        BlogArticleView.objects.filter(viewed_at__date__range=[date_from, date_to])
        .filter(exclude_views_q)
        .annotate(group_date=TruncDate(trunc_fn('viewed_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    # В графике хотим всегда видеть весь диапазон (включая нули).
    result: list[DailyStatistics] = []
    current_date = date_from
    while current_date <= date_to:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def _collect_blog_articles_added_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)

    queryset = (
        BlogArticle.objects.filter(created_at__date__range=[date_from, date_to])
        .annotate(group_date=TruncDate(trunc_fn('created_at', tzinfo=timezone.utc)))
        .values('group_date')
        .annotate(count=Count('id'))
        .order_by('group_date')
    )

    grouped_data = {item['group_date']: item['count'] for item in queryset}

    result: list[DailyStatistics] = []
    current_date = date_from
    while current_date <= date_to:
        result.append(
            DailyStatistics(
                label=_format_group_label(current_date, group_by),
                count=grouped_data.get(current_date, 0),
            )
        )
        current_date = _next_group_date(current_date, group_by)

    return result


def build_blog_overview_period(now_date: date, days: int) -> tuple[date, date, date, date]:
    """
    Возвращает границы для:
    - текущего периода: [date_from, date_to] (включительно)
    - предыдущего периода: [previous_date_from, previous_date_to] (равной длины)
    """
    date_to = now_date
    date_from = date_to - timedelta(days=days - 1)
    previous_date_to = date_from - timedelta(days=1)
    previous_date_from = previous_date_to - timedelta(days=days - 1)
    return date_from, date_to, previous_date_from, previous_date_to


def collect_blog_last_added_articles_items(limit: int = 10) -> list[BlogArticleTableRow]:
    """Возвращает 10 последних добавленных статей с количеством просмотров."""
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
    """Возвращает 10 самых просматриваемых статей с количеством просмотров."""
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
    return BlogArticle.objects.filter(created_at__date__range=[date_from, date_to]).count()


def count_blog_article_views_in_range(date_from: date, date_to: date) -> int:
    exclude_views_view = Q(user__isnull=True) | Q(user__is_superuser=False)
    return (
        BlogArticleView.objects.filter(viewed_at__date__range=[date_from, date_to])
        .filter(exclude_views_view)
        .count()
    )


def build_period_comparison_stats(current_count: int, previous_count: int) -> PeriodComparisonStatistics:
    delta = current_count - previous_count
    delta_percent = 0.0 if previous_count == 0 else round((delta / previous_count) * 100, 2)
    return PeriodComparisonStatistics(
        current_count=current_count,
        previous_count=previous_count,
        delta=delta,
        delta_percent=delta_percent,
    )


def collect_blog_last_added_card_overview(now_date: date, days: int = 30) -> BlogArticlesCardOverview:
    """Карточка 'Последние добавленные статьи'."""
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)

    items = collect_blog_last_added_articles_items(limit=10)
    current_count = count_blog_articles_added_in_range(period_from, period_to)
    previous_count = count_blog_articles_added_in_range(prev_from, prev_to)

    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_blog_articles_added_by_group(date_from=period_from, date_to=period_to, group_by='day')

    return BlogArticlesCardOverview(items=items, comparison=comparison, chart=chart)


def collect_blog_top_viewed_card_overview(now_date: date, days: int = 60) -> BlogArticlesCardOverview:
    """Карточка 'Самые просматриваемые статьи'."""
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)

    items = collect_blog_top_viewed_articles_items(limit=10)
    current_count = count_blog_article_views_in_range(period_from, period_to)
    previous_count = count_blog_article_views_in_range(prev_from, prev_to)

    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_blog_article_views_by_group(date_from=period_from, date_to=period_to, group_by='day')

    return BlogArticlesCardOverview(items=items, comparison=comparison, chart=chart)

