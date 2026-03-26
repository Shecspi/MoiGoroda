"""
Статистика пользователей (регистрации).
"""

from __future__ import annotations

from datetime import date

from django.db.models import OuterRef, Subquery
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions.datetime import TruncDate

from city.models import VisitedCity
from dashboard.schemas import DailyStatistics, Quantity, TrendCardOverview
from dashboard.statistics_helpers.common import (
    _format_group_label,
    _get_group_trunc_function,
    _next_group_date,
    build_blog_overview_period,
    build_period_comparison_stats,
    timezone,
)


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


def collect_total_users() -> Quantity:
    return Quantity(count=User.objects.count())


def collect_number_of_users_without_visited_cities() -> Quantity:
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
        .filter(qty_visited_cities=None)
        .order_by('-qty_visited_cities')
    )

    return Quantity(count=queryset.count())


def count_registrations_in_range(date_from: date, date_to: date) -> int:
    return User.objects.filter(date_joined__date__range=[date_from, date_to]).count()


def collect_registrations_trend_card_overview(
    now_date: date,
    days: int,
    group_by: str,
) -> TrendCardOverview:
    period_from, period_to, prev_from, prev_to = build_blog_overview_period(now_date, days)
    current_count = count_registrations_in_range(period_from, period_to)
    previous_count = count_registrations_in_range(prev_from, prev_to)
    comparison = build_period_comparison_stats(current_count, previous_count)
    chart = _collect_registrations_by_group(
        date_from=period_from, date_to=period_to, group_by=group_by
    )
    return TrendCardOverview(comparison=comparison, chart=chart)


__all__ = [
    '_collect_registrations_by_group',
    'collect_total_users',
    'collect_number_of_users_without_visited_cities',
    'count_registrations_in_range',
    'collect_registrations_trend_card_overview',
]
