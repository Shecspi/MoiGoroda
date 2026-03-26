"""
Статистика посещённых городов.
"""

from __future__ import annotations

from datetime import date

from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.db.models import OuterRef, Subquery
from django.db.models.functions.datetime import TruncDate

from city.models import VisitedCity
from dashboard.schemas import DailyStatistics, Quantity, TrendCardOverview, UserStatistics
from dashboard.statistics_helpers.common import (
    _format_group_label,
    _get_group_trunc_function,
    _next_group_date,
    build_blog_overview_period,
    build_period_comparison_stats,
    timezone,
)


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


def collect_total_visited_cities_visits() -> Quantity:
    return Quantity(count=VisitedCity.objects.count())


def collect_unique_visited_cities() -> Quantity:
    qty = (
        VisitedCity.objects.values('user')
        .annotate(unique_cities=Count('city', distinct=True))
        .aggregate(total=Sum('unique_cities'))
        .get('total', 0)
        or 0
    )

    return Quantity(count=qty)


def count_added_visited_cities_in_range(date_from: date, date_to: date) -> int:
    return VisitedCity.objects.filter(created_at__date__range=[date_from, date_to]).count()


def collect_added_visited_cities_trend_card_overview(
    now_date: date,
    days: int,
    group_by: str,
) -> TrendCardOverview:
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)
    current_count = count_added_visited_cities_in_range(period_from, period_to)
    previous_count = count_added_visited_cities_in_range(prev_from, prev_to)
    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_added_visited_cities_by_group(
        date_from=period_from,
        date_to=period_to,
        group_by=group_by,
    )

    return TrendCardOverview(comparison=comparison, chart=chart)


def collect_visited_cities_by_user_chart(limit: int = 50) -> list[UserStatistics]:
    queryset = (
        User.objects.annotate(
            qty_visited_cities=Subquery(
                VisitedCity.objects.filter(user=OuterRef('pk'))
                .values('user')
                .annotate(qty=Count('pk'))
                .values('qty')
            )
        )
        .values('username', 'qty_visited_cities')
        .exclude(qty_visited_cities=None)
        .order_by('-qty_visited_cities')[:limit]
    )
    result = [
        UserStatistics(label=item['username'], count=item['qty_visited_cities'])
        for item in queryset
    ]

    return list(reversed(result))


def collect_unique_visited_cities_by_user_chart(limit: int = 50) -> list[UserStatistics]:
    queryset = (
        User.objects.annotate(
            qty_unique_visited_cities=Subquery(
                VisitedCity.objects.filter(user=OuterRef('pk'))
                .values('user')
                .annotate(qty=Count('city', distinct=True))
                .values('qty')
            )
        )
        .values('username', 'qty_unique_visited_cities')
        .exclude(qty_unique_visited_cities=None)
        .order_by('-qty_unique_visited_cities')[:limit]
    )
    result = [
        UserStatistics(label=item['username'], count=item['qty_unique_visited_cities'])
        for item in queryset
    ]

    return list(reversed(result))


__all__ = [
    '_collect_added_visited_cities_by_group',
    'collect_total_visited_cities_visits',
    'collect_unique_visited_cities',
    'count_added_visited_cities_in_range',
    'collect_added_visited_cities_trend_card_overview',
    'collect_visited_cities_by_user_chart',
    'collect_unique_visited_cities_by_user_chart',
]
