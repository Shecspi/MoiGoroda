"""
Статистика посещённых стран.
"""

from __future__ import annotations

from datetime import date

from django.db.models import Count
from django.db.models.functions.datetime import TruncDate

from country.models import VisitedCountry
from dashboard.schemas import DailyStatistics, Quantity, TrendCardOverview
from dashboard.statistics_helpers.common import (
    _format_group_label,
    _get_group_trunc_function,
    _next_group_date,
    build_blog_overview_period,
    build_datetime_range,
    build_period_comparison_stats,
    timezone,
)


def _collect_added_visited_countries_by_group(
    date_from: date,
    date_to: date,
    group_by: str,
) -> list[DailyStatistics]:
    trunc_fn = _get_group_trunc_function(group_by)
    dt_from, dt_to = build_datetime_range(date_from, date_to)
    queryset = (
        VisitedCountry.objects.filter(
            added_at__gte=dt_from,
            added_at__lt=dt_to,
        )
        .annotate(group_date=TruncDate(trunc_fn('added_at', tzinfo=timezone.utc)))
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


def collect_visited_countries_total() -> Quantity:
    return Quantity(count=VisitedCountry.objects.count())


def collect_users_with_visited_countries() -> Quantity:
    return Quantity(count=VisitedCountry.objects.values('user').distinct().count())


def count_added_visited_countries_in_range(date_from: date, date_to: date) -> int:
    dt_from, dt_to = build_datetime_range(date_from, date_to)
    return VisitedCountry.objects.filter(added_at__gte=dt_from, added_at__lt=dt_to).count()


def collect_added_visited_countries_trend_card_overview(
    now_date: date,
    days: int,
    group_by: str,
) -> TrendCardOverview:
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)
    current_count = count_added_visited_countries_in_range(period_from, period_to)
    previous_count = count_added_visited_countries_in_range(prev_from, prev_to)
    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_added_visited_countries_by_group(
        date_from=period_from,
        date_to=period_to,
        group_by=group_by,
    )
    return TrendCardOverview(comparison=comparison, chart=chart)


__all__ = [
    '_collect_added_visited_countries_by_group',
    'collect_visited_countries_total',
    'collect_users_with_visited_countries',
    'count_added_visited_countries_in_range',
    'collect_added_visited_countries_trend_card_overview',
]

